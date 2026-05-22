# Deep Research Findings — Round 2

## Summary

This round deepens the evidence base for the remaining blockers.

- A remains blocked for production Tables 5, 7, and 8. A real EPS/NBS / China City Statistical Yearbook export is still required.
- Public substitutes can support appendix-only historical capacity checks, but they cannot replace the 2019–2024 production city controls.
- B2 is solvable with continued source verification. This pass adds a larger set of usable external evidence leads for `external_verification_queue.csv`.

---

# A — City controls

## Production requirement remains unchanged

The repo contract requires a city-year panel with:

```text
city
province
year
gdp
gdp_per_capita
secondary_value_added
industrial_output
population
employment
average_wage
fdi
fixed_asset_investment
education_proxy
telecom_or_internet_proxy
foreign_trade
source_name
source_file
```

Target years:

```text
2019-2024
```

This cannot be reconstructed legitimately from the open national NBS yearbook alone.

## Public sources found

### NBS national yearbooks

URL:

```text
https://www.stats.gov.cn/sj/ndsj/index.html
```

Use:

```text
National/provincial background only. Not enough for city-level production controls.
```

Why insufficient:

```text
The online national yearbook index is open, but the relevant prefecture city controls are not exposed as a complete 2019-2024 city-year CSV with all required variables.
```

### China City Statistical Yearbook through EPS

URL:

```text
https://epschinastats.com/db_city.html
```

Use:

```text
Preferred production source.
```

Action:

```text
A human with institutional access should export EPS China City Statistics for all repo cities, 2019-2024.
```

### ETI / Figshare 282-city dataset

URL:

```text
https://figshare.com/articles/dataset/Energy_transition_index_for_282_Chinese_cities/24563590
```

Use:

```text
Appendix-only, pre-2019 city-capacity robustness.
```

Strength:

```text
Public, CC BY 4.0, 282 cities, 2003-2019.
```

Limitation:

```text
Does not cover 2024-2025 smart-factory adoption years; not a substitute for production Tables 5, 7, and 8.
```

### Scientific Data article for ETI

URL:

```text
https://www.nature.com/articles/s41597-023-02815-7
```

Use:

```text
Citation and data-description support for the ETI appendix if used.
```

Key detail:

```text
Reports 282 Chinese cities from 2003-2019 and public Figshare data records.
```

## Recommendation for A

Use the following decision rule.

### If EPS/NBS export is obtained

Run production controls and cite Tables 5, 7, and 8.

### If EPS/NBS export is not obtained

Do not cite Tables 5, 7, or 8 as controlled evidence. Add an appendix using ETI 2003-2019 only as a historical city-capacity proxy.

---

# B2 — External verification leads

## Evidence rule

A row is externally verified only if a real non-list URL supports plant/company/project location. Solarbe/JLTS list pages do not count.

## New usable leads from Round 2

| queue_rank | project_id | firm_name_zh | assigned_city | URL | evidence_type | assessment |
|---:|---|---|---|---|---|---|
| 24 | 2025_2025_excellence_batch_0131 | 中策橡胶集团股份有限公司 | Hangzhou | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12097929&stockid=603049 | company_annual_report | Annual report mirror lists registered and office address in 杭州钱塘区1号大街1号. Prefer SSE official PDF if found. |
| 25 | 2024_2024_first_batch_0142 | 武汉精测电子集团股份有限公司 | Wuhan | https://www.wuhanjingce.com/Contact/index.aspx | company_site_registry | Official company contact page lists address in 武汉市东湖新技术开发区流芳园南路22号. |
| 26 | 2024_2024_first_batch_0144 | 武汉京东方光电科技有限公司 | Wuhan | https://www.qichamao.com/orgcompany/searchitemdtl/ab8e60f5985a4681d742ba87130f694d.html | project_registry | Registry profile lists address 武汉市东西湖区临空港大道691号. Use only if third-party registry is accepted; prefer official/local-government source if found. |
| 27 | 2025_2025_excellence_batch_0199 | 烽火通信科技股份有限公司 | Wuhan | https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12181554&stockid=600498 | company_annual_report | Annual report mirror lists registered address 武汉市洪山区邮科院路88号 and office address 武汉市东湖新技术开发区高新四路6号. |
| 30 | 2025_2025_excellence_batch_0202 | 湖北三峰透平装备股份有限公司 | Wuhan | https://ru.sfturbo.com/contact-us | company_site_registry | Company contact page gives headquarters in Wuhan but production base in Guangshui. Do not use to verify Wuhan if project is a production factory without further evidence. Flag for review. |
| 31 | 2025_2025_excellence_batch_0206 | 武汉光迅科技股份有限公司 | Wuhan | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10945693&stockid=002281 | company_annual_report | Annual report mirror lists registered address 武汉东湖新技术开发区流苏南路1号 and office address 武汉江夏区藏龙岛开发区潭湖路1号. |
| 35 | 2024_2024_first_batch_0157 | 博世汽车部件（长沙）有限公司 | Changsha | https://www.bosch.com.cn/our-company/bosch-in-china/bosch-automotive-products-changsha/ | company_site_registry | Official Bosch China page lists 湖南省长沙市星沙漓湘中路26号 and describes Changsha operations. Strong evidence. |
| 36 | 2024_2024_first_batch_0160 | 三一集团有限公司 | Changsha | https://www.sanyglobal.com/cn/contact_us/ | company_site_registry | Official Sany contact page lists global headquarters at 湖南省长沙经济技术开发区三一工业城. Strong corporate-location evidence; project-specific factory match should be reviewed. |
| 32 | 2024_2024_first_batch_0153 | 蓝思科技（长沙）有限公司 | Changsha | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10818840 | company_annual_report | Annual report mirror lists registered/office address 湖南浏阳生物医药园 and defines 长沙蓝思 as subsidiary. Supports Changsha area; reviewer should ensure city mapping to Changsha/浏阳 accepted. |
| 45 | 2025_2025_excellence_batch_0212 | 威胜信息技术股份有限公司 | Changsha | https://www.willfar.com/ | company_site_registry | Official website lists address 中国湖南省长沙市国家高新技术产业开发区桐梓坡西路468号. Strong evidence. |
| 47 | 2025_2025_excellence_batch_0215 | 中国铁建重工集团股份有限公司 | Changsha | https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12007522&stockid=688425 | company_annual_report | Annual report mirror lists registered and office address 长沙经济技术开发区泉塘街道东七路88号. Strong evidence. |
| 46 | 2025_2025_excellence_batch_0213 | 盐津铺子食品股份有限公司 | Changsha | https://www.yanjinpuzi.com/contact.aspx | company_site_registry | Official contact page lists HQ and production base in 长沙/浏阳. Strong evidence. |
| 39 | 2024_2024_first_batch_0193 | 鸿富成精密电子（成都）有限公司 | Chengdu | https://www.qichamao.com/orgcompany/searchitemdtl/1f5545caec2aec6cb1d0a62fb88d0cf4.html | project_registry | Registry profile lists address 成都高新区合作路689号. Third-party registry; acceptable only if policy allows project_registry. |
| 49 | 2025_2025_excellence_batch_0246 | 鸿富锦精密电子（成都）有限公司 | Chengdu | https://www.zhipin.com/companys/1c82874fdc9124ca1nN70t64.html | project_registry | BOSS/Zhipin registry section lists registered address 四川省成都高新西区合作路888号. Third-party registry; use cautiously. |
| 40 | 2024_2024_first_batch_0194 | 川开电气有限公司 | Chengdu | https://ggzy.qingdao.gov.cn/PortalQDManage/ShareResources/CorpInfo?corpGuid=11c219be-a12d-4964-bcad-19d09df8117a | project_registry | Public procurement registry lists address 中国（四川）自由贸易试验区成都市双流区西南航空港经济开发区空港五路1888号. Strong registry evidence. |
| 23 | 2025_2025_excellence_batch_0129 | 浙江万向精工有限公司 | Hangzhou | https://www.zjwxpi.com/contact.html | company_site_registry | Official contact page lists 杭州萧山区经济技术开发区建设一路887号. Strong evidence. |
| 22 | 2025_2025_excellence_batch_0125 | 浙江大胜达包装股份有限公司 | Hangzhou | https://www.sdpack.cn/Contact | company_site_registry | Official contact page lists company address in 杭州市萧山区. Strong corporate-location evidence. Annual report also available via Sina mirror. |

## Combined B2 status

Round 1 produced roughly 14 usable leads. Round 2 adds roughly 17 additional leads, though several need caution because they are third-party registry pages or corporate-location rather than project-factory evidence.

Current practical status:

```text
~31 usable/high-confidence leads found across Rounds 1-2.
```

Remaining to reach 50:

```text
~19 additional externally verified rows.
```

## Recommended next B2 search sequence

Continue with queue rows 50 onward and prioritize official pages / annual reports.

Search patterns:

```text
"<firm_name_zh>" "联系我们"
"<firm_name_zh>" "地址"
"<firm_name_zh>" "年度报告"
"<firm_name_zh>" "生产基地"
"<firm_name_zh>" site:cninfo.com.cn
"<firm_name_zh>" site:sse.com.cn
"<firm_name_zh>" site:szse.cn
"<firm_name_zh>" site:<local gov domain>
```

## Stronger evidence hierarchy for B2

Use this order:

1. Project-specific local-government or industrial-park page.
2. Official company production-base/contact page naming the plant city.
3. Exchange/CNINFO annual report PDF naming registered/office/factory location.
4. Public procurement / official registry page.
5. Third-party registry page, only if no better source exists and clearly labeled.

## Paper note

When using company headquarters pages rather than plant-specific evidence, write:

```text
Externally verified corporate-location evidence, not necessarily project-specific plant-location evidence.
```

This avoids overstating the precision of B2.
