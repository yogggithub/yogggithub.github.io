# Personal Blog with Hugo & PaperMod

基于 Hugo 和 PaperMod 主题的个人博客，采用 Profile 模式展示，包含观影记录模块，管理 2200+ 条影视记录。

## ✨ 特性

- � **Profile 模式** - 个人主页展示，突出社交媒体链接
- 📽️ **观影记录** - 管理 2200+ 条电影/电视剧记录
- 🎨 **响应式设计** - 基于 PaperMod 主题的现代化界面
- 🌍 **双语支持** - 中文（默认）和英文界面
- 🔍 **全站搜索** - 支持内容快速检索
- 🖼️ **图片画廊** - 展示相册内容
- 🚀 **双平台部署** - GitHub Pages + Cloudflare Pages

## 🚀 快速开始

### 环境要求

- Hugo Extended v0.152.2+
- Git（用于主题子模块）

### 安装 Hugo

```bash
# Windows (使用 Chocolatey)
choco install hugo-extended

# macOS (使用 Homebrew)
brew install hugo

# Linux
snap install hugo --channel=extended
```

### 克隆项目

```bash
git clone --recurse-submodules https://github.com/yogggithub/yogggithub.github.io.git
cd yogggithub.github.io
```

### 启动开发服务器

```bash
hugo server -D
```

访问 http://localhost:1313

## 📁 项目结构

```
yogggithub.github.io/
├── .github/
│   └── workflows/       # GitHub Actions 部署配置
├── archetypes/          # 内容模板
├── assets/              # 主题资源
├── content/             # 内容文件
│   ├── posts/          # 博客文章
│   ├── watched/        # 观影记录（2237个markdown文件）
│   │   ├── imdb/       # IMDb 来源
│   │   └── douban/     # 豆瓣来源
│   ├── gallery/        # 相册
│   ├── archives.md     # 归档页面
│   └── search.md       # 搜索页面
├── layouts/             # 自定义布局（可选）
├── static/              # 静态资源
│   ├── logo.png        # 网站 Logo
│   └── favicon.png     # 网站图标
├── themes/
│   └── PaperMod/       # Git 子模块
├── hugo.toml           # Hugo 配置文件
└── README.md
```

## 🎯 核心功能

### 1. Profile 模式首页

- 展示个人头像和简介
- 快速导航按钮（文章、相册、影评、归档、搜索）
- 社交媒体图标（GitHub、Twitter、Email、Telegram、Buy Me a Coffee、PayPal）

### 2. 观影记录模块

**数据规模：** 2237 条记录
- IMDb 来源
- 豆瓣来源

**URL 结构：**
- 使用 Permalink 自动生成：`/watched/:contentbasename/`
- 示例：`tt28996126.md` → `/watched/tt28996126/`

**特点：**
- 所有记录使用独立 Markdown 文件
- 支持 Frontmatter 元数据
- 自动化 URL 生成，无需手动维护

### 3. 多语言支持

- **中文（默认）**：`/`
- **英文**：`/en/`
- 独立的菜单配置和内容目录

### 4. 搜索功能

- 基于 Fuse.js 的客户端搜索
- 支持文章、页面全文检索
- 响应式搜索界面

## 📝 配置说明

### 主要配置（hugo.toml）

```toml
baseURL = "https://yogggithub.github.io/"
defaultContentLanguage = "zh"
theme = "PaperMod"

[params]
  env = "production"
  ShowReadingTime = true
  ShowBreadCrumbs = true
  ShowCodeCopyButtons = true

  [params.profileMode]
    enabled = true
    title = "Your Name"
    subtitle = "欢迎来到我的个人网站 👋"
    imageUrl = "/logo.png"
    buttons = [
      {name = "文章", url = "/posts/"},
      {name = "相册", url = "/gallery/"},
      {name = "影评", url = "/watched/"},
      {name = "归档", url = "/archives/"},
      {name = "搜索", url = "/search/"}
    ]

# Permalink 配置 - 自动化 URL 生成
[permalinks.page]
  watched = "/watched/:contentbasename/"
```

### 社交图标配置

PaperMod 主题支持 141 种社交网络图标，包括：

- **开发者平台**：github, gitlab, stackoverflow
- **社交媒体**：twitter, facebook, instagram, telegram
- **中文平台**：douban（豆瓣）, bilibili, zhihu, juejin
- **资助平台**：buymeacoffee, kofi, patreon, paypal
- 更多：详见 `themes/PaperMod/layouts/partials/svg.html`

## 🔧 内容管理

### 添加博客文章

```bash
hugo new posts/my-post.md
```

### 添加观影记录

1. 在 `content/watched/imdb/` 或 `content/watched/douban/` 创建 Markdown 文件
2. 文件名即为 URL（如 `tt1234567.md` → `/watched/tt1234567/`）
3. 编辑 Frontmatter：

```yaml
---
title: "电影标题"
date: 2025-11-09T10:00:00+08:00
draft: false
---

影评内容...
```

### 批量管理

使用提供的 PowerShell 脚本批量操作：

```powershell
# 批量移除 watched 记录中的 url 字段
.\remove_url_from_watched.ps1
```

## 🌐 部署

### GitHub Pages

项目已配置 GitHub Actions 自动部署：

1. 推送到 `master` 分支
2. GitHub Actions 自动构建
3. 部署到 `gh-pages` 分支
4. 访问：https://yogggithub.github.io/

### Cloudflare Pages

1. 在 Cloudflare Pages 连接 GitHub 仓库
2. 配置构建设置：
   - **Framework preset**: Hugo
   - **Build command**: `hugo --minify`
   - **Build output directory**: `public`
   - **Environment variables**: `HUGO_VERSION=0.152.2`
3. 设置环境变量覆盖 baseURL：
   - `HUGO_BASEURL=https://yourdomain.xyz/`

### URL 配置说明

- **GitHub Pages**: 使用 `hugo.toml` 中的 `baseURL`
- **Cloudflare Pages**: 使用环境变量 `HUGO_BASEURL` 覆盖
- **菜单链接**: 使用绝对路径（以 `/` 开头），确保跨平台兼容

## 🛠️ 技术栈

- **生成器**: Hugo Extended v0.152.2
- **主题**: PaperMod（Git 子模块）
- **部署**: GitHub Actions + GitHub Pages / Cloudflare Pages
- **搜索**: Fuse.js（客户端搜索）
- **图标**: PaperMod 内置 SVG 图标（141 种）

## 🔍 关键技术决策

### Permalink 自动化

**问题**：2237 个 watched 页面，每个都需要手动配置 URL

**解决方案**：
```toml
[permalinks.page]
  watched = "/watched/:contentbasename/"
```

- 文件名即 URL，无需 Frontmatter 中的 `url` 字段
- 支持子目录结构（imdb/douban）
- URL 始终为 `/watched/文件名/`

### 双平台部署

**问题**：不同平台需要不同的 baseURL

**解决方案**：
- GitHub Pages：使用 `hugo.toml` 的 `baseURL`
- Cloudflare Pages：使用 `HUGO_BASEURL` 环境变量覆盖
- 菜单使用绝对路径（`/posts/`），避免 URL 拼接问题

### Git 子模块管理

PaperMod 主题作为 Git 子模块：

```bash
# 初始化子模块
git submodule update --init --recursive

# 更新主题
git submodule update --remote --merge
```

## 📊 项目统计

- **观影记录**: 2237 条
- **支持语言**: 2 种（中文、英文）
- **社交图标**: 141 种可选
- **部署平台**: 2 个（GitHub Pages + Cloudflare Pages）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 🔗 相关链接

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [PaperMod 主题](https://github.com/adityatelange/hugo-PaperMod)
- [PaperMod Wiki](https://github.com/adityatelange/hugo-PaperMod/wiki)

---

**Powered by Hugo & PaperMod** 🚀
