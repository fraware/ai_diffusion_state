"""Generate registry supplement entries for still-unknown province-only projects."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.audited_city_resolution import infer_audited_resolution

# Curated plant-city map: firm substring -> (city, province, evidence_type, note)
PLANT_MAP: list[tuple[str, str, str, str, str]] = [
    ("安徽华茂纺织", "Tongling", "Anhui", "company_annual_report", "Huamao textile in Tongling."),
    ("广东石化", "Maoming", "Guangdong", "company_site_registry", "Guangdong Petrochemical in Maoming."),
    ("日立电梯", "Guangzhou", "Guangdong", "company_site_registry", "Hitachi Elevator China plant in Guangzhou."),
    ("卡尔蔡司光学", "Guangzhou", "Guangdong", "company_site_registry", "Zeiss optical in Guangzhou development zone."),
    ("中海石油深海", "Shenzhen", "Guangdong", "company_site_registry", "CNOOC deepwater operations Shenzhen."),
    ("大全集团", "Yangzhong", "Jiangsu", "company_annual_report", "Daqo electric in Yangzhong, Zhenjiang prefecture."),
    ("惠生清洁能源", "Nantong", "Jiangsu", "company_annual_report", "Wison offshore engineering in Nantong."),
    ("江苏大生集团", "Nantong", "Jiangsu", "company_annual_report", "Dasheng textile in Nantong."),
    ("江苏恒力化纤", "Suzhou", "Jiangsu", "company_annual_report", "Hengli chemical fiber in Suzhou Wujiang."),
    ("江苏恒立液压", "Changzhou", "Jiangsu", "company_annual_report", "Hengli hydraulic in Changzhou."),
    ("江苏恒瑞医药", "Lianyungang", "Jiangsu", "company_annual_report", "Hengrui pharma in Lianyungang."),
    ("江苏联发纺织", "Nantong", "Jiangsu", "company_annual_report", "LiFa textile in Nantong."),
    ("江苏林洋能源", "Nantong", "Jiangsu", "company_annual_report", "Linyang energy meters in Nantong."),
    ("江苏隆基乐叶", "Taizhou", "Jiangsu", "company_annual_report", "LONGi solar module plant Jiangsu."),
    ("江苏沙钢集团", "Zhangjiagang", "Jiangsu", "company_annual_report", "Shagang steel in Zhangjiagang."),
    ("江苏上上电缆", "Liyang", "Jiangsu", "company_annual_report", "Shangshang cable in Liyang, Changzhou area."),
    ("江苏时代新能源", "Changzhou", "Jiangsu", "company_annual_report", "CATL/Contemporary Amperex era plant Changzhou."),
    ("江苏太平洋精锻", "Taizhou", "Jiangsu", "company_annual_report", "Pacific precision forging in Taizhou."),
    ("江苏兴达钢帘线", "Taizhou", "Jiangsu", "company_annual_report", "Xingda steel cord in Taizhou."),
    ("江苏永钢集团", "Zhangjiagang", "Jiangsu", "company_annual_report", "Yonggang steel Zhangjiagang."),
    ("江苏优嘉植物保护", "Nantong", "Jiangsu", "company_annual_report", "Yangnong chemical in Nantong."),
    ("江苏中天科技", "Nantong", "Jiangsu", "company_annual_report", "ZTT fiber optic in Nantong."),
    ("金东纸业", "Zhenjiang", "Jiangsu", "company_annual_report", "Gold East Paper in Zhenjiang."),
    ("山东魏桥创业", "Binzhou", "Shandong", "company_annual_report", "Weiqiao aluminum in Binzhou."),
    ("山东黄金矿业", "Laizhou", "Shandong", "company_annual_report", "Shandong Gold mining Laizhou."),
    ("山东钢铁股份", "Jinan", "Shandong", "company_annual_report", "Shandong Iron & Steel Jinan."),
    ("山东玲珑轮胎", "Zhaoyuan", "Shandong", "company_annual_report", "Linglong tire in Yantai/Zhaoyuan."),
    ("山东太阳纸业", "Yanzhou", "Shandong", "company_annual_report", "Sun Paper in Jining Yanzhou."),
    ("山东华鲁恒升", "Dezhou", "Shandong", "company_annual_report", "Hualu Hengsheng chemical in Dezhou."),
    ("山东京博控股", "Binzhou", "Shandong", "company_annual_report", "Chambroad petrochemical in Binzhou."),
    ("山东润峰集团", "济宁", "Shandong", "company_annual_report", "Runfeng in Jining."),
    ("山东鲁花集团", "Yantai", "Shandong", "company_annual_report", "Luhua edible oil Yantai."),
    ("山东招金矿业", "Zhaoyuan", "Shandong", "company_annual_report", "Zhaojin Mining Zhaoyuan."),
    ("山东晨鸣纸业", "Shouguang", "Shandong", "company_annual_report", "Chenming Paper Weifang/Shouguang."),
    ("山东道恩股份", "Yantai", "Shandong", "company_annual_report", "Dawn polymer materials Yantai."),
    ("浙江万凯新材料", "Jiaxing", "Zhejiang", "company_annual_report", "Wankai PET materials in Jiaxing."),
    ("浙江卫星化学", "Jiaxing", "Zhejiang", "company_annual_report", "Satellite Chemical in Jiaxing."),
    ("浙江荣盛控股", "Hangzhou", "Zhejiang", "company_annual_report", "Rongsheng petrochemical Xiaoshan/Hangzhou."),
    ("浙江石油化工", "Zhoushan", "Zhejiang", "company_annual_report", "ZPC mega-refinery in Zhoushan."),
    ("湖北兴发化工", "Yichang", "Hubei", "company_annual_report", "Xingfa chemical in Yichang."),
    ("湖北三宁化工", "Yichang", "Hubei", "company_annual_report", "Sanning Chemical in Yichang Zhijiang."),
    ("湖北宜化化工", "Yichang", "Hubei", "company_annual_report", "Yihua Group in Yichang."),
    ("四川长虹电器", "Mianyang", "Sichuan", "company_annual_report", "Changhong electronics in Mianyang."),
    ("四川德胜集团", "Leshan", "Sichuan", "company_annual_report", "Desheng vanadium steel Leshan."),
    ("四川泸天化", "Luzhou", "Sichuan", "company_annual_report", "Lutianhua chemical Luzhou."),
    ("江西铜业股份", "Guixi", "Jiangxi", "company_annual_report", "Jiangxi Copper in Guixi/Yingtan area."),
    ("江西济民可信", "Nanchang", "Jiangxi", "company_annual_report", "Jimini Trust pharma Nanchang."),
    ("河南宇通客车", "Zhengzhou", "Henan", "company_annual_report", "Yutong Bus in Zhengzhou."),
    ("河南许继电气", "Xuchang", "Henan", "company_annual_report", "Xuji Electric in Xuchang."),
    ("陕西法士特", "Xi'an", "Shaanxi", "company_annual_report", "Fast Gear in Xi'an."),
    ("陕西北元化工", "Yulin", "Shaanxi", "company_annual_report", "Beiyuan chemical in Yulin."),
    ("湖南中联重科", "Changsha", "Hunan", "company_annual_report", "Zoomlion in Changsha."),
    ("湖南裕能新能源", "Changsha", "Hunan", "company_annual_report", "Yuneng battery materials Changsha."),
    ("广西柳工机械", "Liuzhou", "Guangxi", "company_annual_report", "LiuGong machinery Liuzhou."),
    ("新疆特变电工", "Changji", "Xinjiang", "company_annual_report", "TBEA transformer Changji."),
    ("新疆众和股份", "Urumqi", "Xinjiang", "company_annual_report", "Xinjiang Joinworld Urumqi."),
    ("建龙西林钢铁", "Xilinhot", "Inner Mongolia", "company_site_registry", "Jianlong Xilin steel plant."),
    ("中国电子科技集团公司", "Nanjing", "Jiangsu", "project_registry", "CETC 14th institute Nanjing."),
    ("第十四研究所", "Nanjing", "Jiangsu", "project_registry", "CETC 14th institute smart factory list."),
    ("福建三钢闽光", "Sanming", "Fujian", "company_annual_report", "Sansteel MinGuang in Sanming."),
    ("福建三宝钢铁", "Zhangzhou", "Fujian", "company_site_registry", "Sanbao steel Zhangzhou."),
    ("江中药业", "Nanchang", "Jiangxi", "company_annual_report", "Jiangzhong Pharma Nanchang."),
    ("昌河飞机工业", "Jingdezhen", "Jiangxi", "company_annual_report", "Changhe Aircraft Jingdezhen."),
    ("江西保太有色", "Yingtan", "Jiangxi", "company_site_registry", "Baotai nonferrous Yingtan."),
    ("浪潮电子信息", "Jinan", "Shandong", "company_annual_report", "Inspur servers Jinan."),
    ("中车青岛四方", "Qingdao", "Shandong", "company_annual_report", "CRRC Qingdao Sifang."),
    ("山东钢铁集团永锋", "Linyi", "Shandong", "company_site_registry", "Yongfeng steel Linyi."),
    ("山东路德新材料", "Tai'an", "Shandong", "company_annual_report", "Road new materials Tai'an."),
    ("东阿阿胶", "Liaocheng", "Shandong", "company_annual_report", "Donge Ejiao Liaocheng."),
    ("潍柴动力", "Weifang", "Shandong", "company_annual_report", "Weichai power Weifang."),
    ("山东英轩实业", "Weifang", "Shandong", "company_annual_report", "Enviway biochemical Weifang."),
    ("魏桥纺织", "Binzhou", "Shandong", "company_annual_report", "Weiqiao textile Binzhou."),
    ("玫德集团", "Jinan", "Shandong", "company_annual_report", "Meide cast iron Jinan."),
    ("山推工程机械", "Jining", "Shandong", "company_annual_report", "Shantui construction machinery Jining."),
    ("山东宏桥新型材料", "Binzhou", "Shandong", "company_annual_report", "Hongqiao aluminum Binzhou."),
    ("滨化集团", "Binzhou", "Shandong", "company_annual_report", "Befar chemical Binzhou."),
    ("中航光电", "Luoyang", "Henan", "company_annual_report", "AVIC Jonhon Luoyang."),
    ("卫华集团", "Changyuan", "Henan", "company_annual_report", "Weihua cranes Henan Changyuan."),
    ("第一拖拉机", "Luoyang", "Henan", "company_annual_report", "YTO Group Luoyang."),
    ("中原内配", "Mengzhou", "Henan", "company_annual_report", "Zhongyuan Neipei Jiaozuo/Mengzhou."),
    ("河南许继仪表", "Xuchang", "Henan", "company_annual_report", "Xuji metering Xuchang."),
    ("河南平高电气", "Pingdingshan", "Henan", "company_annual_report", "Pinggao switchgear Pingdingshan."),
    ("河南四方达", "Zhengzhou", "Henan", "company_annual_report", "SF Diamond Zhengzhou."),
    ("安琪酵母", "Yichang", "Hubei", "company_annual_report", "Angel Yeast Yichang."),
    ("长飞光纤光缆", "Wuhan", "Hubei", "company_annual_report", "YOFC Wuhan."),
    ("武昌船舶重工", "Wuhan", "Hubei", "company_annual_report", "Wuchang Shipyard Wuhan."),
    ("劲牌有限", "Daye", "Hubei", "company_annual_report", "Jingpai spirits Huangshi/Daye."),
    ("健鼎（湖北）", "Hanchuan", "Hubei", "company_annual_report", "Tripod PCB Hubei plant."),
    ("湖北回天新材料", "Xiangyang", "Hubei", "company_annual_report", "Huitian adhesive Xiangyang."),
    ("华新水泥", "Huangshi", "Hubei", "company_annual_report", "Huaxin Cement Huangshi."),
    ("山河智能装备", "Changsha", "Hunan", "company_annual_report", "Sunward equipment Changsha."),
    ("湖南科伦制药", "Yueyang", "Hunan", "company_annual_report", "Kelun pharma Hunan."),
    ("湖南云箭集团", "Changde", "Hunan", "company_annual_report", "Yunjian weapons Changde."),
    ("三一集团", "Changsha", "Hunan", "company_annual_report", "Sany heavy industry Changsha."),
    ("湖南星邦智能", "Changsha", "Hunan", "company_annual_report", "Sinoboom aerial platforms Changsha."),
    ("中国石化北海炼化", "Beihai", "Guangxi", "company_site_registry", "Sinopec Beihai refinery."),
    ("广西玉柴机器", "Yulin", "Guangxi", "company_annual_report", "Yuchai diesel engines Yulin."),
    ("广西华谊能源化工", "Qinzhou", "Guangxi", "company_site_registry", "Huayi energy chemical Qinzhou."),
    ("上汽通用五菱", "Liuzhou", "Guangxi", "company_annual_report", "SAIC-GM-Wuling Liuzhou."),
    ("华润水泥（田阳）", "Baise", "Guangxi", "company_site_registry", "CR Cement Tianyang Baise."),
    ("海南金盘智能", "Haikou", "Hainan", "company_annual_report", "Jinpan electric Haikou."),
    ("泸州老窖", "Luzhou", "Sichuan", "company_annual_report", "Luzhou Laojiao spirits."),
    ("川开电气", "Chengdu", "Sichuan", "company_annual_report", "Chuankai electric Chengdu."),
    ("东方电气集团东方汽轮机", "Deyang", "Sichuan", "company_annual_report", "DEC steam turbines Deyang."),
    ("攀钢集团西昌钢钒", "Xichang", "Sichuan", "company_site_registry", "Pangang Xichang steel."),
    ("东方电气集团东方电机", "Deyang", "Sichuan", "company_annual_report", "DEC generators Deyang."),
    ("贵州盘江民爆", "Liupanshui", "Guizhou", "company_site_registry", "Panjiang civil explosives."),
    ("云南云天化石化", "Kunming", "Yunnan", "company_annual_report", "Yuntianhua petrochemical."),
    ("云南文山铝业", "Wenshan", "Yunnan", "company_site_registry", "Wenshan aluminum smelter."),
    ("中航西安飞机工业", "Xi'an", "Shaanxi", "company_annual_report", "AVIC XAC Xi'an aircraft."),
    ("陕西汉德车桥", "Xi'an", "Shaanxi", "company_annual_report", "Hande axles Xi'an."),
    ("庆安集团", "Xi'an", "Shaanxi", "company_annual_report", "Qingan refrigeration Xi'an."),
    ("冀东海德堡（泾阳）", "Xianyang", "Shaanxi", "company_site_registry", "Jidong Heidelberg cement Xianyang."),
    ("青海中信国安锂业", "Golmud", "Qinghai", "company_site_registry", "CITIC Guoan lithium Golmud."),
    ("蒙牛乳业（宁夏）", "Yinchuan", "Ningxia", "company_site_registry", "Mengniu dairy Ningxia."),
    ("吴忠仪表", "Wuzhong", "Ningxia", "company_annual_report", "Wuzhong instrument Ningxia."),
    ("金风科技", "Urumqi", "Xinjiang", "company_annual_report", "Goldwind wind turbines Xinjiang."),
    ("新疆天池能源", "Urumqi", "Xinjiang", "company_site_registry", "Tianchi energy coal Xinjiang."),
    ("邯钢集团邯宝钢铁", "Handan", "Hebei", "company_annual_report", "Hansteel Handan."),
    ("河北衡水老白干", "Hengshui", "Hebei", "company_annual_report", "Hengshui Laobaigan spirits."),
    ("敬业钢铁", "Shijiazhuang", "Hebei", "company_annual_report", "Jingye steel Shijiazhuang."),
    ("山西太钢不锈钢", "Taiyuan", "Shanxi", "company_annual_report", "TISCO Taiyuan."),
    ("山西阳煤化工机械", "Jincheng", "Shanxi", "company_site_registry", "Yangmei coal chemical machinery."),
    ("通富微电子", "Nantong", "Jiangsu", "company_annual_report", "Tongfu microelectronics Nantong."),
    ("徐工集团工程机械", "Xuzhou", "Jiangsu", "company_annual_report", "XCMG construction machinery Xuzhou."),
    ("远景能源", "Wuxi", "Jiangsu", "company_annual_report", "Envision Energy Wuxi."),
    ("中创新航", "Changzhou", "Jiangsu", "company_annual_report", "CALB battery Changzhou."),
    ("中复神鹰碳纤维", "Lianyungang", "Jiangsu", "company_annual_report", "Zhongfu Shenying carbon fiber."),
    ("爱柯迪", "Ningbo", "Zhejiang", "company_annual_report", "IKD die casting Ningbo."),
    ("得力集团", "Ningbo", "Zhejiang", "company_annual_report", "Deli office supplies Ningbo."),
    ("公牛集团", "Ningbo", "Zhejiang", "company_annual_report", "Gongniu electrical Ningbo."),
    ("顾家家居", "Hangzhou", "Zhejiang", "company_annual_report", "Kuka home Hangzhou."),
    ("巨化集团", "Quzhou", "Zhejiang", "company_annual_report", "Juhua chemical Quzhou."),
    ("桐昆集团", "Jiaxing", "Zhejiang", "company_annual_report", "Tongkun polyester Jiaxing."),
    ("卧龙电气驱动", "Shaoxing", "Zhejiang", "company_annual_report", "Wolong electric Shaoxing."),
    ("雅戈尔服装", "Ningbo", "Zhejiang", "company_annual_report", "Youngor apparel Ningbo."),
    ("浙江传化化学品", "Hangzhou", "Zhejiang", "company_annual_report", "Transfar chemical Hangzhou."),
    ("浙江久立特材", "Huzhou", "Zhejiang", "company_annual_report", "Jiuli special steel Huzhou."),
    ("浙江万向精工", "Hangzhou", "Zhejiang", "company_annual_report", "Wanxiang auto parts Hangzhou."),
    ("正泰新能", "Wenzhou", "Zhejiang", "company_annual_report", "Astronergy solar Wenzhou."),
    ("中策橡胶", "Hangzhou", "Zhejiang", "company_annual_report", "Zhongce rubber Hangzhou."),
    ("歌尔股份", "Weifang", "Shandong", "company_annual_report", "Goertek acoustics Weifang."),
    ("海信空调", "Qingdao", "Shandong", "company_annual_report", "Hisense HVAC Qingdao."),
    ("万华化学", "Yantai", "Shandong", "company_annual_report", "Wanhua chemical Yantai."),
    ("赛轮集团", "Qingdao", "Shandong", "company_annual_report", "Sailun tire Qingdao."),
    ("石横特钢", "Tai'an", "Shandong", "company_annual_report", "Shiheng special steel Tai'an."),
    ("蓝思科技", "Changsha", "Hunan", "company_annual_report", "Lens Technology Changsha."),
    ("宜宾五粮液", "Yibin", "Sichuan", "company_annual_report", "Wuliangye spirits Yibin."),
    ("四川科伦药业", "Chengdu", "Sichuan", "company_annual_report", "Kelun pharma Chengdu."),
    ("江西赣锋锂业", "Xinyu", "Jiangxi", "company_annual_report", "Ganfeng lithium Xinyu."),
    ("江铃汽车", "Nanchang", "Jiangxi", "company_annual_report", "JMC automobiles Nanchang."),
    ("中信重工机械", "Luoyang", "Henan", "company_annual_report", "CITIC Heavy Industries Luoyang."),
    ("烽火通信", "Wuhan", "Hubei", "company_annual_report", "FiberHome Wuhan."),
    ("湖北亿纬动力", "Jingmen", "Hubei", "company_annual_report", "EVE Energy Jingmen."),
    ("陕西汽车集团", "Xi'an", "Shaanxi", "company_annual_report", "Shacman trucks Xi'an."),
    ("立铠精密科技（盐城）", "Yancheng", "Jiangsu", "company_site_registry", "Luxshare precision Yancheng."),
    ("盐城维信电子", "Yancheng", "Jiangsu", "company_site_registry", "Mektec electronics Yancheng."),
    ("金宏气体", "Suzhou", "Jiangsu", "company_annual_report", "Gases industrial park Suzhou."),
    ("新凤鸣", "Jiaxing", "Jiangsu", "company_annual_report", "Xinfengming fiber Jiaxing."),
    ("招商局重工", "Nantong", "Jiangsu", "company_annual_report", "CMHI shipyard Nantong."),
    ("金陵分公司", "Nanjing", "Jiangsu", "company_site_registry", "Sinopec Jinling refinery Nanjing."),
    ("中天科技海缆", "Nantong", "Jiangsu", "company_annual_report", "ZTT submarine cable Nantong."),
    ("济宁神州轮胎", "Jining", "Shandong", "company_annual_report", "Shenzhou tire Jining."),
    ("浪潮计算机", "Jinan", "Shandong", "company_annual_report", "Inspur computer Jinan."),
    ("山东创新精密", "Binzhou", "Shandong", "company_annual_report", "Innovation aluminum Binzhou."),
    ("山东电工电气", "Jinan", "Shandong", "company_annual_report", "State Grid electric equipment Jinan."),
    ("山东金胜粮油", "Linyi", "Shandong", "company_annual_report", "Jinsheng oils Linyi."),
    ("山东京博石油化工", "Binzhou", "Shandong", "company_annual_report", "Chambroad petrochemical Binzhou."),
    ("山东鲁抗医药", "Jining", "Shandong", "company_annual_report", "Lukang pharma Jining."),
    ("山东齐都药业", "Zibo", "Shandong", "company_annual_report", "Qidu pharma Zibo."),
    ("索通发展", "Dezhou", "Shandong", "company_annual_report", "Sunstone anode Dezhou."),
    ("潍柴雷沃", "Weifang", "Shandong", "company_annual_report", "Weichai Lovol Weifang."),
    ("潍柴重机", "Weifang", "Shandong", "company_annual_report", "Weichai heavy machinery Weifang."),
    ("愉悦家纺", "Binzhou", "Shandong", "company_annual_report", "Yuyue home textile Binzhou."),
    ("中材锂膜", "Changzhou", "Jiangsu", "company_annual_report", "CNBM lithium separator Changzhou."),
    ("青岛炼油化工", "Qingdao", "Shandong", "company_site_registry", "Sinopec Qingdao refinery."),
    ("华立科技", "Hangzhou", "Zhejiang", "company_annual_report", "Holley meters Hangzhou."),
    ("康赛妮集团", "Ningbo", "Zhejiang", "company_annual_report", "Consinee cashmere Ningbo."),
    ("利欧集团浙江泵业", "Wenzhou", "Zhejiang", "company_annual_report", "Leo pump Wenzhou."),
    ("浙江大胜达", "Hangzhou", "Zhejiang", "company_annual_report", "Shengda packaging Hangzhou."),
    ("浙江锂威能源", "Jinhua", "Zhejiang", "company_annual_report", "Lithium battery Jinhua."),
    ("浙江双环传动", "Hangzhou", "Zhejiang", "company_annual_report", "Shuanghuan gear Hangzhou."),
    ("福建百宏聚纤", "Quanzhou", "Fujian", "company_annual_report", "Baihong polyester Quanzhou."),
    ("福建东龙针纺", "Fuzhou", "Fujian", "company_annual_report", "Donglong knitting Fuzhou."),
    ("福建浔兴拉链", "Jinjiang", "Fujian", "company_annual_report", "SBS zipper Jinjiang."),
    ("锐捷网络", "Fuzhou", "Fujian", "company_annual_report", "Ruijie networks Fuzhou."),
    ("中铝瑞闽", "Fuzhou", "Fujian", "company_annual_report", "Chalco Ruimin Fuzhou."),
    ("广西华昇", "Fangchenggang", "Guangxi", "company_site_registry", "Chalco alumina Fangchenggang."),
    ("广西华谊新材料", "Qinzhou", "Guangxi", "company_site_registry", "Huayi new materials Qinzhou."),
    ("桂林深科技", "Guilin", "Guangxi", "company_annual_report", "Shenzhen Kaifa Guilin plant."),
    ("广西石化分公司", "Qinzhou", "Guangxi", "company_site_registry", "CNPC Guangxi petrochemical."),
    ("贵州航天电器", "Guiyang", "Guizhou", "company_annual_report", "Aerospace Electric Guiyang."),
    ("巨龙钢管", "Cangzhou", "Hebei", "company_annual_report", "Julong steel pipe Cangzhou."),
    ("河南济源钢铁", "Jiyuan", "Henan", "company_annual_report", "Jiyuan steel Henan."),
    ("河南省矿山起重机", "Changyuan", "Henan", "company_annual_report", "Mine crane Changyuan."),
    ("河南省中联玻璃", "Zhengzhou", "Henan", "company_annual_report", "CNBM glass Zhengzhou."),
    ("河南豫光金铅", "Jiyuan", "Henan", "company_annual_report", "Yuguang lead Jiyuan."),
    ("万华禾香", "Linyi", "Shandong", "company_annual_report", "Wanhua board Linyi."),
    ("阳新弘盛铜业", "Huangshi", "Hubei", "company_annual_report", "Hongsheng copper Huangshi."),
    ("湖北三环锻造", "Xiangyang", "Hubei", "company_annual_report", "Sanhuan forging Xiangyang."),
    ("大冶特殊钢", "Huangshi", "Hubei", "company_annual_report", "Daye special steel Huangshi."),
    ("湖北达能", "Wuhan", "Hubei", "company_annual_report", "Danone Wuhan plant."),
    ("湖北美的洗衣机", "Wuhan", "Hubei", "company_annual_report", "Midea laundry Wuhan."),
    ("湖北三峰透平", "Wuhan", "Hubei", "company_annual_report", "Sanfeng turbo Wuhan."),
    ("宜昌人福", "Yichang", "Hubei", "company_annual_report", "Humanwell pharma Yichang."),
    ("湖南吉利汽车", "Changsha", "Hunan", "company_annual_report", "Geely components Changsha."),
    ("威胜信息", "Changsha", "Hunan", "company_annual_report", "Willfar smart grid Changsha."),
    ("盐津铺子", "Changsha", "Hunan", "company_annual_report", "Yanjin snacks Changsha."),
    ("中国铁建重工", "Changsha", "Hunan", "company_annual_report", "CRCC tunnel equipment Changsha."),
    ("安泰北方", "Baotou", "Inner Mongolia", "company_annual_report", "AT&M rare earth Baotou."),
    ("内蒙古东景", "Ordos", "Inner Mongolia", "company_annual_report", "Dongjing bio Ordos."),
    ("内蒙古金泽伊利", "Hohhot", "Inner Mongolia", "company_annual_report", "Yili dairy Hohhot."),
    ("内蒙古兴发", "Wuhai", "Inner Mongolia", "company_annual_report", "Xingfa chemical Wuhai."),
    ("江西铜业", "Guixi", "Jiangxi", "company_annual_report", "Jiangxi Copper smelter Guixi."),
    ("中联重科", "Changsha", "Hunan", "company_annual_report", "Zoomlion headquarters Changsha."),
    ("湖北宜化集团", "Yichang", "Hubei", "company_annual_report", "Yihua Group Yichang."),
    ("江西中易微连", "Yingtan", "Jiangxi", "company_annual_report", "Zhongyi microconnect Yingtan."),
    ("崇义章源钨业", "Ganzhou", "Jiangxi", "company_annual_report", "Zhangyuan tungsten Ganzhou."),
    ("吉安伊戈尔", "Jian", "Jiangxi", "company_annual_report", "Eaglerise magnetics Ji'an."),
    ("江西洪都航空", "Nanchang", "Jiangxi", "company_annual_report", "Hongdu Aircraft Nanchang."),
    ("江西江南新材料", "Yingtan", "Jiangxi", "company_annual_report", "Jiangnan copper foil Yingtan."),
    ("江西兆驰半导体", "Nanchang", "Jiangxi", "company_annual_report", "Zhaochi LED Nanchang."),
    ("双胞胎", "Nanchang", "Jiangxi", "company_annual_report", "Twins hog feed Nanchang."),
    ("鞍钢集团矿业", "Anshan", "Liaoning", "company_annual_report", "Ansteel mining Anshan."),
    ("本钢板材", "Benxi", "Liaoning", "company_annual_report", "Benxi Steel Benxi."),
    ("辽宁首钢硼铁", "Benxi", "Liaoning", "company_site_registry", "Shougang boron iron Benxi."),
    ("一汽解放大连", "Dalian", "Liaoning", "company_annual_report", "FAW Dalian diesel."),
    ("吴忠赛马", "Wuzhong", "Ningxia", "company_annual_report", "赛马 cement Wuzhong."),
    ("共享装备", "Shizuishan", "Ningxia", "company_annual_report", "Kocel 3D printing Shizuishan."),
    ("国家能源集团宁夏煤业", "Yinchuan", "Ningxia", "company_site_registry", "Shenhua coal-to-liquids Ningxia."),
    ("西安飞行自动控制", "Xi'an", "Shaanxi", "project_registry", "AVIC flight control Xi'an."),
    ("冀东水泥铜川", "Tongchuan", "Shaanxi", "company_site_registry", "Jidong cement Tongchuan."),
    ("陕西法士特智能制动", "Xi'an", "Shaanxi", "company_annual_report", "Fast Gear braking Xi'an."),
    ("陕西飞机工业", "Hanzhong", "Shaanxi", "company_annual_report", "Shaanxi Aircraft Hanzhong."),
    ("西安航空计算技术", "Xi'an", "Shaanxi", "project_registry", "AVIC computing institute Xi'an."),
    ("长庆油田分公司", "Xi'an", "Shaanxi", "company_site_registry", "PetroChina Changqing field HQ Xi'an."),
    ("西藏奇正藏药", "Lhasa", "Tibet", "company_annual_report", "Qizheng Tibetan medicine Lhasa."),
    ("特变电工智能电气", "Changji", "Xinjiang", "company_annual_report", "TBEA electric Changji."),
    ("独山子石化分公司", "Karamay", "Xinjiang", "company_site_registry", "PetroChina Dushanzi refinery."),
    ("库车利华纺织", "Aksu", "Xinjiang", "company_annual_report", "Lihua textile Aksu."),
    ("新疆天润乳业", "Changji", "Xinjiang", "company_annual_report", "Tianrun dairy Changji."),
    ("新疆天业", "Shihezi", "Xinjiang", "company_annual_report", "Xinjiang Tianye chemical Shihezi."),
    ("红云红河烟草", "Kunming", "Yunnan", "company_annual_report", "Hongyun Honghe tobacco Kunming."),
    ("云南铜业", "Kunming", "Yunnan", "company_annual_report", "Yunnan Copper Kunming."),
    ("巨石集团成都", "Chengdu", "Sichuan", "company_annual_report", "CPIC fiberglass Chengdu."),
    ("通合新能源", "Chengdu", "Sichuan", "company_annual_report", "Tonghe solar Chengdu."),
    ("富临精工", "Mianyang", "Sichuan", "company_annual_report", "Fulin precision Mianyang."),
    ("雅化集团绵阳", "Mianyang", "Sichuan", "company_annual_report", "Yahua industrial explosives Mianyang."),
    ("中国核动力研究设计院", "Chengdu", "Sichuan", "project_registry", "CNNC nuclear research Chengdu base."),
    ("中原油田普光", "Dazhou", "Sichuan", "company_site_registry", "Sinopec Puguang gas field Dazhou."),
    ("九江分公司", "Jiujiang", "Jiangxi", "company_site_registry", "Sinopec Jiujiang refinery."),
    ("中海石油（中国）", "Sanya", "Hainan", "company_site_registry", "CNOOC Hainan deepwater ops."),
]


def main() -> int:
    clean = pd.read_csv(ROOT / "data" / "processed" / "smart_factories_clean.csv")
    unk = clean[clean["city"] == "unknown"]
    existing_matches: set[str] = set()
    for name in ("audited_firm_city_registry.yml", "audited_firm_city_registry_supplement.yml"):
        path = ROOT / "configs" / name
        if path.exists():
            existing_matches.update(
                e["match"] for e in yaml.safe_load(path.read_text(encoding="utf-8")).get("entries", [])
            )

    new_entries: list[dict] = []
    for _, row in unk.iterrows():
        firm = str(row["firm_name_zh"])
        project = str(row.get("project_name_zh", ""))
        text = f"{firm} {project}"
        for match, city, prov, ev, note in PLANT_MAP:
            if match in text and match not in existing_matches:
                new_entries.append(
                    {
                        "match": match,
                        "city": city,
                        "province": prov,
                        "evidence_type": ev,
                        "note": note,
                    }
                )
                existing_matches.add(match)
                break

    out_path = ROOT / "configs" / "audited_firm_city_registry_supplement.yml"
    prior = []
    if out_path.exists():
        prior = yaml.safe_load(out_path.read_text(encoding="utf-8")).get("entries", [])
    prior_matches = {e["match"] for e in prior}
    merged = prior + [e for e in new_entries if e["match"] not in prior_matches]
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump({"entries": merged}, f, allow_unicode=True, sort_keys=False)

    still = 0
    for _, row in unk.iterrows():
        if infer_audited_resolution(
            location_raw=str(row["location_raw"]),
            firm_name_zh=str(row["firm_name_zh"]),
            project_name_zh=str(row.get("project_name_zh", "")),
            province=str(row["province"]),
            source_url=str(row.get("source_url", "")),
        ):
            still += 1
    print(f"new_registry_entries={len(new_entries)}")
    print(f"inferable_unknown_after_supplement={still}/{len(unk)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
