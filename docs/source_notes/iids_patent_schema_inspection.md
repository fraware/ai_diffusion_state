# IIDS patent schema inspection

Files directory: `C:\Users\mateo\ai_diffusion_state\data\raw\patents\opendatalab_iids_sources`

## Download status

- `base_patent_detail.sql` present locally: `False`
- `base_patent_law_status.sql` present locally: `False`
- OpenXLab reports `base_patent_detail.sql` at ~135 GB; full local download is impractical on this machine.
- Schema below is taken from the IIDS technical document (Table 5 / Table 6) when SQL files are absent.

## base_patent_detail documented fields

| field | type | description |
| --- | --- | --- |
| `pn` | `varchar` | Publication (announcement) number |
| `title` | `text` | Patent title |
| `abs` | `text` | Abstract |
| `pr` | `json` | Priority number(s) |
| `ap_or` | `json` | Applicant name(s) |
| `in_or` | `json` | Inventor / designer name(s) |
| `ipc` | `json` | IPC classification codes |
| `cpc` | `json` | CPC classification codes |
| `pn_date` | `json` | Publication (announcement) date(s) |
| `ad` | `json` | Filing / application date(s) |
| `family_number` | `varchar` | Patent family number |
| `year` | `int` | Application year |

## base_patent_law_status documented fields

| field | type | description |
| --- | --- | --- |
| `pn` | `varchar` | Patent number (join key to base_patent_detail) |
| `event_date` | `varchar` | Legal status event date |
| `authorize` | `int` | Grant effective flag |
| `reject` | `int` | Rejected / abandoned flag |
| `event_code` | `varchar` | Legal status code |
| `code_expl` | `varchar` | Legal status description |
| `transfer` | `int` | Assignment / transfer flag |
| `invalid` | `int` | Terminated / expired flag |

## Atlas Phase-1 field coverage

| atlas_field | coverage | iids_field | notes |
| --- | --- | --- | --- |
| `patent_id` | **partial** | `pn` | Publication number, not CN application number |
| `application_year` | **yes** | `year` | Direct int field |
| `publication_year` | **partial** | `pn_date` | Derive year from JSON publication date |
| `grant_year` | **partial** | `base_patent_law_status` | Join on pn; derive from authorize=1 event_date |
| `applicant_name` | **partial** | `ap_or` | JSON list of applicant names only |
| `applicant_address` | **no** | `` | Not documented in base_patent_detail |
| `applicant_province` | **no** | `` | Not documented in base_patent_detail |
| `applicant_city` | **no** | `` | Not documented in base_patent_detail |
| `patent_title` | **yes** | `title` | Direct text field |
| `abstract` | **yes** | `abs` | Direct text field |
| `claims_or_description` | **no** | `` | Claims not documented; abstract only |
| `ipc_or_cpc` | **yes** | `ipc;cpc` | Both JSON fields available |
| `patent_type` | **no** | `` | No patent-kind / type field documented |

## Summary

- Direct coverage: `4` fields
- Partial / join-derived coverage: `4` fields
- Missing from documented IIDS patent schema: `5` fields
- Location/address hint detected: `True`
- Title/abstract/claims hint detected: `True`
- IPC/CPC/classification hint detected: `True`

## Verdict

`base_patent_detail` is **not sufficient alone** for Atlas evidence ingest because applicant city,
province, and address are not documented. A converter can still produce a partial export for
AI patent classification and year/title/abstract/IPC work, but Atlas `patent_layer_ready` will
remain blocked until applicant geography is joined from another source or confirmed in the SQL dump.

Next: build a streaming SQL→CSV converter that reads only required columns and filters by year/IPC,
then map to `data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv`.