# 开发日志

## 项目概览

个人博客网站，基于 Hugo + PaperMod 主题，采用 Profile 模式，包含 2200+ 条观影记录。

## 技术架构

### 核心技术栈

- **静态站点生成器**: Hugo Extended v0.152.2
- **主题**: PaperMod（Git 子模块）
- **部署**: GitHub Pages + Cloudflare Pages
- **版本控制**: Git

### 项目特点

1. **Profile 模式首页** - 个人展示页面，包含头像、简介和快速导航
2. **双语支持** - 中文（默认）+ 英文
3. **观影记录模块** - 2237 条独立 Markdown 文件
4. **全站搜索** - 客户端 Fuse.js 搜索
5. **双平台部署** - GitHub Pages + Cloudflare Pages 同步部署

## 重要技术决策

### 1. Permalink 自动化 URL 生成

**时间**: 2025-11-09  
**问题**: 2237 个 watched 页面需要手动配置 URL，维护成本极高  
**解决方案**:

```toml
[permalinks.page]
  watched = "/watched/:contentbasename/"
```

**效果**:
- 文件名自动成为 URL（如 `tt28996126.md` → `/watched/tt28996126/`）
- 批量移除了所有 Frontmatter 中的 `url` 字段
- 支持子目录结构（imdb/douban）但 URL 统一为 `/watched/文件名/`

**操作记录**:
```powershell
# 批量移除 2236 个文件的 url 字段
$files = Get-ChildItem -Path "content\watched" -Recurse -Filter "*.md"
foreach ($file in $files) {
  $content = Get-Content $file.FullName -Raw
  $content = $content -replace "url: `"/watched/[^`"]+/`"\r?\n", ""
  Set-Content $file.FullName $content
}
```

**验证**: `Select-String -Path "content\watched\**\*.md" -Pattern "url:"` 返回 0 结果

### 2. 双平台部署的 BaseURL 管理

**时间**: 2025-11-09  
**问题**: GitHub Pages 和 Cloudflare Pages 需要不同的 baseURL  
**解决方案**:

- **GitHub Pages**: 使用 `hugo.toml` 中的 `baseURL = "https://yogggithub.github.io/"`
- **Cloudflare Pages**: 设置环境变量 `HUGO_BASEURL=https://yourdomain.xyz/` 覆盖

**配置**:
```toml
# hugo.toml
baseURL = "https://yogggithub.github.io/"
canonifyURLs = false  # 不自动转换为绝对 URL
relativeURLs = false  # 使用绝对路径而非相对路径
```

**菜单配置**:
```toml
# 使用绝对路径（以 / 开头）
[[languages.zh.menu.main]]
  url = "/posts/"      # 正确
  # url = "posts"      # 错误：会被拼接为完整域名

[[languages.en.menu.main]]
  url = "/en/posts/"   # 正确
```

**原理**: 
- 相对路径 `"posts"` → Hugo 添加 baseURL → `https://domain.com/posts/`（完整 URL）
- 浏览器识别为外部链接 → 新标签打开
- 绝对路径 `"/posts/"` → 保持原样 → 浏览器识别为内部链接 → 当前标签打开

### 3. PaperMod 主题的 Git 子模块管理

**时间**: 项目初始化  
**问题**: 主题文件为空，页面无法渲染  
**原因**: Git 子模块注册但未初始化  
**解决方案**:

```bash
# 初始化子模块
git submodule update --init --recursive

# 验证
Get-ChildItem themes/PaperMod/layouts -Recurse | Measure-Object
# 结果：42 个布局文件
```

**CI/CD 配置**:
```yaml
# .github/workflows/deploy.yml
- name: 检出代码
  uses: actions/checkout@v4
  with:
    submodules: recursive  # 关键：自动初始化子模块
```

### 4. Profile 模式配置

**时间**: 2025-11-09  
**功能**: 将首页从文章列表改为个人展示页  
**配置**:

```toml
[params.profileMode]
  enabled = true
  title = "Your Name"
  subtitle = "欢迎来到我的个人网站 👋"
  imageUrl = "/logo.png"
  imageWidth = 120
  imageHeight = 120
  imageTitle = "我的头像"
  buttons = [
    {name = "文章", url = "/posts/"},
    {name = "相册", url = "/gallery/"},
    {name = "影评", url = "/watched/"},
    {name = "归档", url = "/archives/"},
    {name = "搜索", url = "/search/"}
  ]
```

**效果**:
- 首页显示头像和简介
- 5 个快速导航按钮
- 社交媒体图标（Email、Telegram、Buy Me a Coffee、PayPal 等）

### 5. 社交图标配置

**时间**: 2025-11-09  
**发现**: PaperMod 主题内置 141 种社交网络图标  
**配置示例**:

```toml
[[languages.zh.params.socialIcons]]
  name = "github"
  url = "https://github.com/username"

[[languages.zh.params.socialIcons]]
  name = "email"
  url = "mailto:your@email.com"

[[languages.zh.params.socialIcons]]
  name = "telegram"
  url = "https://t.me/username"

[[languages.zh.params.socialIcons]]
  name = "buymeacoffee"
  url = "https://buymeacoffee.com/username"

[[languages.zh.params.socialIcons]]
  name = "paypal"
  url = "https://paypal.me/username"
```

**支持的图标**（部分）:
- 开发平台：github, gitlab, codepen, stackoverflow
- 社交媒体：twitter, facebook, instagram, telegram, discord
- 中文平台：douban, bilibili, zhihu, juejin
- 资助平台：buymeacoffee, kofi, patreon, paypal
- 完整列表：141 种（见 `themes/PaperMod/layouts/partials/svg.html`）

### 6. Logo 和 Favicon 配置

**时间**: 2025-11-09  
**文件位置**: `static/logo.png`, `static/favicon.png`  
**配置**:

```toml
[params.label]
  icon = "/logo.png"
  iconHeight = 35

[params.assets]
  favicon = "/favicon.png"
  favicon16x16 = "/favicon.png"
  favicon32x32 = "/favicon.png"
  apple_touch_icon = "/favicon.png"
```

## 项目结构演变

### 初始结构
```
my-blog/
├── content/
│   ├── posts/
│   ├── watched/
│   └── gallery.md
├── themes/PaperMod/
└── hugo.toml
```

### 当前结构
```
yogggithub.github.io/
├── .github/workflows/      # GitHub Actions
├── content/
│   ├── posts/             # 博客文章
│   ├── watched/           # 2237 个观影记录
│   │   ├── imdb/          # IMDb 来源
│   │   └── douban/        # 豆瓣来源
│   ├── gallery/           # 相册
│   ├── archives.md        # 归档页
│   ├── search.md          # 搜索页
│   └── en/                # 英文内容
├── static/
│   ├── logo.png           # 网站 Logo
│   └── favicon.png        # Favicon
├── themes/PaperMod/       # Git 子模块
└── hugo.toml              # 配置文件
```

## 配置文件变更历史

### hugo.toml 主要变更

1. **基础配置**
   - `baseURL`: example.com → yogggithub.github.io
   - `defaultContentLanguage`: zh
   - `canonifyURLs`: false（防止 URL 转换）
   - `relativeURLs`: false（使用绝对路径）

2. **Profile 模式**
   - 启用 `params.profileMode`
   - 配置头像、简介、快速导航按钮

3. **Permalink 配置**
   - 添加 `[permalinks.page]` 部分
   - `watched = "/watched/:contentbasename/"`

4. **多语言配置**
   - 中文（zh）+ 英文（en）
   - 独立的菜单和内容目录
   - 社交图标配置

5. **菜单 URL 修正**
   - 所有菜单项改为绝对路径（以 `/` 开头）
   - 中文：`/posts/`, `/gallery/`, `/watched/`, `/archives/`, `/search/`
   - 英文：`/en/posts/`, `/en/gallery/`, `/en/watched/`, `/en/archives/`, `/en/search/`

## 部署配置

### GitHub Actions

**文件**: `.github/workflows/deploy.yml`  
**关键配置**:
- Hugo 版本：0.152.2 Extended
- 使用 `peaceiris/actions-hugo@v3` 官方 Action
- 子模块自动初始化：`submodules: recursive`
- 部署目标：`gh-pages` 分支

### Cloudflare Pages

**构建设置**:
- Framework: Hugo
- Build command: `hugo --minify`
- Build output: `public`
- Hugo version: 0.152.2

**环境变量**:
- `HUGO_VERSION=0.152.2`
- `HUGO_BASEURL=https://yourdomain.xyz/`（覆盖 baseURL）

## 常见问题解决

### 问题 1: Watched 页面 404

**症状**: 链接如 `/watched/imdb/tt28996126/` 返回 404  
**原因**: 2235 个文件有手动 `url` 字段（`/watched/tt28996126/`），与目录结构不匹配  
**解决**: 配置 Permalink + 批量移除 `url` 字段

### 问题 2: GitHub Actions 部署失败

**错误**: `Permission denied` 访问 `/hugo.deb`  
**原因**: 手动下载 Hugo 到 `$TMPDIR` 失败  
**解决**: 改用官方 `peaceiris/actions-hugo@v3` Action

### 问题 3: PaperMod 主题文件为空

**症状**: `found no layout file for html` 警告  
**原因**: Git 子模块未初始化  
**解决**: `git submodule update --init --recursive`

### 问题 4: Cloudflare Pages 菜单新标签打开

**症状**: 首次点击菜单在新标签打开  
**原因**: 相对 URL `"posts"` + `HUGO_BASEURL` → 完整域名 URL → 浏览器视为外部链接  
**解决**: 菜单改用绝对路径 `"/posts/"`

### 问题 5: 模板解析错误

**错误**: `unexpected <define> in command`  
**原因**: 模板文件包含 `{{define}}` 但不在正确的上下文中  
**解决**: 确保模板使用 `{{define "main"}}` 并在 `baseof.html` 中调用

## 维护指南

### 更新主题

```bash
cd themes/PaperMod
git pull origin master
cd ../..
git add themes/PaperMod
git commit -m "更新 PaperMod 主题"
```

### 批量操作 Watched 文件

```powershell
# 统计文件数量
(Get-ChildItem -Path "content\watched" -Recurse -Filter "*.md").Count

# 查找包含特定字段的文件
Select-String -Path "content\watched\**\*.md" -Pattern "url:"

# 批量替换内容
Get-ChildItem -Path "content\watched" -Recurse -Filter "*.md" | ForEach-Object {
  (Get-Content $_.FullName) -replace "old-pattern", "new-pattern" | 
  Set-Content $_.FullName
}
```

### 本地测试

```bash
# 开发模式（包含草稿）
hugo server -D

# 生产模式预览
hugo server --minify

# 清理构建缓存
hugo --gc

# 检查配置
hugo config
```

## 性能优化

### 已实施

1. **URL 自动化** - 消除 2236 个手动 URL 字段
2. **子模块优化** - 主题作为子模块，减小仓库体积
3. **资源压缩** - `hugo --minify` 压缩输出
4. **静态资源** - Logo/Favicon 使用静态文件

### 可优化项

1. **图片优化** - 考虑使用 WebP 格式
2. **CDN 加速** - Cloudflare CDN for static assets
3. **搜索索引** - 考虑服务端搜索方案（如 Algolia）
4. **懒加载** - 为长页面实现图片懒加载

## 项目统计

- **启动时间**: 2025-11-08
- **总提交数**: 查看 `git log --oneline | wc -l`
- **观影记录**: 2237 条
- **支持语言**: 2 种
- **部署平台**: 2 个
- **社交图标**: 6 个已配置 / 141 个可选

## 下一步计划

- [ ] 优化观影记录的展示方式（海报墙？）
- [ ] 添加更多博客文章内容
- [ ] 完善相册功能
- [ ] 自定义主题样式
- [ ] 添加评论系统（如 Giscus）
- [ ] 集成统计分析（Google Analytics / Umami）

---

**最后更新**: 2025-11-09
