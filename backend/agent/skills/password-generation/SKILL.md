---
name: password-generation
description: 生成安全口令，支持基于种子词变换、助记短语、可发音随机口令等方式。当用户想创建新密码、为某网站生成密码、用图片/音频素材生成密码时使用。
allowed-tools: generate_password,passphrase_generate,pronounceable_generate,fetch_site_policy,multimodal_parse
---

# 口令生成

## Quick Start

根据用户需求选择生成策略：

1. 有个人偏好/种子词 → 先 **retrieve_memory**，再 **generate_password**(seeds=...)
2. 为特定网站 → 先 **fetch_site_policy**，再根据策略约束生成
3. 要求好记 → **passphrase_generate**（助记短语）
4. 要求随机但可读 → **pronounceable_generate**
5. 有上传文件 → 先 **multimodal_parse** 提取关键词作为种子

## 工具说明

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| generate_password | 种子词变换或纯随机生成 | 最通用，有种子词时首选 |
| passphrase_generate | xkcdpass/diceware 助记短语 | 用户要求"好记"时 |
| pronounceable_generate | 辅音-元音音节组合 | 用户要求"可读/可念"时 |
| fetch_site_policy | 获取网站密码策略约束 | 用户说"为XX网站生成密码"时 |
| multimodal_parse | 图片/音频转文本关键词 | uploaded_files 非空时 |

## 决策策略

**生成偏好感知：**
- 自动模式（gen_auto_mode=true）→ 根据上下文自行决策生成策略和安全档位
- 手动模式（gen_auto_mode=false）→ 严格按 gen_security_weight 对应的安全档位执行

**中文转换规则（强制）：** 从用户记忆提取的种子词若为中文，**必须转为拼音或英文**再传入。口令只能包含 ASCII 字符。
- "小红" → "xiaohong"
- "北京" → "beijing"
- "生日" → "shengri" 或 "birthday"

**网站约束流程：** 用户提到特定网站时，先调 fetch_site_policy 获取约束（最小/最大长度、字符要求），再把约束传入 generate_password 的 constraints 参数。

## Examples

**用户：** "帮我生成一个 GitHub 密码"

TODO 计划：
```
1. retrieve_memory(query="GitHub 密码偏好")      → 获取用户习惯
2. fetch_site_policy(site_name="GitHub")          → min_length=8, require_upper, require_digit
3. generate_password(constraints={...})            → 基于网站策略约束生成
4. respond                                        → 展示候选密码
```

**用户：** "用我家猫的名字帮我生成一个好记的密码"

TODO 计划：
```
1. retrieve_memory(query="猫 宠物名字")            → 记忆中找到猫叫"咪咪"
2. generate_password(seeds=["mimi"], constraints={min_length: 12})  → 种子词变换
3. respond                                        → 展示候选密码
```

**用户：** "帮我生成一个容易记住的密码"

TODO 计划：
```
1. passphrase_generate(word_count=4, separator="-")  → 生成助记短语
2. respond                                           → 展示助记短语口令
```

## 完成条件

生成口令候选后，调用 **respond** 展示结果。若 TODO 中有后续强度验证步骤（跨 skill），继续执行。
