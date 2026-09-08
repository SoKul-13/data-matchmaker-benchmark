import logging
from typing import Dict, Type

from .base_adapter import DatasetAdapter
from .officeqa_adapter import OfficeQAAdapter
from .finqa_adapter import FinQAAdapter
from .tatqa_adapter import TATQAAdapter
from .tabfact_adapter import TabFactAdapter
from .hf_generic_adapter import GenericDatasetAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Registry factory for dataset adapters.
    """

    _registry: Dict[str, Type[DatasetAdapter]] = {
        "officeqa": OfficeQAAdapter,
        "finqa": FinQAAdapter,
        "tat_qa": TATQAAdapter,
        "tatqa": TATQAAdapter,
        "tab_fact": TabFactAdapter,
        "tabfact": TabFactAdapter,
        "generic": GenericDatasetAdapter,
        "convfinqa": GenericDatasetAdapter,
        "financebench": GenericDatasetAdapter,
        "wikitablequestions": GenericDatasetAdapter,
        "fetaqa": GenericDatasetAdapter,
        "mpdocvqa": GenericDatasetAdapter,
        "sec_qa": GenericDatasetAdapter,
    }

    @classmethod
    def get_adapter(cls, dataset_name: str) -> DatasetAdapter:
        name = dataset_name.lower().strip()
        adapter_cls = cls._registry.get(name, GenericDatasetAdapter)
        logger.info(f"Using adapter class '{adapter_cls.__name__}' for dataset '{name}'")
        return adapter_cls()

    @classmethod
    def register_adapter(cls, name: str, adapter_cls: Type[DatasetAdapter]) -> None:
        cls._registry[name.lower().strip()] = adapter_cls
        logger.info(f"Registered custom adapter for '{name}'")
