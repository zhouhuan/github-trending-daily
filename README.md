# GitHub Trending Daily

每天自动爬取 GitHub 热门项目，分析热度原因，并通过 Gmail 推送给你。

## 功能特性

- 🌟 **每日 Top 10**: 自动获取 GitHub Trending 当日增长最快的 10 个项目
- 📊 **详细信息**: 包含项目名称、描述、星数、日增数、语言、README 摘要等
- 🔥 **热度解读**: 智能分析项目热门原因（技术突破、新发布、社区讨论等）
- 📧 **邮件推送**: 精美的 HTML 格式邮件，每日定时送达
- ⏰ **自动执行**: 基于 GitHub Actions，每天北京时间早上 9 点自动运行

## 项目结构

```
github-trending-daily/
├── main.py              # 主入口
├── github_trending.py   # GitHub 热门项目爬取
├── news_analyzer.py     # 相关新闻搜索与解读
├── email_sender.py      # 邮件发送 + HTML 模板
├── requirements.txt     # Python 依赖
├── README.md            # 使用说明
└── .github/
    └── workflows/
        └── daily.yml    # GitHub Actions 定时任务配置
```

## 快速开始

### 方式一：Fork 本仓库（推荐）

1. 点击右上角 **Fork** 按钮，将仓库复制到你自己的 GitHub 账号
2. 配置 Secrets（见下方配置说明）
3. 启用 Actions，首次运行可以手动触发

### 方式二：本地运行

```bash
# 克隆仓库
git clone <your-repo-url>
cd github-trending-daily

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@qq.com"
# 可选：GitHub Token，提高 API 请求限额
export GITHUB_TOKEN="your-github-token"

# 运行
python main.py
```

## 配置说明

### 需要配置的 GitHub Secrets

在仓库页面依次点击 **Settings → Secrets and variables → Actions → New repository secret**，添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `GMAIL_USER` | 发件人 Gmail 地址 | `your-email@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail **应用专用密码**（不是登录密码） | `abcdefghijklmnop` |
| `RECIPIENT_EMAIL` | 收件人邮箱 | `recipient@qq.com` |

> 💡 `GITHUB_TOKEN` 不需要手动添加，GitHub Actions 会自动生成。

### Gmail 应用专用密码获取方式

Gmail SMTP 需要使用**应用专用密码**而不是登录密码：

1. 在 Google 账号中开启**两步验证**
2. 在 Google 账号设置中搜索并打开**应用专用密码**
3. 创建一个新的应用专用密码
4. 将生成的 16 位密码填入 `GMAIL_APP_PASSWORD` Secret 中

> ⚠️ 注意：应用专用密码相当于邮箱的专用密码，请不要写入代码或提交到仓库。

## GitHub Actions 配置说明

### 定时规则

默认配置为每天**北京时间早上 9:00** 执行：

```yaml
cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

如需修改时间：
- UTC 时间 = 北京时间 - 8 小时
- Cron 格式：`分 时 日 月 周`

### 手动触发

在仓库的 **Actions** 页面：
1. 选择 **GitHub Trending Daily** 工作流
2. 点击 **Run workflow** → **Run workflow** 即可立即执行

## 技术实现

### 数据来源

- **Trending 列表**: 抓取 `github.com/trending?since=daily` 页面
- **项目详情**: 通过 GitHub REST API v3 获取
- **README 摘要**: 通过 GitHub API 获取并解析 README
- **热度分析**: 综合项目数据、Hacker News 讨论、技术标签等多维度分析

### 限流处理

- GitHub API 未认证时每小时 60 次请求，使用 Token 后提升至 5000 次/小时
- 代码中内置了请求间隔和限流重试逻辑
- 每日仅爬取 10 个项目，API 请求量很小

### 邮件格式

- 使用纯 HTML + CSS 内联样式，兼容各种邮件客户端
- 响应式设计，手机端也能良好显示
- 包含项目卡片、热度解读、README 摘要等信息

## 常见问题

### Q: 邮件收不到怎么办？

A: 请检查：
1. Gmail 应用专用密码是否正确（注意不是登录密码）
2. 收件人邮箱是否正确
3. 是否被归类到垃圾邮件
4. Actions 运行日志是否有错误信息

### Q: GitHub Actions 运行失败怎么办？

A: 在仓库的 **Actions** 页面查看具体失败日志，常见原因：
- Secrets 未配置或配置错误
- 网络问题导致无法访问 GitHub Trending 页面
- Gmail SMTP 认证失败

### Q: 可以修改推送的项目数量吗？

A: 可以，修改 `main.py` 中的 `get_top_projects(top_n=10)` 参数即可。

### Q: 可以修改推送时间吗？

A: 可以，修改 `.github/workflows/daily.yml` 中的 cron 表达式。

## 许可证

MIT License
