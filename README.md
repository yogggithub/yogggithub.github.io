# 观影收藏 Hugo 博客

基于 Hugo 和 PaperMod 主题的个人博客，包含专门的观影记录模块。

## ✨ 特性

- 📽️ **海报墙展示** - 响应式网格布局，支持懒加载
- 🎬 **观影记录管理** - 支持电影、电视剧、综艺节目
- ⭐ **多源评分** - 自动获取 IMDb 和豆瓣评分
- 📊 **数据集中管理** - 使用 Hugo Data Files 架构
- 🌍 **双语支持** - 中文和英文界面
- 🚀 **易于部署** - 支持 GitHub Pages 和 Cloudflare Pages

## 🚀 快速开始

### 安装 Hugo

```bash
# Windows (使用 Chocolatey)
choco install hugo-extended

# 或使用 Scoop
scoop install hugo-extended
```

### 启动开发服务器

```bash
hugo server -D
```

访问 http://localhost:1313

## 📁 项目结构

```
my-blog/
├── content/              # 内容文件
│   ├── posts/           # 博客文章
│   ├── watched/         # 观影记录页面
│   └── gallery.md       # 图片画廊
├── data/
│   └── watched.yaml     # 观影数据（Data Files）
├── layouts/
│   └── watched/         # 观影模块模板
│       ├── list.html    # 海报墙
│       └── single.html  # 详情页
├── static/              # 静态资源
├── themes/
│   └── PaperMod/        # 主题
├── docs/                # 📚 项目文档
├── migrate_watched.py   # 数据迁移脚本
├── add_watched.py       # 快速添加记录
├── watched_example.csv  # CSV 模板
└── hugo.toml           # 配置文件
```

## 📚 文档

所有教程和指南位于 `docs/` 目录：

- [快速启动指南](docs/02-quick-start.md) - 立即开始使用
- [海报墙功能指南](docs/04-poster-wall-guide.md) - 海报墙特性说明
- [数据文件指南](docs/05-data-files-guide.md) - Data Files 架构详解
- [CSV 导入指南](docs/06-csv-import-guide.md) - 批量导入数据
- [3000 条记录管理方案](docs/07-managing-3000-records.md) - 大规模数据管理
- [部署指南](docs/01-deployment-guide.md) - 部署到 GitHub/Cloudflare Pages
- [项目总结](docs/03-project-summary.md) - 技术实现说明

## 🎯 核心功能

### 观影记录模块

支持三种内容类型：

- 📽️ **电影** (movie)
- 📺 **电视剧** (tvshow)
- 🎪 **综艺** (variety)

每条记录包含：

- 基本信息（标题、年份、导演、类型）
- 海报图片（支持外部 URL，懒加载）
- 个人评分和评论（支持 Markdown）
- IMDb 和豆瓣评分（自动获取）
- 标签分类

### 数据管理

使用 **Data Files 架构**，所有数据存储在 `data/watched.yaml`：

```yaml
watched:
  - id: "movie-id"
    title: "电影标题"
    year: 2024
    rating: 9
    # ... 其他字段
```

**优势：**

- ✅ 单一数据源，易于备份
- ✅ 支持批量编辑（CSV/Excel）
- ✅ 适合管理大量记录（3000+）
- ✅ Git 友好

## 🔧 使用方法

### 添加观影记录

#### 方法 1：使用脚本（推荐）

```bash
python add_watched.py
```

按提示输入信息，自动更新数据和生成页面。

#### 方法 2：批量导入

1. 准备 CSV 文件（参考 `watched_example.csv`）
2. 运行导入脚本：

```bash
python migrate_watched.py
```

3. 选择 CSV 导入，确认创建内容文件

### 构建网站

```bash
# 开发预览
hugo server -D

# 生产构建
hugo --minify
```

## 🌐 部署

支持多种部署方式：

### Cloudflare Pages（推荐）

```bash
# 推送到 GitHub
git push origin main

# 在 Cloudflare Pages 连接仓库
# 配置：Hugo / hugo --gc --minify / public
```

### GitHub Pages

使用 GitHub Actions 自动部署（参见 [部署指南](docs/01-deployment-guide.md)）

## 🛠️ 技术栈

- **生成器**: Hugo (Extended v0.152.2+)
- **主题**: [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **数据存储**: YAML Data Files
- **API**: OMDb (IMDb) + 豆瓣代理
- **前端**: 原生 JavaScript + CSS Grid
- **图片加载**: Intersection Observer API

## 📝 配置

主要配置在 `hugo.toml`：

```toml
baseURL = "https://your-site.com/"
theme = "PaperMod"
defaultContentLanguage = "zh"

# OMDb API Key（在模板中配置）
# 注册：http://www.omdbapi.com/apikey.aspx
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 🔗 相关链接

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [PaperMod 主题文档](https://github.com/adityatelange/hugo-PaperMod/wiki)
- [OMDb API](http://www.omdbapi.com/)
- [豆瓣电影](https://movie.douban.com/)

---

**开始你的观影记录之旅！** 🎬✨
