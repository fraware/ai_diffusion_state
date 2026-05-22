# Deep Research Findings — Workstream A and B2

## Bottom line

A cannot be solved with a fully legitimate public substitute unless the paper downgrades or changes the city-control design. EPS or a manually exported NBS/China City Statistical Yearbook panel is still required for production Tables 5, 7, and 8.

B2 can be solved by source verification. Public web research found several high-quality external URLs for top-priority queue rows, but the full 50-row threshold still requires manual source collection or continued web verification.

---

# A — Real city controls

## Required production source

The production requirement remains:

```text
data/raw/city_controls/eps_china_city_stats_2019_2024.csv
```

or an equivalent NBS / China City Statistical Yearbook export covering the contract fields.

Required columns:

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

## What public research found

### 1. NBS national statistical yearbooks are open but not sufficient

NBS publishes national statistical yearbooks online for 1999–2025. These are useful for national/provincial context but do not provide the full prefecture-level city-control panel required by the repo contract.

Source:

```text
https://www.stats.gov.cn/sj/ndsj/index.html
```

Use:

```text
Background / macro context only, not production city controls.
```

### 2. China City Statistical Yearbook is the correct underlying source, but not easily open as structured city-year CSV

Many academic papers source prefecture-level city controls from China City Statistical Yearbook. The repo needs this kind of export. EPS China City Statistics is the practical route because it provides cleaned city-year tables.

Source:

```text
https://epschinastats.com/db_city.html
```

Use:

```text
Production city controls if the team has institutional access.
```

### 3. City-level ETI dataset is useful but not a production substitute

The Scientific Data ETI dataset covers 282 Chinese cities from 2003–2019 and is public through Figshare. It is based partly on China City Statistical Yearbook and official data. It can support background, robustness, or pre-2019 capacity checks, but it cannot produce 2024–2025 controlled adoption models.

Source:

```text
https://doi.org/10.6084/m9.figshare.24563590.v1
```

Use:

```text
Optional pre-2019 city capacity control / appendix robustness, not Tables 5–8 production controls.
```

### 4. CEADs / Scientific Data socioeconomic inventory is useful but one-year and limited

The Scientific Data emissions-socioeconomic inventory provides 2010 socioeconomic data for 182 Chinese cities, including population, GDP, GDP structure, and industrial output. It cannot support 2019–2024 production controls.

Source:

```text
https://www.nature.com/articles/sdata201927
https://www.ceads.net/data/
```

Use:

```text
Historical validation / city-capacity proxy only.
```

## Recommendation for A

Use one of these two paths:

### Preferred path

Export EPS China City Statistics for 2019–2024 with all required fields and place it locally in:

```text
data/raw/city_controls/eps_china_city_stats_2019_2024.csv
```

### If EPS access is unavailable

Create a narrower public-controls version and downgrade the paper claim:

```text
Tables 5, 7, and 8 remain blocked. The paper reports baseline/hub-exclusion descriptive evidence only.
```

Do not try to fabricate a production file from ETI/CEADs/NBS national yearbooks.

---

# B2 — External verification research leads

## Rule

A row is externally verified only if it has a non-list URL proving plant, project, registered, or operating location. Solarbe and JLTS list URLs do not count.

## Verified or high-confidence candidate rows

These are suitable for filling `external_verification_queue.csv` after human review.

| priority_rank | project_id | firm_name_zh | assigned_city | external_evidence_url | external_evidence_type | note |
|---:|---|---|---|---|---|---|
| 1 | 2025_2025_excellence_batch_0128 | 浙江双环传动机械股份有限公司 | Hangzhou | https://www.gearsnet.com/ | company_site_registry | Official company site lists Hangzhou management headquarters at 杭州市余杭区五常街道荆长路658-1号. This supports Hangzhou corporate location, but production-base match should be reviewed because production bases are also in 玉环、嘉兴、淮安、大连、重庆. |
| 2 | 2024_2024_first_batch_0141 | 长飞光纤光缆股份有限公司 | Wuhan | https://www.yofc.com/list/244.html | company_site_registry | Official contact page gives 中国武汉光谷大道9号. |
| 3 | 2024_2024_first_batch_0143 | 武昌船舶重工集团有限公司 | Wuhan | https://www.hbjmrh.gov.cn/wcm.files/upload/CMShbgb/202503/202503280502045.pdf | project_registry | Hubei shipbuilding administrative filing lists registration and production address in 武汉市新洲区. |
| 4 | 2024_2024_first_batch_0207 | 中国航空工业集团公司西安飞行自动控制研究所 | Xi'an | https://chinabidding.mofcom.gov.cn/bidDetail/bidding/bulletin/202309/ff808081870df1e9018adab9554103de.html | project_registry | Bidding notice gives招标人 address 陕西省西安市高新区锦业路129号. |
| 6 | 2025_2025_excellence_batch_0209 | 湖南吉利汽车部件有限公司 | Changsha | https://pdf.dfcfw.com/pdf/H2_AN202604091821099110_1.pdf?1775765281000.pdf= | company_annual_report | Filing/response document lists 湖南吉利汽车部件有限公司 warehouse/customer address in Hunan; reviewer should confirm whether 湘潭 vs Changsha affects assigned city. |
| 11 | 2025_2025_excellence_batch_0144 | 长鑫存储技术有限公司 | Hefei | https://www.maigoo.com/company/142050.html | project_registry | Company profile lists address 安徽省合肥市经济技术开发区启德路799号 and official website. Prefer official CXMT page if found. |
| 12 | 2024_2024_first_batch_0173 | 因湃电池科技有限公司 | Guangzhou | https://sthjj.gz.gov.cn/attachment/7/7866/7866285/9762178.pdf | project_registry | Guangzhou environmental document states project location at 广州市番禺区龙泽路239号 and describes factory project. |
| 13 | 2024_2024_first_batch_0065 | 江苏亨通光电股份有限公司 | Suzhou | https://www.htgd.com.cn/web/bocupload/2025/05/13/17471109699878v8taz.pdf | company_annual_report | 2024 annual report lists registered address in 吴江区七都镇 and office address in 苏州市吴江区. |
| 17 | 2024_2024_first_batch_0091 | 浙江大华技术股份有限公司 | Hangzhou | https://disc.static.szse.cn/disc/disk03/finalpage/2025-03-28/2c81e63a-b564-4298-bdac-913698e0213b.PDF | company_annual_report | 2024 annual report lists registered and headquarters addresses in 杭州滨江区. |
| 18 | 2024_2024_first_batch_0092 | 中控技术股份有限公司 | Hangzhou | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=9949281 | company_annual_report | Annual-report mirror lists registered and office address 浙江省杭州市滨江区六和路309号. Prefer SSE/official annual report PDF if found. |
| 19 | 2025_2025_excellence_batch_0109 | 顾家家居股份有限公司 | Hangzhou | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=11039301&stockid=603816 | company_annual_report | 2024 annual report mirror lists registered address 杭州经济技术开发区11号大街113号 and office address 杭州上城区东宁路599号. |
| 21 | 2025_2025_excellence_batch_0124 | 浙江传化化学品有限公司 | Hangzhou | https://www.transfarchem.com/index.php/newsinfo/index/439.html | industrial_park_page | Company/news EIA disclosure states project/company location in 杭州钱塘区临江工业园/临江高新技术产业园. |
| 22 | 2025_2025_excellence_batch_0125 | 浙江大胜达包装股份有限公司 | Hangzhou | https://static.cninfo.com.cn/finalpage/2025-04-22/1223197178.PDF | company_annual_report | 2024 annual report lists headquarters address 浙江省杭州市萧山区萧山经济技术开发区红垦农场垦瑞路518号. |
| 23 | 2025_2025_excellence_batch_0129 | 浙江万向精工有限公司 | Hangzhou | https://www.zjwxpi.com/contact.html | company_site_registry | Official company contact page lists 杭州萧山区经济技术开发区建设一路887号. |
| 24 | 2025_2025_excellence_batch_0131 | 中策橡胶集团股份有限公司 | Hangzhou | TBD | company_annual_report | Need official annual report/company page. Not yet verified in this research pass. |
| 25 | 2024_2024_first_batch_0142 | 武汉精测电子集团股份有限公司 | Wuhan | TBD | company_annual_report | Need official annual report/company page. |
| 26 | 2024_2024_first_batch_0144 | 武汉京东方光电科技有限公司 | Wuhan | TBD | project_registry | Need BOE or local-government source naming Wuhan facility. |

## Suggested B2 execution

1. Fill the verified URLs above into `data/interim/external_verification_queue.csv` only after a human reviewer confirms each row.
2. Continue with rows 24–50 using the same search pattern:

```text
"<firm_name_zh>" "地址"
"<firm_name_zh>" "年度报告"
"<firm_name_zh>" "生产基地"
"<firm_name_zh>" site:cninfo.com.cn
"<firm_name_zh>" site:sse.com.cn
"<firm_name_zh>" site:szse.cn
```

3. For listed companies, prefer exchange/CNINFO annual report PDFs over third-party mirrors.
4. For subsidiaries and factories, prefer local-government environmental, bidding, or industrial-park documents that name the project address.

## B2 current state after research

High-confidence or usable leads found in this pass:

```text
14 rows
```

Remaining to reach target:

```text
36 rows
```

Do not run `make apply-geo-updates` expecting B2 to pass until at least 50 rows have valid non-list URLs.
