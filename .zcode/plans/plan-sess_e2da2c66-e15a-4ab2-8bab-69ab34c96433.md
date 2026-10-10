# 体育人物与体育精神交互系统 — 执行计划

## 已确认的决策
- **数据集**：全量组合 = 奥运统计（1896–2024）+ 中国奥运冠军人物卡 + 足球（FIFA）+ 篮球（NBA）+ 国际传奇人物卡
- **技术栈**：Python(Anaconda) 做数据清洗与 PyTorch 计算 → 产出 JSON；前端 HTML/JS + ECharts；GitHub Pages 免费公网部署
- **PyTorch**：文本嵌入模型做「寻找精神同类」相似运动员推荐（向量离线算好，前端余弦相似度实时匹配，保持纯静态部署）
- **UI**：展示体育明星时使用 ring-gallery（环形画廊）、coverflow-stage（封面流）、design-taste-frontend（反模板设计）三个技能
- **工作流**：每个阶段的方案先解释、你确认后再动手；zcode.md 详细记录全部需求

## 阶段 1：项目文档 + Git 管理（先做）
1. 创建 `zcode.md`：完整记录主题、全国比赛水平要求、公网部署要求、数据集决策、技术栈决策、三个 UI skills 使用要求、"每个方案由你确认"的工作流、各阶段进度
2. `git init` + `.gitignore`（排除原始大数据文件、`__pycache__`、venv 等）+ 首次提交；此后每阶段结束 commit 一次，确保代码不丢失
3. 本地 Git 完成后，用 git-save 技能推送 GitHub 远程仓库（届时需要你的 GitHub 账号配合创建远程仓库）

## 阶段 2：数据获取与清洗（Python 脚本，产出 JSON）
| 板块 | 数据源 | 产物 |
|---|---|---|
| 奥运统计 | GitHub KeithGalli/Olympics-Dataset（1896–2022，免账号直下）+ Paris 2024 奖牌数据 | 奖牌趋势、国家对比、项目分布、中国历届成绩 |
| 中国冠军人物卡 | 中文维基"中国奥运冠军列表"（1984 许海峰→2024，约 300+ 位）+ 维基共享资源抓照片 | 每人：姓名/性别/项目/届次/生平/体育精神标签/照片 |
| 足球 | Kaggle FIFA 15–23 球员数据集（stefanoleone992 版） | 梅西/C罗/姆巴佩等 20–30 位巨星逐年评分曲线 |
| 篮球 | Kaggle drgilermo NBA 1950 起数据（或 GitHub 镜像） | 乔丹/詹姆斯/科比等 20–30 位巨星生涯曲线 |
| 国际传奇人物卡 | TopEndSports/ESPN 百大榜 + Wikidata 抓照片生平 | 20–40 位（博尔特/菲尔普斯/阿里/费德勒…） |
| 体育精神专题 | 冠军事迹整理 | 女排精神、乒乓统治力、首金故事等主题线 |

风险与备选：Kaggle 下载需 Kaggle 账号（免费注册）+ API token——若不方便，改用 GitHub 镜像；维基抓取遇网络问题改用维基 API 国内可达端点。所有抓取脚本可重跑、数据入库前给你过目。

## 阶段 3：PyTorch「精神同类」推荐模块
- 用 sentence-transformers 中文多语言模型把人物卡（生平+成就+精神标签）编码为向量
- 交互：访问者勾选欣赏的品质（坚韧/突破/团队/天赋…），实时匹配"精神同类"体育人物
- 全部向量导出 JSON，前端计算相似度，部署形态不变

## 阶段 4：前端网站（先出设计稿，你确认视觉方向后开发）
初步板块：① 首页 Hero（coverflow-stage 封面流巨星）② 奥运百年统计厅（ECharts）③ 中国冠军环形画廊（ring-gallery）④ 足球/篮球巨星曲线厅 ⑤ 体育精神专题 ⑥ 精神同类推荐页。使用 design-taste-frontend 做整体视觉，完成后按视觉验收流程逐页检查。

## 阶段 5：部署与存档
- GitHub Pages 发布公网（若大陆访问速度不理想，备选 Cloudflare Pages，二者都免费）
- git-save 存档推送，交付完整仓库 + 访问链接

## 环境注意
- 目录为中文路径，项目内文件/脚本一律英文命名，避免编码问题
- Python 依赖（pandas/numpy/requests/PyTorch/sentence-transformers）安装到你的 Anaconda 环境