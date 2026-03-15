---
name: graphical-mode
description: 唤起前端图形口令组件，支持图片选点和地图选点两种模式。当用户想使用图形密码、图片密码、地图密码、可视化密码时使用。
allowed-tools: graphical_mode
---

# 图形口令

## Quick Start

图形口令通过用户在图片或地图上的选点位置生成密码：

1. 根据用户需求选择 mode（image 或 map）
2. **graphical_mode**(mode=...) → 唤起前端组件
3. **respond** → 向用户说明操作方法，等待用户完成选点

## 工具说明

| 工具 | 用途 | 参数 |
|------|------|------|
| graphical_mode | 唤起前端图形口令组件 | mode: "image"（图片选点）或 "map"（地图选点） |

## 决策策略

- 用户提到"图片密码"/"图片选点" → mode="image"
- 用户提到"地图密码"/"位置密码" → mode="map"
- 用户未明确 → 默认推荐 mode="image"，并简要说明两种模式的区别

## Examples

**用户：** "我想用图片来设置一个密码"

TODO 计划：
```
1. graphical_mode(mode="image")    → 唤起图片选点组件
2. respond                         → 说明：请在图片上选择 3~5 个记忆点
```

**用户：** "可以用地图位置做密码吗"

TODO 计划：
```
1. graphical_mode(mode="map")      → 唤起地图选点组件
2. respond                         → 说明：请在地图上标记对你有意义的位置
```

## 完成条件

唤起组件后，调用 **respond** 向用户说明操作方式和注意事项。
