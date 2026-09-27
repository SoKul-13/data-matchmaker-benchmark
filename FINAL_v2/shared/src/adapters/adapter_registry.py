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
from .mmtu_adapter import MMTUAdapter
from .realhitbench_adapter import RealHiTBenchAdapter
from .suc_adapter import SUCAdapter
from .tabis_adapter import TabISAdapter
from .tableeval_adapter import TableEvalAdapter
from .tablebench_adapter import TableBenchAdapter
from .bird_adapter import BIRDAdapter
from .officeqa_pro_v2_adapter import OfficeQAProV2Adapter
from .hf_generic_adapter import GenericDatasetAdapter
from .wdc_lspc_adapter import WDCLSPCAdapter
from .machamp_adapter import MachampAdapter
from .papadakis_dn_adapter import PapadakisDnAdapter
from .alaska_camera_adapter import AlaskaCameraAdapter
from .alaska_schema_adapter import AlaskaSchemaAdapter
from .valentine_adapter import ValentineAdapter
from .magneto_gdc_adapter import MagnetoGDCAdapter
from .smat_adapter import SMATAdapter
from .opensanctions_pairs_adapter import OpenSanctionsPairsAdapter
from .fintagging_adapter import FinTaggingAdapter
from .raw_cache import default_pool_n as _pool_n

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """Registry factory: name -> adapter instance."""

    _registry: Dict[str, Callable[[], DatasetAdapter]] = {
        # tier 2: reasoning over tables / documents
        "officeqa": OfficeQAAdapter, "finqa": FinQAAdapter, "tat_qa": TATQAAdapter, "tatqa": TATQAAdapter,
        "tab_fact": TabFactAdapter, "tabfact": TabFactAdapter, "wikitablequestions": WikiTableQuestionsAdapter, "wtq": WikiTableQuestionsAdapter,
        "fetaqa": FeTaQAAdapter, "financebench": FinanceBenchAdapter, "hitab": HiTabAdapter, "docfinqa": DocFinQAAdapter,
        "multihiertt": MultiHierttAdapter,
        # tier 2: v6 additions (table / document QA)
        "mmtu": MMTUAdapter, "realhitbench": RealHiTBenchAdapter, "suc": SUCAdapter, "tabis": TabISAdapter,
        "tableeval": TableEvalAdapter, "tablebench": TableBenchAdapter, "bird": BIRDAdapter, "officeqa_pro_v2": OfficeQAProV2Adapter,
        # tier 1: data matching proper
        "abt_buy": lambda: MagellanEMAdapter("abt_buy"), "amazon_google": lambda: MagellanEMAdapter("amazon_google"),
        "dblp_scholar": lambda: MagellanEMAdapter("dblp_scholar"), "walmart_amazon": lambda: MagellanEMAdapter("walmart_amazon"),
        "wdc_products": WDCProductsAdapter, "tpcdi_cells": TPCDICellsAdapter,
        # tier 1, extended suite: entity matching
        "dblp_acm": lambda: MagellanEMAdapter("dblp_acm", default_n=_pool_n("dblp_acm")),
        "wdc_lspc": WDCLSPCAdapter, "machamp": MachampAdapter,
        "papadakis_dn": PapadakisDnAdapter, "alaska_camera": AlaskaCameraAdapter,
        "opensanctions_pairs": OpenSanctionsPairsAdapter,
        # tier 1, extended suite: schema matching / concept linking
        "alaska_schema": AlaskaSchemaAdapter, "valentine": ValentineAdapter, "magneto_gdc": MagnetoGDCAdapter,
        "smat": SMATAdapter, "fintagging": FinTaggingAdapter,
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
