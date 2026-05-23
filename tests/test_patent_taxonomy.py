from __future__ import annotations

from diffusion_state.patent_taxonomy import classify_patent_text


def test_machine_vision_keyword_classification():
    cls = classify_patent_text(
        title="基于机器视觉的焊缝缺陷检测系统",
        abstract="图像检测与缺陷识别用于生产线质检",
    )
    assert cls.is_industrial_ai
    assert cls.categories["machine_vision"]
    assert cls.categories["quality_inspection"]


def test_surveillance_exclusion():
    cls = classify_patent_text(
        title="人脸识别安防系统",
        abstract="公安大数据与视频结构化",
    )
    assert cls.is_excluded_non_industrial
    assert not cls.is_industrial_ai
