# TrendRadar Market Signal Edition

这是基于 upstream TrendRadar 的自定义部署版，目标不是浏览泛新闻热榜，而是把网页变成一个偏政治、财经、科技和全球股票市场的早期信号面板。

当前版本基于 TrendRadar `6.6.2` / MCP `4.0.4`，保留 upstream 的 Docker、RSS、HTML 报告、AI 分析和 MCP 能力，同时加入了本仓库的筛选、去重和部署优化。

## 我们做过的优化

### 市场相关内容优先

默认关注以下方向：

- 政治和政策风险：中美关系、制裁、关税、出口管制、台海、俄乌、中东、监管法案等。
- 全球市场信号：美股、A 股、港股、日股、债券、汇率、商品、VIX、央行、通胀、就业、PMI 等。
- 科技和半导体：AI、大模型、GPU、芯片、台积电、ASML、英伟达、AMD、数据中心、电力约束等。
- 上市公司事件：财报、指引、评级、并购、回购、减持、债务、做空报告、监管问询、重大诉讼等。
- 早期异常信号：传闻、待核实爆料、盘前/盘后异动、期权异动、供应中断、突袭检查、传票、调查等。

体育、娱乐、明星、综艺、景区旅游、普通民生、情感八卦等默认过滤，除非它们直接影响上市公司、监管政策或资产价格。

### 更少重复新闻

本仓库新增了标题级去重逻辑：

- 热榜、新增、RSS、独立展示区之间做全页面去重。
- 相似标题会合并来源，并在页面中显示合并来源信息。
- 过滤掉同一事件在多个新闻源反复出现造成的刷屏。

相关实现：

- `trendradar/report/dedupe.py`
- `trendradar/report/generator.py`
- `trendradar/report/html.py`
- `tests/test_report_dedupe.py`

### 网页查看优先

当前部署默认不配置通知渠道，只生成 HTML 页面供浏览器查看。页面会由后台定时任务更新，打开后手动刷新即可看到最新报告。

默认本地访问地址：

```bash
http://127.0.0.1:18177/index.html
```

## 当前部署默认值

本仓库的 Docker 部署使用不常用端口：

| 服务 | 绑定 | 说明 |
| --- | --- | --- |
| Web 页面 | `0.0.0.0:18177` | 浏览器查看报告 |
| MCP 服务 | `127.0.0.1:18337` | 仅本机访问 |

默认运行方式：

- `RUN_MODE=cron`
- `CRON_SCHEDULE=*/12 * * * *`
- `IMMEDIATE_RUN=true`
- 通知关闭，仅网页查看
- AI 分析使用 Gemini
- 主筛选方式为关键词筛选，不启用 AI 筛选

本地密钥和端口配置放在 `docker/.env.local`，该文件不应提交到 Git。

## 快速启动

```bash
cd docker
docker compose --env-file .env.local -p trendradar -f docker-compose-build.yml up -d --build
```

查看状态：

```bash
docker compose --env-file .env.local -p trendradar -f docker-compose-build.yml ps
```

查看日志：

```bash
docker compose --env-file .env.local -p trendradar -f docker-compose-build.yml logs --tail=120 trendradar
```

手动跑一轮抓取和报告生成：

```bash
docker compose --env-file .env.local -p trendradar -f docker-compose-build.yml exec -T trendradar python -m trendradar
```

## 关键配置文件

| 文件 | 用途 |
| --- | --- |
| `config/config.yaml` | 数据源、报告模式、展示区域、AI 分析、存储、通知等主配置 |
| `config/frequency_words.txt` | 关键词分组和全局过滤词 |
| `config/ai_interests.txt` | AI 兴趣描述，用于说明关注方向 |
| `config/ai_analysis_prompt.txt` | AI 分析提示词，强调弱信号和信息差 |
| `docker/.env.local` | 本地端口、运行模式、API Key 等私密运行配置 |

注意：`docker/.env.local`、`output/`、SQLite 数据库、日志、生成的 HTML 报告都不应推送到公开仓库。

## 数据源策略

热榜源保留相对有用的综合、财经和讨论源，例如：

- 百度热搜
- 华尔街见闻
- 澎湃新闻
- 财联社热门
- 知乎

RSS 增加了偏市场和早期信号的来源，例如：

- Yahoo Finance
- WSJ Markets
- SEC Press Releases
- Federal Reserve
- CNBC Markets / CNBC World
- TechCrunch
- The Register
- Google Market Signals
- Google Regulatory Shocks
- Google Short & Activist Signals
- Google Chip Supply Signals
- Google Geopolitics Markets

这些 RSS 查询主要用于捕捉监管、做空、激进投资者、半导体供应链、AI 数据中心、地缘政治和全球资产价格相关信息。

## 开发与验证

安装依赖：

```bash
uv sync
```

运行测试：

```bash
uv run python -m unittest discover -s tests
```

语法检查：

```bash
uv run python -m compileall trendradar mcp_server
```

本地运行一轮：

```bash
uv run python -m trendradar
```

## 隐私与安全

- 不要提交任何 API Key、Webhook、通知 Token、邮箱密码或 S3 密钥。
- 不要提交 `docker/.env.local`。
- 不要提交 `output/` 下生成的 HTML、RSS、SQLite 数据库或日志。
- 推送前建议检查：

```bash
git status --short
git diff --check
git diff origin/master..HEAD | rg -n "sk-|AIza|webhook|api_key|secret|token|password" || true
```

## 与 upstream 的关系

本仓库是 `sansan0/TrendRadar` 的自定义 fork。上游负责通用功能演进；本 fork 主要维护以下本地目标：

- 面向股票市场和政策风险的信息筛选。
- 更少重复、更少娱乐化和泛民生噪声。
- Docker 本地部署和网页查看优先。
- 保留本地密钥和生成数据的隐私边界。

合并上游更新时，必须保留本仓库的关键词配置、独立展示区过滤、标题去重和 Docker 端口策略。

## 许可证

沿用 upstream 项目的许可证。请查看 `LICENSE`。
