---
name: breach-checking
description: 查询密码或邮箱是否出现在已知泄露数据库中，获取泄露事件详情。当用户想查密码是否泄露、邮箱是否暴露、了解某个数据泄露事件时使用。
allowed-tools: hibp_password_check,hibp_email_check,breach_detail
---

# 泄露检查

## Quick Start

根据用户提供的信息类型选择工具：

1. 提供了密码 → **hibp_password_check**（k-Anonymity 安全查询，不会泄露明文）
2. 提供了邮箱 → **hibp_email_check**（验证有效性 + 暴露风险评估）
3. 想了解某个泄露事件 → **breach_detail**(breach_name=...)
4. 想看全部泄露事件 → **breach_detail**()（不传参数）

## 工具说明

| 工具 | 用途 | 输入 |
|------|------|------|
| hibp_password_check | HIBP k-Anonymity 密码泄露查询 | password（必需） |
| hibp_email_check | Hunter.io 邮箱验证 + 暴露风险 | email（必需） |
| breach_detail | 泄露事件详情或列表 | breach_name（可选）、domain（可选） |

## 决策策略

- 用户只提供密码 → 调 hibp_password_check，一次即可
- 用户只提供邮箱 → 调 hibp_email_check，一次即可
- 用户同时提供密码和邮箱 → 两个工具都调
- 用户未提供密码或邮箱 → 直接 **respond** 追问
- 查询到泄露后用户想知道详情 → 追加 breach_detail

## Examples

**用户：** "123456 这个密码有没有被泄露过"

TODO 计划：
```
1. hibp_password_check(password="123456")   → 泄露 23,547,453 次
2. respond                                  → 极度危险，已泄露超过 2300 万次
```

**用户：** "帮我查一下 test@example.com 安全吗"

TODO 计划：
```
1. hibp_email_check(email="test@example.com")  → 邮箱有效，关联 3 次泄露
2. breach_detail(domain="example.com")          → 获取相关泄露事件详情
3. respond                                      → 汇总邮箱暴露风险和泄露事件
```

## 完成条件

查询结果返回后，调用 **respond** 汇总泄露情况、影响范围和安全建议。
