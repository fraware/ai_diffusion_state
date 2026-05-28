from pathlib import Path

p = Path("/root/ai_diffusion_state/src/diffusion_state/iids_patent_converter.py")
s = p.read_text(encoding="utf-8")

# Correct target table.
s = s.replace(
    'DETAIL_TABLE = "base_china_epo_ipc"',
    'DETAIL_TABLE = "base_patent_detail"',
)
s = s.replace(
    'DETAIL_TABLE = "base_patent_detail"',
    'DETAIL_TABLE = "base_patent_detail"',
)

# Replace detail columns with the true 13-field layout.
start = s.index("DOCUMENTED_DETAIL_COLUMNS = (")
end = s.index("\n\nINDUSTRIAL_AI_IPC_PREFIXES", start)

new_cols = '''DOCUMENTED_DETAIL_COLUMNS = (
    "row_id",
    "pn",
    "title",
    "abs",
    "pr",
    "ap_or",
    "in_or",
    "ipc",
    "cpc",
    "pn_date",
    "ad",
    "family_number",
    "year",
)'''

s = s[:start] + new_cols + s[end:]

# Safety fix if typo exists.
s = s.replace(
    "config.jurisdiction_cn_onlyand not",
    "config.jurisdiction_cn_only and not",
)

p.write_text(s, encoding="utf-8")
print("Patched converter: base_patent_detail + 13-field row_id layout.")
