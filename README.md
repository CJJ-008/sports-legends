# 体育人物与体育精神 · 交互式数据展陈

> 从 327 枚中国奥运金牌到 32 位世界传奇，用交互式图表与沉浸式画廊讲述「体育人物」与「体育精神」。
> 纯静态、零后端，任何设备打开浏览器即可访问：**https://cjj-008.github.io/sports-legends/**

---

## 一、作品简介

本项目是一个以「体育人物与体育精神」为主题的交互式数据展陈网站，按全国比赛水平制作。项目以
**自建数据集** 为基础（全网没有现成的"含照片、生平与精神故事"的体育明星人物卡数据集，人物层
数据全部通过 Python 抓取与清洗自建），用 Apache ECharts 与自研的原生 JS 交互组件，把百年奥运
格局、344 位中国奥运冠军、32 位国际传奇巨星的人生曲线与十个体育精神主题，组织成一场可以"滚动、
拖拽、选择"的线上展览。

## 二、展厅导览

| 板块 | 内容 |
|---|---|
| **首页** | 橙色 Beyond 式开场（四层堆叠大字 + 词列随滚动滑入）、白色品牌跑马灯、32 位传奇封面流（拖拽/键盘翻页）、荣誉之墙双排照片墙（随滚动反向流动） |
| **奥运百年统计厅** | 7 张 ECharts 图表：奖牌总榜（夏/冬切换）、中国逐届金牌、中美对决、强国趋势、项目分布、女子项目演进、参赛规模 |
| **中国冠军环形画廊** | 344 位中国奥运冠军悬浮于 3D 胶片环上，拖拽旋转、正面选中，按项目筛选，联动展示每人全部夺金记录 |
| **巨星曲线厅** | 梅西/C罗/姆巴佩等 28 位足球巨星 FIFA 评分曲线、乔丹/詹姆斯/科比等 25 位 NBA 巨星生涯得分曲线，曲线末端标注姓名，最多 6 人同屏对比 |
| **明星介绍页** | 传奇巨星的完整介绍：立绘、头衔、生平、中英名言、精神标签；与封面流、精神同类页双向深链 |
| **体育精神专题** | 女排精神、首金时刻、中国速度等 10 个主题的编辑式长文，首段逐字点亮（滚动驱动） |
| **精神同类推荐** | 选择 1~3 个欣赏的品质，PyTorch 语义嵌入 + 余弦相似度实时匹配 376 位体育人物中的「精神同类」 |

## 三、技术亮点

- **自建数据集**：Python 全流程管道（requests 抓取 → pandas/numpy 清洗 → JSON 交付），涵盖奥运百年赛果、
  344 位中国冠军人物卡、32 位国际传奇、FIFA/NBA 生涯曲线、精神主题与画像，共 12+ 个清洗后数据文件
- **PyTorch 语义推荐**：用多语言 MiniLM 嵌入模型将 376 位人物的生涯画像编码为 384 维向量，
  与品质语义向量在浏览器端实时计算余弦相似度，再叠加六维精神指标加权评分——推荐引擎离线计算、纯静态部署
- **原生 JS 交互组件**（无框架依赖）：3D 封面流（Coverflow）、3D 环形画廊（Ring Gallery）、
  滚动驱动双排照片墙、逐字点亮长文、粘性堆叠、IntersectionObserver 入场编排
- **暗夜金属设计系统**：#0C0C0C 中性黑底 + #D7E2EA 冰银文字 + 自托管 Kanit/Poppins 字体 +
  五色主题切换器（CSS 变量整站换肤，localStorage 记忆）+ 白色面板反差构图
- **工程质量**：响应式布局、`prefers-reduced-motion` 全量降级、`:focus-visible` 键盘可达、
  WCAG AA 对比度校准、数据加载失败兜底、图表数值标签与图例全部本地化

## 四、技术栈

| 层 | 技术 |
|---|---|
| 前端 | 原生 HTML / CSS / JavaScript，Apache ECharts 5 |
| 数据管道 | Python（pandas / numpy / requests），PyTorch + sentence-transformers（语义嵌入） |
| 人物抠像 | rembg（U2Net 前景分割，本地推理） |
| 部署 | GitHub Pages（main 仓库 `git subtree push --prefix=site origin gh-pages`） |
| 版本管理 | Git 全程管理，阶段化提交存档 |

## 五、项目结构

```
├── site/                  # 纯静态站点（GitHub Pages 部署目录）
│   ├── index.html         # 首页：Beyond 开场 + 封面流 + 荣誉之墙 + 展厅入口
│   ├── olympics.html      # 奥运百年统计厅（7 张图表）
│   ├── champions.html     # 中国冠军环形画廊（3D 胶片环 + 详情面板）
│   ├── stars.html         # 巨星曲线厅（FIFA / NBA 生涯曲线）
│   ├── star.html          # 明星介绍页（传奇立绘 + 名言 + 精神标签）
│   ├── spirit.html        # 体育精神专题（10 主题编辑式长文）
│   ├── match.html         # 精神同类推荐（品质选择 + 实时匹配）
│   ├── css/ js/           # 设计系统与共享交互组件（导航/封面流/环形画廊）
│   ├── data/              # 清洗后的 JSON 数据 + 人物照片
│   └── fonts/             # 自托管 Kanit / Poppins 字体
├── data/
│   ├── raw/               # 原始数据集（体积大，不入库）
│   ├── clean/             # 清洗后的标准 JSON（入库）
│   └── staging/           # 中间整合数据
├── scripts/               # Python 数据管道（抓取 / 清洗 / 建曲线 / 语义嵌入）
└── zcode.md               # 需求、决策与开发过程档案
```

## 六、快速开始

**Windows 用户**：双击项目根目录的 `启动作品.bat`，自动启动本地服务并打开浏览器。

```bash
# 或手动本地预览（需任意静态服务器，根目录为 site/）
cd site
python -m http.server 8765
# 打开 http://localhost:8765
```

> 注意：作品通过 fetch 加载数据，直接双击 index.html 会被浏览器本地安全策略拦截，
> 必须经由静态服务器（上述任一方式）访问。

数据管道重建（可选，成品 JSON 已入库）：

```bash
python scripts/build_olympics_stats.py   # 奥运统计
python scripts/build_nba_curves.py       # NBA 曲线
python scripts/build_fifa_curves.py      # FIFA 曲线
python scripts/build_legends.py          # 国际传奇人物卡
python scripts/build_spirit_themes.py    # 精神主题
python scripts/build_spirit_match.py     # 精神同类向量数据
```

## 七、数据来源与口径

| 数据 | 来源 |
|---|---|
| 奥运赛果 1896–2022 | GitHub `KeithGalli/Olympics-Dataset` |
| Paris 2024 奖牌 | Kaggle `berkayalan/paris-2024-olympics-medals` |
| FIFA 球员评分 | Kaggle `stefanoleone992`（SoFIFA 快照，07–14 + 18–21） |
| NBA 生涯数据 | Kaggle `drgilermo`（1950 起） |
| 中国奥运冠军 | 中文维基百科「中国奥运冠军列表」+ 国家体育总局口径整理 |
| 国际传奇 | TopEndSports / ESPN 百大运动员榜整理 |
| 人物照片 | 百度图片搜索抓取（版权属原发布方，仅用于学习交流） |

**口径说明**：中国数据采用官方「夺金时刻」口径（2008 年按夺金时点计 51 金，其中 3 枚后因兴奋剂
取消，已在数据中标注）；FIFA 曲线缺 2015/2016/2022/2023 年份（镜像源未覆盖），前端已做平滑连接。

## 八、声明

本项目为学习交流作品。人物照片来自互联网公开渠道，版权归原作者所有；数据来自上述公开数据集与
权威媒体整理，图表与文字内容在加工中力求准确，如有出入以官方发布为准。
