---
name: strength-assessment
description: 评估口令强度，包括熵值评分、字符组成分析、模式检测、弱口令匹配和个人信息泄露检查。当用户想检测密码强度、分析密码安全性、问"这个密码安不安全"时使用。
allowed-tools: zxcvbn_check,basic_analysis,pattern_detect,weak_list_match,pcfg_analyze,passgpt_prob,pass2rule,personal_info_check
---

# 口令强度评估

## Quick Start

对一个密码执行多维度强度评估，典型流程：

1. **zxcvbn_check** → 获取熵值评分(0-4)和破解时间，作为后续策略的基准
2. 根据 zxcvbn 评分选择 2~3 个补充工具
3. 如果有用户记忆 → 加入 **personal_info_check**
4. 调用 **respond** 汇总报告

## 工具说明

| 工具 | 用途 | 优先级 |
|------|------|--------|
| zxcvbn_check | 熵值评分(0-4)、破解时间 | 必调，第一个 |
| basic_analysis | 字符组成（大小写/数字/特殊）、重复模式 | 高 |
| pattern_detect | 键盘模式(qwerty)、拼音组合、日期模式 | 高 |
| weak_list_match | 弱口令库匹配(top100/top1000/rockyou) | 中，弱密码时优先 |
| pcfg_analyze | PCFG 结构分析，是否为常见结构 | 中 |
| personal_info_check | 结合用户记忆检测个人信息（需 memories） | 有记忆时必调 |
| passgpt_prob | GPU 模型评估猜中概率（待接入） | 低 |
| pass2rule | hashcat 规则变化分析（待接入） | 低 |

## 决策策略

**根据 zxcvbn 评分分流：**

- 评分 0~1（极弱/弱）→ 补充 weak_list_match + pattern_detect + basic_analysis
- 评分 2（中等）→ 补充 basic_analysis + pattern_detect 或 pcfg_analyze
- 评分 3~4（强/极强）→ 补充 basic_analysis + 一个其他工具即可

**记忆感知：** 如果 memories 非空，务必加入 personal_info_check — 很多用户用生日、姓名做密码，这是高危信号。

## Examples

**用户：** "帮我检测一下 qwerty123 安全吗"

TODO 计划：
```
1. zxcvbn_check(password="qwerty123")       → 评分 0, 10秒破解
2. weak_list_match(password="qwerty123")     → 命中 top100 弱口令库
3. pattern_detect(password="qwerty123")      → 检测到键盘模式 qwerty + 顺序数字 123
4. respond                                   → 汇总：极弱密码，键盘模式+顺序数字，在弱口令库中
```

**用户：** "X$9kL#2mP!qR 这个密码够强吗"

TODO 计划：
```
1. zxcvbn_check(password="X$9kL#2mP!qR")    → 评分 4, 世纪级破解时间
2. basic_analysis(password="X$9kL#2mP!qR")   → 12位，含大小写+数字+特殊，无重复
3. respond                                   → 汇总：极强密码，无需更多评估
```

## 完成条件

3 个以上不同工具有结果后，调用 **respond** 生成结构化报告。
