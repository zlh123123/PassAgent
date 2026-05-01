---
name: graphical-mode
description: 打开 PassInfinity 独立体验页，支持图片记忆点、地图位置、富文本标记三种独立模式，并能读取用户已保存的体验结果做解释。只在用户明确提到 PassInfinity、图形口令、图片密码、地图密码、富文本标记，或明确要求解读 PassInfinity 方案时使用。
allowed-tools: graphical_mode,passinfinity_artifact
---

# 图形口令

## Quick Start

PassInfinity 通过三种独立界面让用户构造多因子口令：

1. 如果用户已经明确类型，选择 mode（image / map / richtext）
2. **graphical_mode**(mode=...) → 打开 PassInfinity 独立体验页
3. **respond** → 向用户说明操作方法，等待用户确认跳转

如果用户只是在问 PassInfinity 是什么，或还没明确想体验哪一种：

1. 不要调用 `graphical_mode`
2. 先用简洁中文介绍三种模式的区别
3. 追问用户想先体验哪一种，等用户明确后再打开页面

如果用户要求“解释我刚保存的 PassInfinity 方案”：

1. **passinfinity_artifact**(artifact_id=... 或 latest=true) → 读取体验结果
2. **respond** → 解释因子结构、指出策略问题并给建议

如果用户只是：

1. 上传一张图片让你生成普通密码
2. 分析一段文本
3. 从图片/文本里提取关键词

不要使用 `graphical-mode`。这些属于普通口令生成、内容分析或多模态解析，不属于 PassInfinity 体验页。

## 工具说明

| 工具 | 用途 | 参数 |
|------|------|------|
| graphical_mode | 打开体验页 | mode: "image" / "map" / "richtext" |
| passinfinity_artifact | 读取保存结果 | artifact_id（可选） / latest（默认 true） |

## 决策策略

- 用户明确提到"PassInfinity"/"图形口令"/"图形密码" → 进入此 skill
- 用户提到"图片密码"/"图片选点"/"图片记忆点"/"图像因子" → mode="image"
- 用户提到"地图密码"/"位置密码"/"地理位置因子"/"地图位置因子" → mode="map"
- 用户提到"富文本标记"/"文本标记"/"样式标记" → mode="richtext"
- 用户提到"PassInfinity 方案解释"/"刚保存的体验结果" → 先读取 `passinfinity_artifact`
- 用户只提到 PassInfinity、但未明确因子 → 先介绍三种模式，不跳转
- 单独出现"图片"/"地图"/"文本"/"文字" 不足以进入此 skill，必须有明确的口令体验语义
- "上传图片生成密码"、"分析这段文本" 这类请求不要误判成 PassInfinity

## Examples

**用户：** "我想用图片来设置一个密码"

TODO 计划：
```
1. graphical_mode(mode="image")    → 打开图片体验页
2. respond                         → 说明：请在图片上选择 3~5 个记忆点
```

**用户：** "可以用地图位置做密码吗"

TODO 计划：
```
1. graphical_mode(mode="map")      → 打开地图体验页
2. respond                         → 说明：请在地图上标记对你有意义的位置
```

**用户：** "我想玩一下 PassInfinity"

TODO 计划：
```
1. respond                         → 简要介绍图片、地图、富文本三种模式
2. respond                         → 追问用户想先体验哪一种
```

**用户：** "我想试试富文本标记"

TODO 计划：
```
1. graphical_mode(mode="richtext") → 打开富文本体验页
2. respond                         → 说明：先写文字内容，再选择样式标记
```

**用户：** "帮我解释一下我刚才保存的 PassInfinity 方案"

TODO 计划：
```
1. passinfinity_artifact(latest=true)  → 读取最近保存的体验结果
2. respond                             → 解读因子组合和改进建议
```

**不属于本 skill：** "我上传一张图片，你帮我生成一个密码"

TODO 计划：
```
应交给普通口令生成链路，不要打开 PassInfinity 页面。
```
```

## 完成条件

打开体验页或读取结果后，调用 **respond** 向用户说明下一步或解读结果。
