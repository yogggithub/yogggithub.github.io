---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false

# 内容类型：movie(电影) / tvshow(电视剧) / variety(综艺)
content_type: "movie"

# 基本信息
media:
  # IMDb ID (例如: tt0111161)
  imdb_id: ""
  # 豆瓣ID (例如: 1292052)
  douban_id: ""
  # 海报URL (如果不填，会自动从IMDb获取)
  poster: ""
  # 中文名称
  title: ""
  # 原始名称
  original_title: ""
  # 上映/播出年份
  year: 
  # 导演/主持人
  director: ""
  # 类型 (例如: ["剧情", "犯罪"] / ["喜剧", "真人秀"])
  genres: []
  # 电视剧/综艺专用字段（可选）
  # seasons: 1        # 季数
  # episodes: 10      # 集数
  
# 你的评分 (1-10)
rating: 0

# 标签和分类
tags: ["电影"]  # 可改为 ["电视剧"] 或 ["综艺"]
categories: ["已观看"]
---

## 简介

在这里写内容简介...

## 我的观看感受

在这里写你的观看感受...

## 推荐指数

⭐⭐⭐⭐⭐ (5/5)
