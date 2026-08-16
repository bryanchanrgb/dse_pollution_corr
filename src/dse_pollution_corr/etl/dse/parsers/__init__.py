"""Route classified Table 5 schemas to parsers."""

from __future__ import annotations

from dse_pollution_corr.etl.dse.classify import (
    SCHEMA_CATEGORY_A_CSD,
    SCHEMA_CATEGORY_A_LEVELS,
    SCHEMA_CATEGORY_B_CHINESE,
    SCHEMA_CATEGORY_B_STANDARD,
    SCHEMA_CATEGORY_C_CEFR,
    SCHEMA_CATEGORY_C_GRADES,
    SCHEMA_CATEGORY_C_TOPIK,
)
from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.parsers.category_a import parse_category_a_levels
from dse_pollution_corr.etl.dse.parsers.category_a_csd import parse_category_a_csd
from dse_pollution_corr.etl.dse.parsers.category_b import parse_category_b
from dse_pollution_corr.etl.dse.parsers.category_c import (
    parse_category_c_cefr,
    parse_category_c_grades,
    parse_category_c_topik,
)

PARSERS = {
    SCHEMA_CATEGORY_A_LEVELS: parse_category_a_levels,
    SCHEMA_CATEGORY_A_CSD: parse_category_a_csd,
    SCHEMA_CATEGORY_B_STANDARD: lambda doc, page, table: parse_category_b(
        doc, page, table, SCHEMA_CATEGORY_B_STANDARD
    ),
    SCHEMA_CATEGORY_B_CHINESE: lambda doc, page, table: parse_category_b(
        doc, page, table, SCHEMA_CATEGORY_B_CHINESE
    ),
    SCHEMA_CATEGORY_C_GRADES: parse_category_c_grades,
    SCHEMA_CATEGORY_C_CEFR: parse_category_c_cefr,
    SCHEMA_CATEGORY_C_TOPIK: parse_category_c_topik,
}


def parse_results_table(
    doc: RawDocument, page: RawPage, table: RawTable, schema: str
) -> list[dict]:
    parser = PARSERS.get(schema)
    if parser is None:
        return []
    return parser(doc, page, table)

