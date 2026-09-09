import logging
from typing import Callable, Dict

from .base_adapter import DatasetAdapter
from .officeqa_adapter import OfficeQAAdapter
from .finqa_adapter import FinQAAdapter
from .tatqa_adapter import TATQAAdapter
from .tabfact_adapter import TabFactAdapter
from .wtq_adapter import WikiTableQuestionsAdapter
from .fetaqa_adapter import FeTaQAAdapter
from .financebench_adapter import FinanceBenchAdapter
from .magellan_em_adapter import MagellanEMAdapter
from .wdc_products_adapter import WDCProductsAdapter
from .hitab_adapter import HiTabAdapter
from .docfinqa_adapter import DocFinQAAdapter
from .multihiertt_adapter import MultiHierttAdapter
from .tpcdi_cells_adapter import TPCDICellsAdapter
from .hf_generic_adapter import GenericDatasetAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """Registry factory: name -> adapter instance."""

    _registry: Dict[str, Callable[[], DatasetAdapter]] = {
        # tier 2: reasoning over tables / documents
        "officeqa": OfficeQAAdapter, "finqa": FinQAAdapter, "tat_qa": TATQAAdapter, "tatqa": TATQAAdapter,
        "tab_fact": TabFactAdapter, "tabfact": TabFactAdapter, "wikitablequestions": WikiTableQuestionsAdapter, "wtq": WikiTableQuestionsAdapter,
        "fetaqa": FeTaQAAdapter, "financebench": FinanceBenchAdapter, "hitab": HiTabAdapter, "docfinqa": DocFinQAAdapter,
        "multihiertt": MultiHierttAdapter,
        # tier 1: data matching proper
        "abt_buy": lambda: MagellanEMAdapter("abt_buy"), "amazon_google": lambda: MagellanEMAdapter("amazon_google"),
        "dblp_scholar": lambda: MagellanEMAdapter("dblp_scholar"), "walmart_amazon": lambda: MagellanEMAdapter("walmart_amazon"),
        "wdc_products": WDCProductsAdapter, "tpcdi_cells": TPCDICellsAdapter,
        "generic": GenericDatasetAdapter,
    }

    @classmethod
    def get_adapter(cls, dataset_name: str) -> DatasetAdapter:
        name = dataset_name.lower().strip()
        factory = cls._registry.get(name, GenericDatasetAdapter)
        return factory()

    @classmethod
    def register_adapter(cls, name: str, factory) -> None:
        cls._registry[name.lower().strip()] = factory

    @classmethod
    def names(cls):
        return sorted(cls._registry)
