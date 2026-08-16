"""Backward-compatible re-exports for result table parsers."""

from dse_pollution_corr.etl.dse.parsers import PARSERS, parse_results_table
from dse_pollution_corr.etl.dse.parsers._shared import _compose_subject, _scheme_from_level
from dse_pollution_corr.etl.dse.parsers.category_a import parse_category_a_levels
from dse_pollution_corr.etl.dse.parsers.category_a_csd import parse_category_a_csd
from dse_pollution_corr.etl.dse.parsers.category_b import parse_category_b
from dse_pollution_corr.etl.dse.parsers.category_c import (
    parse_category_c_cefr,
    parse_category_c_grades,
    parse_category_c_topik,
)

__all__ = [
    "PARSERS",
    "parse_results_table",
    "_compose_subject",
    "_scheme_from_level",
    "parse_category_a_levels",
    "parse_category_a_csd",
    "parse_category_b",
    "parse_category_c_cefr",
    "parse_category_c_grades",
    "parse_category_c_topik",
]
