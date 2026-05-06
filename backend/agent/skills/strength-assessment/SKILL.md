---
name: strength-assessment
description: 评估口令强度，包括熵值评分、字符组成分析、模式检测、弱口令匹配和个人信息泄露检查。当用户想检测密码强度、分析密码安全性、问"这个密码安不安全"时使用。
allowed-tools: zxcvbn_check,basic_analysis,pattern_detect,weak_list_match,pcfg_analyze,passtsl_prob,pass2rule,personal_info_check
---

# 口令强度评估

## Quick Start

对一个密码执行多维度强度评估，典型流程：

1. **retrieve_memory** → 先检索用户记忆，拿到可能相关的姓名、生日、偏好、常用素材
2. **zxcvbn_check** → 获取熵值评分(0-4)和破解时间，作为基准证据
3. **basic_analysis** → 分析长度、字符类别、重复、顺序结构
4. **pattern_detect** → 检测键盘路径、拼音、日期等显式模式
5. **weak_list_match** → 检查是否命中弱口令库
6. **pcfg_analyze** → 分析 PCFG 结构，判断是否是常见模板
7. **personal_info_check** → 结合用户记忆检查是否含个人信息
8. **passtsl_prob** → 如果模型可用，估计口令在生成式猜测模型下的可猜测概率
9. **respond** → 融合所有证据，按风险优先级汇总报告

## 工具说明

| 工具 | 用途 | 优先级 |
|------|------|--------|
| zxcvbn_check | 熵值评分(0-4)、破解时间 | 必调，第一个 |
| basic_analysis | 字符组成（大小写/数字/特殊）、重复模式 | 高 |
| pattern_detect | 键盘模式(qwerty)、拼音组合、日期模式 | 高 |
| weak_list_match | 弱口令库匹配(top100/top1000/rockyou) | 中，弱密码时优先 |
| pcfg_analyze | PCFG 结构分析，是否为常见结构 | 中 |
| personal_info_check | 结合用户记忆检测个人信息（需 memories） | 有记忆时必调 |
| passtsl_prob | PassTSL/ONNX 模型评估猜中概率 | 中，高级证据 |
| pass2rule | PTN 模型规则变化分析，预测旧口令可能演化出的变体 | 条件触发 |

## 决策策略

**默认多证据链：** 只要用户提供了具体待评估口令，就尽量按 Quick Start 调用完整证据链，而不是只调用 zxcvbn/basic/pattern 后直接回复。

**不要提前停止：** 即使 zxcvbn 已经给出强/弱结论，也继续补充 weak_list_match、pcfg_analyze、personal_info_check 和 passtsl_prob。最终回复要体现“多证据融合”，说明哪些证据一致、哪些证据冲突。

**记忆感知：** personal_info_check 必须在 retrieve_memory 后执行；即使没有记忆，也让工具返回低风险证据，方便最终说明“未发现个人信息命中”。

**Pass2Rule 条件：** 只有当用户明确提到旧口令、基础口令、常用变体、演化规则、可能改成什么、找回密码等语境时，才调用 pass2rule。普通“这个密码强不强”不必强行调用 pass2rule。

**模型不可用降级：** passtsl_prob 或 pass2rule 如果返回模型缺失/依赖缺失错误，不要中断流程；把它作为“模型证据暂不可用”写进最终回复，并继续融合其他工具结果。

## Examples

**用户：** "帮我检测一下 qwerty123 安全吗"

TODO 计划：
```
1. retrieve_memory(query="qwerty123 个人信息 口令偏好")
2. zxcvbn_check(password="qwerty123")       → 评分 0, 10秒破解
3. basic_analysis(password="qwerty123")      → 长度 9，字母+数字，存在顺序数字
4. pattern_detect(password="qwerty123")      → 检测到键盘模式 qwerty + 顺序数字 123
5. weak_list_match(password="qwerty123")     → 命中弱口令库
6. pcfg_analyze(password="qwerty123")        → 常见 L6D3 结构
7. personal_info_check(password="qwerty123") → 检查用户记忆命中
8. passtsl_prob(password="qwerty123")        → 模型估计可猜测概率
9. respond                                   → 融合：弱口令命中 + 键盘模式 + 常见结构
```

**用户：** "X$9kL#2mP!qR 这个密码够强吗"

TODO 计划：
```
1. retrieve_memory(query="X$9kL#2mP!qR 个人信息 口令偏好")
2. zxcvbn_check(password="X$9kL#2mP!qR")    → 评分 4, 世纪级破解时间
3. basic_analysis(password="X$9kL#2mP!qR")   → 12位，含大小写+数字+特殊，无重复
4. pattern_detect(password="X$9kL#2mP!qR")   → 未发现明显键盘/日期/拼音模式
5. weak_list_match(password="X$9kL#2mP!qR")  → 未命中弱口令库
6. pcfg_analyze(password="X$9kL#2mP!qR")     → 结构不属于简单常见模板
7. personal_info_check(password="X$9kL#2mP!qR") → 未命中用户个人信息
8. passtsl_prob(password="X$9kL#2mP!qR")     → 模型证据
9. respond                                   → 汇总：多项证据一致支持强口令
```

## 完成条件

默认完成 zxcvbn_check、basic_analysis、pattern_detect、weak_list_match、pcfg_analyze、personal_info_check、passtsl_prob 后，再调用 **respond** 生成结构化报告。若模型工具不可用，也应记录其不可用原因后继续回复。
