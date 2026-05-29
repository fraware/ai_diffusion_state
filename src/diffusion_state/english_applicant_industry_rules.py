"""English applicant/title tokens -> coarse industry (IIDS export has no Chinese text)."""
from __future__ import annotations

# (token, industry_code, industry_label, confidence) — longest tokens first.
EN_INDUSTRY_RULES: tuple[tuple[str, str, str, str], ...] = tuple(
    sorted(
        [
            ("SEMICONDUCTOR MANUFACTURING", "C39_semi", "semiconductors", "high"),
            ("SEMICONDUCTOR", "C39_semi", "semiconductors", "high"),
            ("INTEGRATED CIRCUIT", "C39_semi", "semiconductors", "high"),
            ("MICROELECTRONICS", "C39_semi", "semiconductors", "high"),
            ("OPTOELECTRONICS", "C39", "electronics", "high"),
            ("OPTOELECTRONIC", "C39", "electronics", "high"),
            ("LIQUID CRYSTAL", "C39", "electronics", "high"),
            ("COMMUNICATIONS EQUIPMENT", "C39", "electronics", "high"),
            ("MOBILE COMMUNICATION", "C39", "electronics", "high"),
            ("ELECTRIC POWER", "C38", "electrical_machinery", "high"),
            ("POWER GRID", "C38", "electrical_machinery", "high"),
            ("STATE GRID", "C38", "electrical_machinery", "high"),
            ("PETROLEUM", "C26", "chemicals", "high"),
            ("PETROCHINA", "C26", "chemicals", "high"),
            ("SINOPEC", "C26", "chemicals", "high"),
            ("CHEMICAL", "C26", "chemicals", "medium"),
            ("PHARMACEUTICAL", "C27", "pharma", "high"),
            ("PHARMA", "C27", "pharma", "high"),
            ("RAILWAY", "C37", "railway_shipbuilding_aerospace", "high"),
            ("AEROSPACE", "C37", "railway_shipbuilding_aerospace", "high"),
            ("AIRCRAFT", "C37", "railway_shipbuilding_aerospace", "high"),
            ("AUTOMOBILE", "C36", "automotive", "high"),
            ("MOTOR", "C36", "automotive", "medium"),
            ("HUAWEI", "C39", "electronics", "high"),
            ("ZTE", "C39", "electronics", "high"),
            ("XIAOMI", "C39", "electronics", "high"),
            ("LENOVO", "C39", "electronics", "high"),
            ("BYTEDANCE", "C39", "electronics", "high"),
            ("BOE", "C39", "electronics", "high"),
            ("CSOT", "C39", "electronics", "high"),
            ("TCL", "C39", "electronics", "high"),
            ("MIDEA", "C38", "electrical_machinery", "high"),
            ("GREE ELECTRIC", "C38", "electrical_machinery", "high"),
            ("HAIER", "C38", "electrical_machinery", "high"),
            ("CATL", "C39_battery", "batteries", "high"),
            ("AMPEREX", "C39_battery", "batteries", "high"),
            ("BATTERY", "C39_battery", "batteries", "medium"),
            ("ROBOT", "C35", "special_equipment", "medium"),
            ("ROBOTICS", "C35", "special_equipment", "medium"),
            ("MACHINERY", "C34", "general_equipment", "medium"),
            ("STEEL", "C33", "metals", "high"),
            ("MINING", "C13", "mining", "high"),
            ("TEXTILE", "C17", "textiles", "high"),
            ("FOOD", "C14", "food", "medium"),
            ("AGRICULT", "C14", "food", "medium"),
            ("INSTRUMENT", "C40", "instruments", "high"),
            ("MEASURING", "C40", "instruments", "medium"),
            ("UNIV", "C40", "instruments", "medium"),
            ("INST ", "C40", "instruments", "medium"),
            ("HOSPITAL", "C27", "pharma", "medium"),
            ("BANK", "C34", "general_equipment", "low"),
            ("INSURANCE", "C34", "general_equipment", "low"),
        ],
        key=lambda x: len(x[0]),
        reverse=True,
    )
)


def match_english_industry(text_upper: str) -> tuple[str, str, str] | None:
    for token, code, label, conf in EN_INDUSTRY_RULES:
        if token in text_upper:
            return code, label, conf
    return None
