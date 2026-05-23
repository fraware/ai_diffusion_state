"""One-off helper to regenerate tests/fixtures/patents_cnipa_micro.csv."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
cities = [
    ("Beijing", "Beijing"),
    ("Shanghai", "Shanghai"),
    ("Shenzhen", "Guangdong"),
    ("Hangzhou", "Zhejiang"),
    ("Suzhou", "Jiangsu"),
    ("Nanjing", "Jiangsu"),
    ("Wuhan", "Hubei"),
    ("Chengdu", "Sichuan"),
    ("Chongqing", "Chongqing"),
    ("Xi'an", "Shaanxi"),
    ("Hefei", "Anhui"),
    ("Jinan", "Shandong"),
    ("Qingdao", "Shandong"),
    ("Ningbo", "Zhejiang"),
    ("Wuxi", "Jiangsu"),
    ("Changsha", "Hunan"),
    ("Zhengzhou", "Henan"),
    ("Fuzhou", "Fujian"),
    ("Xiamen", "Fujian"),
    ("Kunming", "Yunnan"),
    ("Guiyang", "Guizhou"),
    ("Nanchang", "Jiangxi"),
    ("Shijiazhuang", "Hebei"),
    ("Taiyuan", "Shanxi"),
    ("Hohhot", "Inner Mongolia"),
    ("Harbin", "Heilongjiang"),
    ("Changchun", "Jilin"),
    ("Dalian", "Liaoning"),
    ("Shenyang", "Liaoning"),
    ("Tianjin", "Tianjin"),
    ("Guangzhou", "Guangdong"),
    ("Dongguan", "Guangdong"),
    ("Foshan", "Guangdong"),
    ("Zhuhai", "Guangdong"),
    ("Wenzhou", "Zhejiang"),
    ("Jiaxing", "Zhejiang"),
    ("Shaoxing", "Zhejiang"),
    ("Yantai", "Shandong"),
    ("Weifang", "Shandong"),
    ("Zibo", "Shandong"),
    ("Luoyang", "Henan"),
    ("Xuzhou", "Jiangsu"),
    ("Nantong", "Jiangsu"),
    ("Yangzhou", "Jiangsu"),
    ("Zhenjiang", "Jiangsu"),
    ("Huzhou", "Zhejiang"),
    ("Jinhua", "Zhejiang"),
    ("Taizhou", "Zhejiang"),
    ("Quanzhou", "Fujian"),
    ("Zhongshan", "Guangdong"),
    ("Huizhou", "Guangdong"),
    ("Jiangmen", "Guangdong"),
    ("Zhaoqing", "Guangdong"),
    ("Maanshan", "Anhui"),
    ("Wuhu", "Anhui"),
    ("Bengbu", "Anhui"),
]
titles = [
    ("机器视觉缺陷检测系统", "H01L21/66"),
    ("工业机器人焊接产线控制", "B25J9/16"),
    ("预测性维护设备健康管理平台", "G05B19/418"),
    ("数字孪生生产线仿真优化", "G06F30/20"),
    ("智能质检良率分析系统", "G01N21/88"),
    ("智能排产调度优化方法", "G06Q10/06"),
    ("化工过程参数闭环控制", "G05D1/02"),
    ("智能仓储路径优化系统", "G06Q10/08"),
    ("工业互联网MES平台", "G06F8/30"),
    ("半导体晶圆量测方法", "H01L21/672"),
    ("锂电池极片缺陷检测", "H01M10/058"),
    ("反应釜工艺参数优化", "C07C1/00"),
    ("汽车整车机器视觉检测平台", "B60W30/00"),
    ("船舶数字孪生智能制造系统", "B63B65/00"),
    ("制药智能质检包装线", "A61J1/00"),
    ("钢铁冶炼过程控制优化", "C21B7/00"),
    ("纺织智能排产调度系统", "D03D47/00"),
    ("食品灌装机器视觉检测", "A23L5/00"),
    ("光伏组件机器视觉检测", "H02S50/00"),
    ("包装机械工业机器人控制", "B65B57/20"),
    ("电机预测性维护平台", "H02K11/00"),
    ("工程机械智能排产系统", "F15B11/00"),
]
rows = []
pid = 1
for year in range(2015, 2025):
    for city, prov in cities:
        title, ipc = titles[pid % len(titles)]
        rows.append(
            {
                "申请号": f"CN{year}{pid:08d}",
                "申请年份": year,
                "公开公告年份": year,
                "授权公告年份": year if year < 2024 else "",
                "申请人": f"{city}智造科技有限公司",
                "申请人类型": 2,
                "申请人地址": f"{prov}{city}高新区",
                "申请人国家": "CN",
                "申请人省份": prov,
                "申请人城市": city,
                "申请人区县": "",
                "专利名称": f"{year}年{title}",
                "专利类型": "发明",
                "IPC分类号": ipc,
                "IPC主分类号": ipc,
                "摘要文本": f"本发明涉及{title}，用于智能制造场景。",
            }
        )
        pid += 1

out = ROOT / "tests" / "fixtures" / "patents_cnipa_micro.csv"
out.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
print(f"wrote {out} ({len(rows)} rows, {len(cities)} cities)")
