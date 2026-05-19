# AI pilot zones — source notes

## Purpose

City- and county-level treatment table for **National New Generation AI Innovation and Development Pilot Zones** (国家新一代人工智能创新发展试验区).

## Canonical output

- `data/processed/pilot_zones.csv` (built by `make seed` from `data/seed/pilot_zones_seed.csv`)

## Sources

### 1. CSET / MOST initial 11 zones

| Field | Value |
|---|---|
| Source ID | `ai_pilot_zones_cset` |
| Type | academic (CSET synthesis of official MOST designations) |
| URL | https://cset.georgetown.edu/publication/china-creates-national-new-generation-artificial-intelligence-innovation-and-development-pilot-zones/ |
| Coverage | Beijing, Shanghai, Hangzhou, Hefei, Shenzhen, Tianjin, Deqing County, Chengdu, Chongqing, Jinan, Xi'an |
| Dates | Creation and announcement dates where reported |
| Limitation | English-language secondary source; verify against MOST notices for publication |

### 2. December 2021 seventeen-zone list

| Field | Value |
|---|---|
| Source ID | `ai_pilot_zones_xinhua_17` |
| Type | official (news report of national list) |
| URL | https://www.news.cn/2021-12/06/c_1128137133.htm |
| Mirror used in seed | https://www.jjckb.cn/2021-12/09/c_1310360145.htm |
| Coverage | Adds Guangzhou, Wuhan (2020 announcements) and Suzhou, Changsha, Zhengzhou, Shenyang (2021 list) |
| Limitation | Some rows lack exact designation dates in seed; flagged as `inferred_year` |

## Treatment definition

- **Unit**: one row per pilot unit (`pilot_unit_id`), normalized to `city` (Deqing County → `Deqing`, `admin_level=county`).
- **Treatment timing**: `pilot_year` is the first year the unit appears in the national pilot-zone program.
- **Date quality**: `exact_date` when both creation and announcement dates exist in seed; `exact_year` when only partial dates exist; `inferred_year` when only list membership is verified.

## Known mapping issues

1. **Deqing County** is county-level, not prefecture-level; merges to city panels require explicit mapping to Huzhou or county-level controls.
2. **Guangzhou** and **Wuhan** appear in the 17-zone list with announcement dates but without CSET creation dates.
3. **Suzhou, Changsha, Zhengzhou** lack announcement dates in the current seed; `pilot_year=2021` follows the December 2021 national list.

## Reproducibility

```bash
make seed    # writes data/processed/pilot_zones.csv
make test    # validates 17 rows, schema, and known pilot years
```

Manual corrections belong in `data/seed/pilot_zones_seed.csv`, not in generated output.
