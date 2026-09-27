"""Dataset -> family mapping used for family-balanced pooling and leave-one-family-out.  Names are pool file stems."""
FAMILY = {
    # entity matching (record pair -> yes / no)
    "abt_buy": "EM", "amazon_google": "EM", "walmart_amazon": "EM", "dblp_scholar": "EM", "dblp_acm": "EM", "wdc_products": "EM",
    "wdc_lspc": "EM", "machamp": "EM", "papadakis_dn": "EM", "alaska_camera": "EM", "opensanctions_pairs": "EM",
    # schema matching / integration (column -> target column, cell-level join task)
    "valentine": "SM", "magneto_gdc": "SM", "smat": "SM", "alaska_schema": "SM", "fintagging": "SM", "tpcdi_cells": "SM",
    # table question answering / understanding
    "hitab": "TQA", "mmtu": "TQA", "wikitablequestions": "TQA", "realhitbench": "TQA", "suc": "TQA", "tabis": "TQA",
    "tableeval": "TQA", "bird": "TQA", "tab_fact": "TQA", "fetaqa": "TQA", "tablebench": "TQA",
    # financial documents
    "officeqa_pro_v2": "FIN", "tat_qa": "FIN", "officeqa": "FIN", "finqa": "FIN", "financebench": "FIN", "docfinqa": "FIN", "multihiertt": "FIN",
}
FAMILY_LABEL = {"EM": "entity matching", "SM": "schema matching / integration", "TQA": "table QA / understanding", "FIN": "financial documents"}


def family_of(name: str) -> str:
    return FAMILY.get(name, "OTHER")
