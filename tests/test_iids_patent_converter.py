from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geo_join import join_patent_geography
from diffusion_state.iids_patent_converter import (
    IidsConvertConfig,
    build_grant_year_index,
    convert_iids_sql_to_csv,
    iids_row_to_phase1,
)
from diffusion_state.iids_sql_parser import parse_insert_statement, split_sql_tuple_values
from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS
from diffusion_state.patent_raw_sources import is_real_export_filename
from diffusion_state.utils import PROJECT_ROOT

FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def test_is_real_export_filename_iids() -> None:
    assert is_real_export_filename("opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv")
    assert not is_real_export_filename("industrial_ai_patent_records.csv")


def test_split_sql_tuple_values_handles_json_and_null() -> None:
    values = split_sql_tuple_values(
        "'CN2018123456A','title text',NULL,'[\"SHARP KK\"]','[\"G06N3/08\"]',2018"
    )
    assert values[0] == "CN2018123456A"
    assert values[2] is None
    assert values[3] == '["SHARP KK"]'
    assert values[5] == 2018


def test_parse_insert_statement_multi_row() -> None:
    sql = (
        "INSERT INTO `base_patent_detail` (`pn`,`title`,`year`) VALUES "
        "('CN1','机器人系统',2019),('CN2','普通零件',2019);"
    )
    batch = parse_insert_statement(sql)
    assert batch is not None
    assert batch.table == "base_patent_detail"
    assert batch.columns == ("pn", "title", "year")
    assert len(batch.rows) == 2


def test_build_grant_year_index() -> None:
    grant = build_grant_year_index(FIXTURES / "iids_base_patent_law_status_sample.sql")
    assert grant["CN2018123456A"] == 2020
    assert grant["CN2019234567A"] == 2021


def test_convert_iids_sql_to_csv_filters_and_maps(tmp_path: Path) -> None:
    out = tmp_path / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
    config = IidsConvertConfig(
        detail_sql=FIXTURES / "iids_base_patent_detail_sample.sql",
        law_status_sql=FIXTURES / "iids_base_patent_law_status_sample.sql",
        output_csv=out,
        year_min=2018,
        year_max=2020,
        jurisdiction_cn_only=True,
        require_industrial_ai=True,
    )
    stats = convert_iids_sql_to_csv(config)
    assert stats.scanned_rows == 5
    assert stats.written_rows == 3
    df = pd.read_csv(out, encoding="utf-8-sig")
    assert list(df.columns) == PHASE1_COLUMNS
    assert set(df["patent_id"]) == {"CN2018123456A", "CN2019234567A", "CN2020345678A"}
    row = df[df["patent_id"] == "CN2018123456A"].iloc[0]
    assert row["grant_year"] == 2020
    assert "G06Q10/06" in row["ipc_or_cpc"]
    assert row["source"] == "opendatalab_iids"


def test_iids_row_to_phase1_mapping() -> None:
    row = {
        "pn": "CN2018123456A",
        "title": "智能制造排产优化系统",
        "abs": "摘要",
        "ap_or": '["苏州智造科技有限公司"]',
        "ipc": '["G06Q10/06"]',
        "cpc": '[]',
        "pn_date": '["2018-09-12"]',
        "ad": '["2018-03-15"]',
        "year": 2018,
    }
    phase1 = iids_row_to_phase1(row, grant_years={"CN2018123456A": 2020}, config=IidsConvertConfig(
        detail_sql=FIXTURES / "iids_base_patent_detail_sample.sql"
    ))
    assert phase1["application_year"] == "2018"
    assert phase1["publication_year"] == "2018"
    assert phase1["grant_year"] == "2020"
    assert phase1["applicant_name"] == "苏州智造科技有限公司"


def test_join_patent_geography(tmp_path: Path) -> None:
    iids_csv = tmp_path / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
    convert_iids_sql_to_csv(
        IidsConvertConfig(
            detail_sql=FIXTURES / "iids_base_patent_detail_sample.sql",
            law_status_sql=FIXTURES / "iids_base_patent_law_status_sample.sql",
            output_csv=iids_csv,
            year_min=2018,
            year_max=2020,
            require_industrial_ai=True,
        )
    )
    out = tmp_path / "joined.csv"
    _, stats = join_patent_geography(iids_csv, FIXTURES / "iids_geography_sample.csv", out)
    df = pd.read_csv(out, encoding="utf-8-sig")
    suzhou = df[df["patent_id"] == "CN2018123456A"].iloc[0]
    assert suzhou["applicant_city"] == "苏州市"
    assert suzhou["applicant_province"] == "江苏省"
    assert stats["rows_with_city"] == 2
