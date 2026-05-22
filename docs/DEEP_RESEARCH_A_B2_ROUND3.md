# Deep Research Findings — Round 3

## Summary

This round focused on closing the remaining B2 external-verification gap and reassessing whether A can be solved without EPS/NBS.

Conclusion:

- A remains blocked for production controls. Public alternatives are usable only for appendix or historical capacity checks.
- B2 is now close to solvable. Across the three research rounds, we have enough candidate leads to approach or exceed 50 rows, but several must be reviewed because they are corporate-location evidence rather than project-specific factory-location evidence.

---

# A — City controls

## Production controls still require EPS/NBS / China City Statistical Yearbook export

The required 2019–2024 prefecture-level city panel still cannot be reconstructed cleanly from fully open public web sources.

Public sources found:

1. NBS national yearbook index

```text
https://www.stats.gov.cn/sj/ndsj/index.html
```

This is open and official, but it is not a complete city-level production control panel.

2. ETI / Figshare dataset for 282 Chinese cities, 2003–2019

```text
https://figshare.com/articles/dataset/Energy_transition_index_for_282_Chinese_cities/24563590
```

Useful only as an appendix historical-capacity proxy.

3. Scientific Data ETI article

```text
https://www.nature.com/articles/s41597-023-02815-7
```

The article documents that the ETI dataset covers 282 Chinese cities from 2003–2019 and uses China City Statistical Yearbook among its sources. It does not cover 2024–2025 adoption years.

## Decision

Do not use ETI/NBS national yearbooks as production Tables 5, 7, or 8 controls.

If EPS/NBS access is unavailable, make the paper a strong measurement/descriptive/hub-architecture paper and leave controlled adoption models blocked.

---

# B2 — Additional external verification leads

## New leads from Round 3

| queue_rank | project_id | firm_name_zh | assigned_city | URL | evidence_type | assessment |
|---:|---|---|---|---|---|---|
| 1 | 2025_2025_excellence_batch_0128 | 浙江双环传动机械股份有限公司 | Hangzhou | https://www.gearsnet.com/about.html | company_site_registry | Official company page lists Hangzhou management headquarters at 浙江省杭州市余杭区五常街道荆长路658-1号. Strong corporate-location evidence; annual report notes registered address in 玉环, so treat as corporate-location not factory-specific unless project evidence is found. |
| 28 | 2025_2025_excellence_batch_0200 | 湖北达能食品饮料有限公司 | Wuhan | https://www.foodsc.net/sc/24418.html | project_registry | Food production-license page lists residence and production address 武汉市东西湖区走马岭食品一路12号. Strong production-location evidence, though third-party mirrors regulatory data. |
| 30 | 2025_2025_excellence_batch_0202 | 湖北三峰透平装备股份有限公司 | Wuhan / Guangshui caution | https://ru.sfturbo.com/contact-us | company_site_registry | Company contact page lists HQ in Wuhan but production base in Guangshui, Hubei. This should be marked caution and may require correcting assigned_city if the smart factory refers to production base. |
| 33 | 2024_2024_first_batch_0154 | 山河智能装备股份有限公司 | Changsha | https://www.sunward.com.cn/lxwm/ | company_site_registry | Official contact page lists address 湖南省长沙县星沙产业基地凉塘东路1335号山河工业城. Strong evidence. |
| 34 | 2024_2024_first_batch_0156 | 中联重科股份有限公司 | Changsha | https://www.zoomlion.com/about/contact.html | company_site_registry | Official contact page lists address 湖南省长沙市银盆南路361号 and branch addresses in Changsha. Good corporate-location evidence; project-specific excavator factory may require branch/factory mapping. |
| 37 | 2024_2024_first_batch_0161 | 湖南星邦智能装备股份有限公司 | Changsha | https://www.sinoboom.com.cn/contact/index.html | company_site_registry | Official contact page lists 湖南省长沙市宁乡高新技术产业园区金洲大道东128号. Strong evidence. |
| 38 | 2024_2024_first_batch_0192 | 成都飞机工业（集团）有限责任公司 | Chengdu | https://sthjt.sc.gov.cn/sthjt/c103939/2024/11/21/57259a70cb244a7886b0684f5edde362/files/%E7%8E%AF%E5%A2%83%E5%BD%B1%E5%93%8D%E6%8A%A5%E5%91%8A%E8%A1%A8%EF%BC%88%E5%85%AC%E7%A4%BA%E6%9C%AC%EF%BC%89-20241121155735492.pdf | project_registry | Sichuan environmental-impact report lists registration and project construction location in 成都市青羊区黄田坝纬一路88号. Strong project-location evidence. |
| 41 | 2024_2024_first_batch_0197 | 通威太阳能（成都）有限公司 | Chengdu | https://cell.tongwei.cn/ | company_site_registry | Official Tongwei Solar page states Chengdu company is located in 成都市双流区 and describes high-efficiency cell production lines. Strong production-location evidence. |
| 42 | 2024_2024_first_batch_0204 | 中航西安飞机工业集团股份有限公司 | Xi'an | https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10838171&stockid=000768 | company_annual_report | 2024 annual report mirror lists registered and office address 陕西省西安市阎良区西飞大道一号. Good evidence; prefer SZSE/CNINFO PDF if available. |
| 43 | 2024_2024_first_batch_0206 | 西安法士特高智新科技有限公司 | Xi'an | https://top.qcc.com/tc/e91c5e348084.html | project_registry | Registry page lists 西安法士特高智新科技有限公司 address 陕西省西安市高新区经三十六路与纬三十路交汇处东南角. Third-party registry; use cautiously. |
| 44 | 2024_2024_first_batch_0208 | 陕西汉德车桥有限公司 | Xi'an | https://www.hdcq.com/about/contact_us.htm | company_site_registry | Official Hande contact page lists 陕西省西安经济技术开发区泾渭工业园16号. Strong evidence. |
| 45 | 2025_2025_excellence_batch_0212 | 威胜信息技术股份有限公司 | Changsha | https://www.willfar.com/ | company_site_registry | Official page lists address 中国湖南省长沙市国家高新技术产业开发区桐梓坡西路468号. Strong evidence. |
| 46 | 2025_2025_excellence_batch_0213 | 盐津铺子食品股份有限公司 | Changsha / Liuyang | https://www.yanjinpuzi.com/contact.aspx | company_site_registry | Official contact page lists administrative HQ in Changsha and headquarters base in Liuyang, Hunan. Treat as Changsha-area evidence, with Liuyang note. |
| 47 | 2025_2025_excellence_batch_0215 | 中国铁建重工集团股份有限公司 | Changsha | https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12007522&stockid=688425 | company_annual_report | Annual report mirror lists registered and office address 长沙经济技术开发区泉塘街道东七路88号. Strong evidence; prefer SSE official PDF if available. |
| 48 | 2025_2025_excellence_batch_0244 | 成都蓉生药业有限责任公司 | Chengdu | https://pharm.ncmi.cn/zysjk/ypscqyk/202312/t20231205_389812.html | project_registry | Pharmaceutical production-license page lists multiple Chengdu production addresses, including 高新区科园南路7号 and 双流区菁园路280号. Strong production-location evidence. |
| 49 | 2025_2025_excellence_batch_0246 | 鸿富锦精密电子（成都）有限公司 | Chengdu | https://www.zhipin.com/companys/1c82874fdc9124ca1nN70t64.html | project_registry | BOSS/Zhipin registry section lists registered address 四川省成都高新西区合作路888号. Third-party registry; use cautiously. |
| 50 | 2025_2025_excellence_batch_0252 | 中国核动力研究设计院 | Chengdu / Sichuan caution | TBD | project_registry | Not solved in this pass. Search results suggest some nuclear power institute activity may be outside Chengdu; do not verify without specific source. |
| official | 2025_2025_excellence_batch_0002 | 北京奔驰汽车有限公司 | Beijing | https://lei.bloomberg.com/leis/view/300300GNDDB55UGZ3O28 | project_registry | LEI record lists legal and HQ address 北京市北京经济技术开发区博兴路8号. Good external legal-address evidence. |
| official | 2025_2025_excellence_batch_0015 | 天津市特变电工变压器有限公司 | Tianjin | https://c.gongkong.com/PhoneVersion/companyInfo?cid=19194 | project_registry | Company profile lists address 天津市南开区黄河道南泥湾路3号北院. Use as third-party company registry. |

## Practical B2 status after Round 3

Approximate usable leads across three rounds:

```text
45-48 rows depending on whether third-party registries and corporate-location evidence are accepted.
```

Remaining high-quality project-specific gap:

```text
At least 2-5 rows should still be verified using official project/annual-report/company pages before claiming >=50 robust external verifications.
```

## Recommendation

1. Fill only the strongest official/company/annual-report/project-registry leads into `external_verification_queue.csv`.
2. For third-party registry entries, set `audit_notes` to:

```text
Third-party registry evidence; acceptable as external legal-location evidence but not project-specific factory evidence.
```

3. For corporate-location evidence, set `audit_notes` to:

```text
Corporate-location evidence; not necessarily project-specific plant-location evidence.
```

4. Exclude uncertain rows such as 中国核动力研究设计院 until a specific Chengdu-linked source is found.

## Next command after queue is filled

```powershell
make apply-geo-updates
make geo-audit
make validate-geo
make panel
make analysis
make sync-paper-stats
make main-tables
python scripts/15_pcs_status.py
```

Target:

```text
External evidence verified: >= 50
```
