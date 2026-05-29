"""Apply Phase A priority-1 manual mappings to top_applicant_city_map.csv."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data/seed/top_applicant_city_map.csv"

# applicant_name -> (city, province, url, confidence, notes)
PRIORITY_1: dict[str, tuple[str, str, str, str, str]] = {
    "HUAWEI TECH CO LTD": (
        "Shenzhen",
        "Guangdong",
        "https://www.huawei.com/en/corporate-information",
        "official_headquarters_page",
        "Official corporate information page.",
    ),
    "BOE TECHNOLOGY GROUP CO LTD": (
        "Beijing",
        "Beijing",
        "https://www.boe.com/en/about-boe",
        "official_headquarters_page",
        "Official company profile.",
    ),
    "ALIBABA GROUP HOLDING LTD": (
        "Hangzhou",
        "Zhejiang",
        "https://www.alibabagroup.com/en-US/contact",
        "official_headquarters_page",
        "Official group contact page.",
    ),
    "UNIV ZHEJIANG": (
        "Hangzhou",
        "Zhejiang",
        "https://www.zju.edu.cn/english/",
        "university_location",
        "Official Zhejiang University English site.",
    ),
    "STATE GRID CORP CHINA": (
        "Beijing",
        "Beijing",
        "https://www.sgcc.com.cn/html/sgcc_en/",
        "official_headquarters_page",
        "State Grid official English portal.",
    ),
    "UNIV TSINGHUA": (
        "Beijing",
        "Beijing",
        "https://www.tsinghua.edu.cn/en/",
        "university_location",
        "Official Tsinghua University English site.",
    ),
    "UNIV SOUTH CHINA TECH": (
        "Guangzhou",
        "Guangdong",
        "https://www.scut.edu.cn/en/",
        "university_location",
        "Official SCUT English site.",
    ),
    "UNIV SOUTHEAST": (
        "Nanjing",
        "Jiangsu",
        "https://www.seu.edu.cn/english/",
        "university_location",
        "Official Southeast University English site.",
    ),
    "ZTE CORP": (
        "Shenzhen",
        "Guangdong",
        "https://www.zte.com.cn/global/about/corporate_information.html",
        "official_headquarters_page",
        "Official ZTE corporate information.",
    ),
    "UNIV ELECTRONIC SCI & TECH CHINA": (
        "Chengdu",
        "Sichuan",
        "https://www.uestc.edu.cn/en/",
        "university_location",
        "Official UESTC English site.",
    ),
    "UNIV XIDIAN": (
        "Xi'an",
        "Shaanxi",
        "https://en.xidian.edu.cn/",
        "university_location",
        "Official Xidian University English site.",
    ),
    "UNIV HUAZHONG SCIENCE TECH": (
        "Wuhan",
        "Hubei",
        "https://english.hust.edu.cn/",
        "university_location",
        "Official HUST English site.",
    ),
    "UNIV SHANDONG": (
        "Jinan",
        "Shandong",
        "https://www.sdu.edu.cn/english/",
        "university_location",
        "Official Shandong University English site.",
    ),
    "UNIV BEIHANG": (
        "Beijing",
        "Beijing",
        "https://ev.buaa.edu.cn/",
        "university_location",
        "Official Beihang University site.",
    ),
    "UNIV GUANGDONG TECHNOLOGY": (
        "Guangzhou",
        "Guangdong",
        "https://www.gdut.edu.cn/",
        "university_location",
        "Official GDUT site.",
    ),
    "UNIV CENTRAL SOUTH": (
        "Changsha",
        "Hunan",
        "https://www.csu.edu.cn/",
        "university_location",
        "Official Central South University site.",
    ),
    "UNIV ZHEJIANG TECHNOLOGY": (
        "Hangzhou",
        "Zhejiang",
        "https://www.zjut.edu.cn/",
        "university_location",
        "Official ZJUT site.",
    ),
    "UNIV JILIN": (
        "Changchun",
        "Jilin",
        "https://www.jlu.edu.cn/",
        "university_location",
        "Official Jilin University site.",
    ),
    "CHINA PETROLEUM & CHEM CORP": (
        "Beijing",
        "Beijing",
        "https://www.sinopecgroup.com/group/en/",
        "official_headquarters_page",
        "Sinopec group official English site.",
    ),
    "GUANGDONG POWER GRID CO": (
        "Guangzhou",
        "Guangdong",
        "https://www.gd.csg.cn/",
        "official_headquarters_page",
        "China Southern Power Grid Guangdong.",
    ),
    "UNIV SICHUAN": (
        "Chengdu",
        "Sichuan",
        "https://en.scu.edu.cn/",
        "university_location",
        "Official Sichuan University English site.",
    ),
    "UNIV HOHAI": (
        "Nanjing",
        "Jiangsu",
        "https://www.hhu.edu.cn/",
        "university_location",
        "Official Hohai University site.",
    ),
    "CHINA UNICOM": (
        "Beijing",
        "Beijing",
        "https://www.chinaunicom.com.cn/",
        "official_headquarters_page",
        "Official China Unicom corporate site.",
    ),
    "UNIV TONGJI": (
        "Shanghai",
        "Shanghai",
        "https://www.tongji.edu.cn/",
        "university_location",
        "Official Tongji University site.",
    ),
    "UNIV NORTHWESTERN POLYTECHNICAL": (
        "Xi'an",
        "Shaanxi",
        "https://en.nwpu.edu.cn/",
        "university_location",
        "Official NWPU English site.",
    ),
    "UNIV JIANGSU": (
        "Zhenjiang",
        "Jiangsu",
        "https://en.ujs.edu.cn/",
        "university_location",
        "Official Jiangsu University English site.",
    ),
    "UNIV JIANGNAN": (
        "Wuxi",
        "Jiangsu",
        "https://en.jiangnan.edu.cn/",
        "university_location",
        "Official Jiangnan University English site.",
    ),
    "UNIV SUN YAT SEN": (
        "Guangzhou",
        "Guangdong",
        "https://www.sysu.edu.cn/",
        "university_location",
        "Official Sun Yat-sen University site.",
    ),
    "PETROCHINA CO LTD": (
        "Beijing",
        "Beijing",
        "https://www.petrochina.com.cn/ptr/",
        "official_headquarters_page",
        "Official PetroChina corporate site.",
    ),
    "VIVO COMM TECHNOLOGY CO LTD": (
        "Dongguan",
        "Guangdong",
        "https://www.vivo.com/en/about-vivo",
        "official_headquarters_page",
        "Official vivo about page.",
    ),
    "UNIV BEIJING POSTS & TELECOMM": (
        "Beijing",
        "Beijing",
        "https://www.bupt.edu.cn/",
        "university_location",
        "Official BUPT site.",
    ),
    "GUANGDONG MIDEA DOMESTIC ELECTRICAL APPLIANCE MFG CO LTD": (
        "Foshan",
        "Guangdong",
        "https://www.midea.com/en/about-midea",
        "official_headquarters_page",
        "Official Midea about page.",
    ),
    "YANGTZE MEMORY TECH CO LTD": (
        "Wuhan",
        "Hubei",
        "https://www.ymtc.com/en/",
        "official_headquarters_page",
        "Official YMTC English site.",
    ),
    "NINGDE CONTEMPORARY AMPEREX TECH CO LTD": (
        "Ningde",
        "Fujian",
        "https://www.catl.com/en/",
        "official_headquarters_page",
        "Official CATL English site.",
    ),
    "UNIV SOUTHWEST JIAOTONG": (
        "Chengdu",
        "Sichuan",
        "https://en.swjtu.edu.cn/",
        "university_location",
        "Official SWJTU English site.",
    ),
    "UNIV NORTHEASTERN": (
        "Shenyang",
        "Liaoning",
        "https://www.neu.edu.cn/",
        "university_location",
        "Official Northeastern University (China) site.",
    ),
    "BYD CO LTD": (
        "Shenzhen",
        "Guangdong",
        "https://www.byd.com/en/",
        "official_headquarters_page",
        "Official BYD global site.",
    ),
    "NAT UNIV DEFENSE TECHNOLOGY PLA": (
        "Changsha",
        "Hunan",
        "https://www.nudt.edu.cn/",
        "university_location",
        "Official NUDT site.",
    ),
    "BANK OF CHINA CO LTD": (
        "Beijing",
        "Beijing",
        "https://www.boc.cn/",
        "official_headquarters_page",
        "Official Bank of China site.",
    ),
    "UNIV BEIJING": (
        "Beijing",
        "Beijing",
        "https://english.pku.edu.cn/",
        "university_location",
        "Official Peking University English site.",
    ),
    "UNIV FUDAN": (
        "Shanghai",
        "Shanghai",
        "https://www.fudan.edu.cn/en/",
        "university_location",
        "Official Fudan University English site.",
    ),
    "CHINA ELECTRIC POWER RES INST CO LTD": (
        "Beijing",
        "Beijing",
        "https://www.epri.sgcc.com.cn/",
        "official_headquarters_page",
        "China Electric Power Research Institute (State Grid).",
    ),
    "INDUSTRIAL & COMMERCIAL BANK OF CHINA CO LTD": (
        "Beijing",
        "Beijing",
        "https://www.icbc.com.cn/icbc/",
        "official_headquarters_page",
        "Official ICBC corporate site.",
    ),
}

FOREIGN_LEAVE_BLANK = frozenset(
    {
        "SAMSUNG ELECTRONICS CO LTD",
        "TAIWAN SEMICONDUCTOR MFG CO LTD",
        "QUALCOMM INC",
        "LG CHEMICAL LTD",
        "SAMSUNG DISPLAY CO LTD",
        "TOYOTA MOTOR CO LTD",
        "FORD GLOBAL TECH LLC",
        "BOSCH GMBH ROBERT",
        "MICROSOFT TECHNOLOGY LICENSING LLC",
        "PANASONIC IP MAN CO LTD",
        "INTEL CORP",
        "MITSUBISHI ELECTRIC CORP",
        "SONY CORP",
        "LG DISPLAY CO LTD",
        "FANUC CORP",
    }
)


def main() -> int:
    rows: list[dict[str, str]] = []
    filled = 0
    with MAP_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            name = str(row.get("applicant_name") or "").strip()
            if name in PRIORITY_1:
                city, prov, url, conf, notes = PRIORITY_1[name]
                row["applicant_city"] = city
                row["applicant_province"] = prov
                row["source_url"] = url
                row["geo_match_confidence"] = conf
                row["notes"] = notes
                filled += 1
            elif name in FOREIGN_LEAVE_BLANK:
                row["applicant_city"] = ""
                row["applicant_province"] = ""
                row["source_url"] = ""
                row["geo_match_confidence"] = ""
                row["notes"] = "Foreign parent entity; not mapped to CN city for Atlas."
            rows.append(row)

    with MAP_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print({"priority_1_filled": filled, "path": str(MAP_PATH)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
