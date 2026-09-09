"""
Unified async generation across providers with usage accounting.

    spec = ModelSpec(name="gpt-4.1-mini", provider="openai", model_id="gpt-4.1-mini", ...)
    res  = await generate(spec, prompt, system_prompt, max_tokens=700)

`res` is a GenResult(text, in_tokens, out_tokens, latency_s, error).  Costs are
estimated from the price table in config/models.toml (USD per 1M tokens).
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

_clients: Dict[str, Any] = {}
_sems: Dict[str, asyncio.Semaphore] = {}


@dataclass
class ModelSpec:
    name: str
    provider: str
    model_id: str
    price_in: float = 3.0      # USD / 1M input tokens (conservative default)
    price_out: float = 15.0    # USD / 1M output tokens
    tier: str = "fast"
    reasoning: Optional[str] = None      # openai reasoning_effort
    thinking: Optional[str] = None       # gemini: "off" | "low" | None
    concurrency: int = 6
    extra: Dict[str, Any] = field(default_factory=dict)
    # ---- generic OpenAI-compatible endpoints (Groq, Together, Fireworks, OpenRouter, DeepSeek,
    #      Mistral, Cerebras, xAI, local vLLM / Ollama): provider = "openai_compat"
    base_url: Optional[str] = None       # literal URL or "$ENV_VAR" to read it from the environment
    api_key_env: Optional[str] = None    # env var holding the key ("" / "none" for keyless local servers)
    free_tier: bool = False              # documentation flag only
    enabled: bool = True                 # set false to keep a model in the catalogue but never run it
    note: str = ""

    def resolved_base_url(self) -> Optional[str]:
        if self.base_url and self.base_url.startswith("$"):
            return os.environ.get(self.base_url[1:], "").strip() or None
        return self.base_url

    def key_available(self) -> bool:
        """True if the credentials this model needs are present (used to auto-skip)."""
        if not self.enabled:
            return False
        env = {"openai": "OPENAI_API_KEY", "google": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(self.provider, self.api_key_env)
        if self.provider == "openai_compat":
            url = self.resolved_base_url() or ""
            if not url or "your" in url.lower() or "example" in url.lower():
                return False
        if env in (None, "", "none"):
            return True
        val = os.environ.get(env, "").strip()
        return bool(val) and "your" not in val.lower()


@dataclass
class GenResult:
    text: str
    in_tokens: int = 0
    out_tokens: int = 0
    latency_s: float = 0.0
    error: Optional[str] = None
    raw_finish: Optional[str] = None

    def cost_usd(self, spec: ModelSpec) -> float:
        return (self.in_tokens * spec.price_in + self.out_tokens * spec.price_out) / 1e6


def _sem(spec: ModelSpec) -> asyncio.Semaphore:
    if spec.name not in _sems:
        _sems[spec.name] = asyncio.Semaphore(spec.concurrency)
    return _sems[spec.name]


def _compat_client(spec: ModelSpec):
    key = (spec.name, spec.resolved_base_url())
    if key not in _clients:
        from openai import AsyncOpenAI
        api_key = os.environ.get(spec.api_key_env, "") if spec.api_key_env not in (None, "", "none") else "none"
        _clients[key] = AsyncOpenAI(base_url=spec.resolved_base_url(), api_key=api_key or "none", timeout=240.0, max_retries=0)
    return _clients[key]


async def _openai_compat(spec: ModelSpec, prompt: str, system: str, max_tokens: int) -> GenResult:
    client = _compat_client(spec)
    kwargs: Dict[str, Any] = dict(model=spec.model_id, max_tokens=max_tokens,
                                  messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}])
    kwargs.update(spec.extra.get("request", {}))
    resp = await client.chat.completions.create(**kwargs)
    choice = resp.choices[0]
    u = getattr(resp, "usage", None)
    text = choice.message.content or ""
    # some reasoning models return the answer in reasoning_content when content is empty
    if not text and getattr(choice.message, "reasoning_content", None):
        text = choice.message.reasoning_content
    return GenResult(text, getattr(u, "prompt_tokens", 0) or 0, getattr(u, "completion_tokens", 0) or 0, raw_finish=choice.finish_reason)


def _client(provider: str):
    if provider in _clients:
        return _clients[provider]
    if provider == "openai":
        from openai import AsyncOpenAI
        _clients[provider] = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=180.0, max_retries=0)
    elif provider == "google":
        from google import genai
        _clients[provider] = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    elif provider == "anthropic":
        from anthropic import AsyncAnthropic
        _clients[provider] = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=180.0, max_retries=0)
    else:
        raise ValueError(f"unknown provider {provider}")
    return _clients[provider]


async def _openai(spec: ModelSpec, prompt: str, system: str, max_tokens: int) -> GenResult:
    client = _client("openai")
    kwargs: Dict[str, Any] = dict(model=spec.model_id,
                                  messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}])
    mid = spec.model_id
    if mid.startswith(("gpt-5", "o1", "o3", "o4")):
        kwargs["max_completion_tokens"] = max_tokens
        if spec.reasoning:
            kwargs["reasoning_effort"] = spec.reasoning
    else:
        kwargs["max_tokens"] = max_tokens
    resp = await client.chat.completions.create(**kwargs)
    choice = resp.choices[0]
    u = resp.usage
    return GenResult(choice.message.content or "", u.prompt_tokens if u else 0, u.completion_tokens if u else 0,
                     raw_finish=choice.finish_reason)


async def _gemini(spec: ModelSpec, prompt: str, system: str, max_tokens: int) -> GenResult:
    from google.genai import types
    client = _client("google")
    cfg_kwargs: Dict[str, Any] = dict(system_instruction=system, max_output_tokens=max_tokens)
    if spec.thinking == "off":
        cfg_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    elif spec.thinking == "low":
        cfg_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level="low")
    try:
        resp = await client.aio.models.generate_content(model=spec.model_id, contents=prompt,
                                                        config=types.GenerateContentConfig(**cfg_kwargs))
    except Exception as e:  # thinking config unsupported -> retry without it
        if "thinking" in str(e).lower() and "thinking_config" in cfg_kwargs:
            cfg_kwargs.pop("thinking_config")
            resp = await client.aio.models.generate_content(model=spec.model_id, contents=prompt,
                                                            config=types.GenerateContentConfig(**cfg_kwargs))
        else:
            raise
    um = getattr(resp, "usage_metadata", None)
    in_t = getattr(um, "prompt_token_count", 0) or 0
    out_t = (getattr(um, "candidates_token_count", 0) or 0) + (getattr(um, "thoughts_token_count", 0) or 0)
    text = ""
    try:
        text = resp.text or ""
    except Exception:
        pass
    finish = None
    try:
        finish = str(resp.candidates[0].finish_reason)
    except Exception:
        pass
    return GenResult(text, in_t, out_t, raw_finish=finish)


async def _anthropic(spec: ModelSpec, prompt: str, system: str, max_tokens: int) -> GenResult:
    client = _client("anthropic")
    resp = await client.messages.create(model=spec.model_id, max_tokens=max_tokens, system=system,
                                        messages=[{"role": "user", "content": prompt}])
    text = "".join(getattr(b, "text", "") for b in resp.content)
    return GenResult(text, resp.usage.input_tokens, resp.usage.output_tokens, raw_finish=resp.stop_reason)


_IMPL = {"openai": _openai, "google": _gemini, "anthropic": _anthropic, "openai_compat": _openai_compat}


async def generate(spec: ModelSpec, prompt: str, system: str, max_tokens: int = 700,
                   retries: int = 6) -> GenResult:
    fn = _IMPL[spec.provider]
    last_err = None
    async with _sem(spec):
        for attempt in range(retries + 1):
            t0 = time.time()
            try:
                res = await fn(spec, prompt, system, max_tokens)
                res.latency_s = time.time() - t0
                return res
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {str(e)[:300]}"
                msg = str(e).lower()
                if "404" in msg and "not_found" in msg.replace(" ", "_"):
                    break  # model does not exist: do not retry
                if attempt < retries:
                    wait = 2.0 * (2 ** attempt)
                    if "rate" in msg or "429" in msg or "overloaded" in msg or "503" in msg or "resource_exhausted" in msg:
                        wait = 20.0 * (attempt + 1)
                    await asyncio.sleep(wait)
    return GenResult("", error=last_err)
