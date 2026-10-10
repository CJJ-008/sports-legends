# 体育人物与体育精神交互系统 — 项目需求与决策记录

> 本文件是项目的**唯一需求与决策档案**。所有需求、数据集决策、技术栈决策、工作流约定都记录在此，每阶段完成后更新进度。最后更新：2026-10-10

---

## 一、项目概述

- **主题**：体育人物与体育精神
- **形态**：交互式图表网页（体育明星交互展示 + 数据可视化）
- **水平要求**：按**全国比赛水平**制作（作品完整度、视觉设计、技术亮点均按国家级赛事标准）
- **部署要求**：**部署在公网**，任何人的电脑通过浏览器即可打开访问
- **防丢失要求**：全程 Git 管理，每阶段提交存档，避免代码丢失

## 二、原始需求清单（用户提出）

1. 主题：体育人物与体育精神
2. 交互式图表网页，关于体育明星
3. 网页部署在公网，别人的电脑能打开
4. 按全国比赛水平生成
5. 数据集从全网找，**候选方案列出后由用户选择** ✅ 已完成（见下）
6. 技术栈：Python、numpy、PyCharm + Anaconda 环境、可使用 PyTorch；其余技术栈由助手选型（需向用户解释并经确认）
7. 电脑已装 Git：项目加入 Git 管理存档
8. UI 设计技能：展示体育明星、做 UI 设计时，必须使用 **ring-gallery**、**coverflow-stage**、**design-taste-frontend** 三个技能
9. **每个要采用的方案都向用户解释一遍，由用户做决定**

## 三、已确认的决策（2026-10-10 用户选定）

### 决策 1：数据集组合 —— 「全都要」方案
| 板块 | 数据源 | 用途 |
|---|---|---|
| 奥运统计 | GitHub `KeithGalli/Olympics-Dataset`（1896–2022，免账号直下）+ Paris 2024 奖牌数据 | 奖牌趋势、国家对比、项目分布、中国历届成绩图表 |
| 中国奥运冠军人物卡 | 中文维基百科「中国奥运冠军列表」（1984 许海峰 → 2024 巴黎，约 300+ 位）+ 维基共享资源照片 | 自建人物卡：姓名/性别/项目/届次/生平/体育精神标签/照片 |
| 足球 | Kaggle FIFA 15–23 完整球员数据集（stefanoleone992 版，1.8 万球员×110+ 属性） | 梅西/C罗/姆巴佩等 20–30 位巨星逐年评分曲线 |
| 篮球 | Kaggle `drgilermo` NBA Players stats since 1950（或 GitHub 镜像） | 乔丹/詹姆斯/科比等 20–30 位巨星生涯曲线 |
| 国际传奇人物卡 | TopEndSports / ESPN 百大榜 + Wikidata 照片生平 | 20–40 位（博尔特/菲尔普斯/阿里/费德勒…） |
| 体育精神专题 | 冠军事迹整理 | 女排精神、乒乓统治力、首金故事等主题线 |

> 备注：全网不存在现成的「体育明星人物卡」数据集（含照片+事迹+精神故事），人物层全部用 Python 抓取自建 —— 自建数据集本身是比赛加分项。

### 决策 2：技术栈与部署 —— 静态页 + ECharts + GitHub Pages
- **Python(Anaconda)**：数据下载、抓取、清洗（pandas/numpy），PyTorch 离线计算向量，产出全部为 JSON
- **前端**：HTML/JS + Apache ECharts 图表库，无后端
- **部署**：GitHub Pages（免费、公网、秒开、零运维）；若大陆访问速度不理想，备选 Cloudflare Pages

### 决策 3：PyTorch 角色 —— 「寻找精神同类」推荐
- 用 sentence-transformers 中文多语言嵌入模型，把人物卡（生平+成就+精神标签）编码为向量
- 交互：访问者勾选欣赏的品质（坚韧/突破/团队/天赋…），前端用余弦相似度实时匹配「精神同类」体育人物
- 向量离线导出 JSON，**部署形态保持纯静态**

## 四、UI 技能使用要求（强制）

以下三个技能在对应场景**必须使用**：

| 技能 | 使用场景 |
|---|---|
| `ring-gallery` | 中国奥运冠军环形画廊展示（3D 环形旋转、拖拽旋转画廊） |
| `coverflow-stage` | 首页巨星封面流 / 沉浸式电影感主视觉 |
| `design-taste-frontend` | 整站 UI 设计（反模板味、真实设计系统、落地页与重设计流程） |

## 五、网站板块规划（初稿，设计阶段可调整）

1. **首页 Hero** — coverflow-stage 封面流巨星 + 电影感背景
2. **奥运百年统计厅** — ECharts：奖牌趋势、国家对比、项目分布、中国历届成绩
3. **中国冠军环形画廊** — ring-gallery：300+ 位奥运冠军人物卡
4. **足球/篮球巨星曲线厅** — FIFA 评分曲线、NBA 生涯曲线对比（折线/雷达）
5. **体育精神专题** — 女排精神、乒乓统治力、首金故事等主题叙事
6. **精神同类推荐页** — PyTorch 向量匹配交互

## 六、工作流约定（用户核心要求）

- **每个要采用的方案先向用户解释，用户确认后再动手**
- 数据入库前给用户过目
- 阶段 4 开发前先出设计方向，用户确认视觉后再开发
- 每阶段结束：更新本文件进度 + git commit 存档

## 七、阶段进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1 | zcode.md + git 初始化 | ✅ 完成（2026-10-10） |
| 2 | 数据获取与清洗（6 个板块 → JSON） | ✅ 完成（FIFA 覆盖 07–14+18–21，缺 15/16/22/23 年份） |
| 3 | PyTorch「精神同类」推荐模块 | ✅ 完成（376 人 × 384 维嵌入 + 八大品质） |
| 4 | 前端网站开发 | ✅ 完成（六页站，已通过截图视觉验收） |
| 5 | 公网部署 + git 存档推送 | ⏸ 用户决定：先本地预览（http://localhost:8765），部署随时可做 |

### 网站结构（site/，暗夜冠军·史诗风）
| 页面 | 内容 | 核心技能 |
|---|---|---|
| index.html | 封面流首页（32 传奇轮播 + 统计 + 展厅入口） | coverflow-stage |
| olympics.html | 奥运百年统计厅（7 张 ECharts 图） | — |
| champions.html | 中国冠军环形画廊（14 张胶片卡拖拽旋转 + 详情面板） | ring-gallery |
| stars.html | 巨星曲线厅（FIFA 评分 + NBA 生涯曲线） | — |
| spirit.html | 体育精神专题（10 主题编辑式排版） | design-taste-frontend |
| match.html | 精神同类推荐（品质选择 + 余弦相似度实时匹配） | — |

### 已知数据口径与边界
- 中国数据 =「夺金时刻」口径（2008 记 51 金含 3 枚后被取消，已打 doping_dq 标注；国际统计为 1896–2022 快照）
- FIFA 曲线缺 2015/2016/2022/2023 年份（镜像源未覆盖），前端曲线已做平滑连接；如需补全可注册 Kaggle 免费账号下载官方 FIFA 15–23 数据集后重跑 `scripts/build_fifa_curves.py`
- 照片来自百度图片搜索抓取（学习交流用途），23 位冠军无照片时前端用首字母渐变卡兜底

### 数据资产清单（data/clean/）
| 文件 | 内容 | 状态 |
|---|---|---|
| olympics/*.json（8 个） | 奖牌总榜/中国逐届/国家趋势/项目分布/女子演进/参赛人数 | ✅ 已对齐官方 |
| photos/（352 张 + manifest） | 冠军 321/344 + 传奇 32 张人像（百度图片搜索抓取） | ✅ 23 位失败者前端用首字母卡兜底 |
| champions master（staging） | 327 金 344 人，与体育总局官方逐届金牌数完全一致 | ✅ |
| legends.json | 32 位国际传奇（生平/成就/名言/精神标签/照片） | ✅ |
| spirit_themes.json | 10 个体育精神专题（女排精神/首金时刻/中国速度…） | ✅ |
| nba/star_curves.json | 25 位 NBA 巨星生涯曲线（1950–2017） | ✅ |
| fifa/star_curves.json | 28 位足球巨星评分曲线（FIFA 07–14） | 🚧 补 18/19/20/21 下载中 |
| spirit_match.json | 376 人画像 + 六维精神指标 + 384 维嵌入 | ✅ |

### 数据说明（口径）
- 中国冠军数据 =「夺金时刻」口径（2008 记 51 金含后来因兴奋剂取消的 3 金，已在数据中打 `doping_dq` 标记；2012 记 38 金为递补前口径）。前端将加注说明。
- 奥运国际统计 = GitHub KeithGalli 数据集（1896–2022 快照），已剔除青奥会、按「赛事×国家」去重，与中国官方数字对齐。
- 照片版权提示：人物照片来自百度图片搜索抓取（版权属原发布方），比赛作品属非商业教育用途，展示页将标注「图片来源网络，仅用于学习交流」；如比赛要求严格，可替换为手绘/授权图。

## 八、环境注意事项

- 工作目录为中文路径 `E:\体育人物及精神交互系统`，**项目内文件/脚本一律英文命名**，避免编码问题
- Python 环境使用用户的 Anaconda（PyCharm 中已部署），依赖：pandas、numpy、requests、PyTorch、sentence-transformers
- Kaggle 数据集下载需 Kaggle 账号 + API token；若无则改用 GitHub 镜像
- 维基百科抓取遇网络问题改用维基 API 备用端点
- 原始大数据文件不入 Git（.gitignore 排除 `data/raw/`），只保留清洗后的 JSON 成品

## 九、数据源链接存档

- 奥运 1896–2022：https://github.com/KeithGalli/Olympics-Dataset
- 奥运 1896–2016（经典版）：https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results
- Paris 2024 奖牌：https://www.kaggle.com/datasets/berkayalan/paris-2024-olympics-medals
- FIFA 15–23 球员：https://www.kaggle.com/datasets/stefanoleone992 （FIFA 23 版：cashncarry）
- NBA 1950 起：https://www.kaggle.com/datasets/drgilermo ；1996–2022 版：https://www.kaggle.com/datasets/justinas
- 中国奥运冠军列表（维基）：zh.wikipedia.org/wiki/中国奥运冠军列表
- 百大运动员榜：topendsports.com / espn.com

## 十、部署待办（用户就绪后执行）
1. 用户在 github.com/new 创建空仓库（Public），地址发给助手
2. `git remote add origin <地址>` → `git push -u origin main`
3. `git subtree push --prefix=site origin gh-pages`（或用 GitHub Pages 设置指向 /site）
4. 仓库 Settings → Pages → Branch 选 gh-pages → Save
5. 公网地址：https://<用户名>.github.io/<仓库名>/
6. 若大陆访问慢：Cloudflare Pages 连接同一仓库一键镜像（免费）

本地预览：在 site/ 目录运行 `python -m http.server 8765` → http://localhost:8765
