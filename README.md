# Wei Long · Academic Homepage

英文为主的学术个人主页，使用纯 HTML、CSS 和 JavaScript。字体和视觉资源在本地加载，无需 npm、CDN 或数据库；Python 仅用于从资料生成静态页面。

## 本地预览

在项目目录运行：

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8766 --bind 127.0.0.1 --directory dist
```

然后打开 <http://localhost:8766>。修改资料后重新生成并检查，再刷新页面；`Ctrl+C` 停止服务器。如果端口已被其他项目占用，请换一个端口，不要停止其他项目的服务。

也可以直接用浏览器打开 `dist/index.html`，无需启动服务器或联网。页面正文、论文筛选和 BibTeX 展开都可离线使用；如果浏览器不允许复制到剪贴板，复制按钮会选中文本，按 `Ctrl+C` / `Cmd+C` 即可。

运行 `python3 scripts/export.py` 可在项目的上一级目录更新单文件预览 `wei-long-preview.html` 和完整源码压缩包 `academic-homepage.zip`。

## 更新个人资料

编辑 `data/profile.json` 和 `data/publications.json`，然后重新生成网站。构建脚本同时生成本地预览用的 `dist/index.html` 和 GitHub Pages 用的根目录 `index.html`；不要直接修改这两个生成文件，下次生成会覆盖它们。

| 文件或字段 | 用途 |
| --- | --- |
| `data/profile.json` | 姓名、身份、单位、简介、联系方式与主页链接 |
| `data/publications.json` | 论文标题、作者、年份、会议、简介及论文/代码/项目链接 |
| `email` | 希望公开的联系邮箱；未提供时留空 |
| `groupUrl`、`institutionUrl` | 简介中课题组与学校的链接 |
| `advisorName`、`advisorUrl` | 导师姓名及个人主页；简介中的同名文本会自动加链接 |
| `photo` | 个人照片的本地资源路径；未提供时留空 |
| `cv` | 简历 PDF 的本地资源路径；未提供时留空 |
| `siteUrl` | 正式上线后填写实际网站根地址 |
| `dist/` | 可直接部署的静态网站 |
| 根目录 `index.html` | GitHub Pages 的入口，引用 `dist/assets/` 下的资源 |

照片可放在 `dist/assets/portrait.jpg`，并把 `photo` 填为 `assets/portrait.jpg`；简历同理放在 `dist/assets/cv.pdf`，`cv` 填为 `assets/cv.pdf`。两项为空时自动隐藏。当前头像来自本人 Scholar，论文配图来自作者官方仓库；来源见 `data/figure-sources.json`。没有真实配图的论文使用纯文字排版。

布局样式在 `dist/assets/site.css`，交互在 `dist/assets/site.js`，页面结构在 `scripts/build.py`。更改姓名时也请同步更新 `dist/assets/favicon.svg`。

公开上线前，请核对姓名、单位、简介、论文作者顺序和发表状态。已知 GitHub 为 [gitlonglong](https://github.com/gitlonglong)，Scholar 链接已提供。

当前已使用你确认的 **UESTC 博士生**身份、**lwsch5940@163.com** 邮箱和 **gitlonglong** 账号。公开资料来源与未核实信息见 `SOURCES.md`。

- **已具备核心资料：** 姓名、身份、单位、公开邮箱、GitHub、Scholar、研究方向、本人头像及 17 篇论文；已按本人要求排除指定的人脸识别论文。
- **推荐补充：** 更高分辨率头像、个人简历 PDF、其余论文的配图。
- **可选内容：** 中文姓名、导师、教育经历、实习经历、获奖、学术服务和新闻动态。

缺失信息先留空，不会用虚构经历或联系方式填充。不要把密码、访问令牌或其他私密信息写进资料文件。

## 论文列表与更新

2026-11-04 读取的 Scholar 页面显示 `Articles 1–18`，且 `Show more` 按钮禁用；已核对全部 18 个详情页。快照记录在 `data/scholar-snapshot.json`，原始论文标题、年份、作者与 Scholar ID 保留在数据中。

历史快照保留原始 18 条记录；当前主页显示 17 篇。本人要求移除的条目记录在 `data/publication-exclusions.json`，同步 Scholar 时应继续排除，避免重新加回。

主页先分为一作／共同一作和其他作者位次两组，各组内按正式发表年份排列。分组由 `authors` 的作者顺序和 `equalContribution` 的已核实共同一作信息决定；与第一位作者共享贡献标记才会归入共同一作，不把普通第二作者当作共同一作。

例如 ICLR 2026 的论文在 Scholar 上可能记为 2025 年预印本，页面另显示初次发表年份。PFT 的 CVPR 2025 版本与 IJCV 2026 扩展版分别列出，未经核实接收的预印本仅标为 arXiv。已确认的共同一作用 `*` 标注。

新增论文时编辑 `data/publications.json`，然后运行 `python3 scripts/build.py` 和 `python3 scripts/check.py`。如重新同步 Scholar，请同时更新快照；检查脚本会防止误删已收录的 Scholar 条目。

Publications 前的 **News** 来自 `data/news.json`，目前覆盖全部 14 篇已接收论文，不把 3 篇纯预印本写为已接收。每项包含接收月份 `date`（`YYYY-MM` 或 `null`）、关联论文 `paperIds`、显示简称 `labels`、会议／期刊 `venue` 和日期依据 `sources`、`dateBasis`。同月同会议的论文可以合为一条动态。

有作者公告或出版社接收记录的月份直接显示；根据官方会议通知日期整理的月份标记 `†`，并提供说明。尚未查到月份的 6 篇期刊论文列在可展开的“More acceptances”中，不以出版日期或 arXiv 上传日期代替接收日期。收到本人确认的日期后可填写 `date` 并更新依据。

## BibTeX 与来源

17 篇论文均于 2026-11-04 重新审核：会议论文使用正式论文集，期刊论文使用出版社或 Crossref 的出版商登记记录，纯预印本使用 arXiv 官方导出。逐篇来源和修正说明见 `data/citation-audit.json`。未确认的 DOI 等字段不猜填，引用键保持不变。

页面内每篇论文的 BibTeX、复制结果和完整下载均来自 `data/publications.json` 的同一字段。生成的 `publications.bib` 与 `dist/publications.bib` 内容一致，收录全部 17 篇。本轮已用 Pybtex 解析并实际格式化渲染，检查了标题、作者顺序、年份、DOI、重复键和重音字符。Pybtex 只用于这次审计，网站本身没有新增运行依赖。

## GitHub Pages 发布与更新

**不需要申请域名，也不需要购买服务器。** 已创建公开仓库 [gitlonglong/gitlonglong.github.io](https://github.com/gitlonglong/gitlonglong.github.io)，主页地址为 <https://gitlonglong.github.io/>。GitHub 免费账号可用公开仓库托管 GitHub Pages。[GitHub 官方创建指南](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)

仓库使用 GitHub 内置的分支发布：**Settings → Pages → Build and deployment → Source → Deploy from a branch**，分支选 **main**，目录选 **/(root)**。根目录的 `index.html` 是正式入口；根目录 `.nojekyll`、`robots.txt`、`sitemap.xml` 也由构建脚本生成。`siteUrl` 应填写正式主页地址。

每次更新资料或样式后，在项目目录执行：

```bash
python3 scripts/build.py
python3 scripts/check.py
git add data scripts dist index.html .nojekyll robots.txt sitemap.xml publications.bib SOURCES.md README.md .github
git commit -m "Update academic homepage"
git push origin main
```

提交前可用 `git diff --cached` 核对修改。源码、静态资源和生成页面需要一起提交；**只修改数据文件并推送，不会重新生成线上页面。** 仓库内的自定义工作流仅检查生成结果是否与数据一致，不负责部署。正式发布由 GitHub 内置的 `pages build and deployment` 完成，保留这一种发布方式即可。

推送后等待内置发布任务成功，再通过 **Settings → Pages → Visit site** 打开网站，核对手机布局和外链。发布可能需要几分钟；如果页面仍旧，刷新浏览器缓存后重试。整个流程不需要把 GitHub 密码交给助手。

## 是否购买个人域名

先使用免费的 `github.io` 地址即可。以后如需更独立的个人品牌，可自行购买域名，再在 GitHub Pages 中配置 Custom domain 和域名服务商的 DNS；通常无需修改页面设计。域名需要按注册商规则续费。[GitHub 自定义域名指南](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)

网站打开时不加载外部字体、脚本库或远程图片，因此页面本身不依赖这些服务的连通性。点击 Scholar、GitHub 或论文链接仍需要访问对应网站；GitHub Pages 在不同网络环境下的访问体验也可能不同。
