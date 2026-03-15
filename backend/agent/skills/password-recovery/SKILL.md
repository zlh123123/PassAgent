---
name: password-recovery
description: 根据用户提供的记忆片段，通过排列组合和变体扩展来恢复忘记的口令。当用户忘记密码、只记得密码的部分片段、想找回旧密码时使用。
allowed-tools: fragment_combine,common_variant_expand
---

# 口令恢复

## Quick Start

口令恢复的核心流程是"收集片段 → 组合候选 → 变体扩展"：

1. **retrieve_memory** → 获取用户记忆中的个人信息（姓名、生日、宠物名等常用密码素材）
2. 结合用户提供的线索，提取记忆片段
3. **fragment_combine**(fragments=[...]) → 排列组合生成基础候选
4. **common_variant_expand**(base_list=[...]) → 对候选做变体扩展（大小写、leet speak、追加数字等）
5. **respond** → 展示候选列表供用户辨认

## 工具说明

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| fragment_combine | 记忆片段排列组合，自动展开年份为多种日期格式 | fragments（必需）、pattern（可选组合提示） |
| common_variant_expand | hashcat 规则子集变体：大小写、leet speak、追加数字/符号、反转 | base_list（必需） |

## 决策策略

**记忆优先（强制）：** 恢复场景必须先有 memories。如果 memories 为空，第一步必须是 retrieve_memory。

**中文转换规则（强制）：** 片段中的中文 **必须转为拼音或英文**：
- "小红" → "xiaohong"
- "2000年" → 保留 "2000"（fragment_combine 会自动展开为 "2000", "00", "0000" 等日期格式）
- "北京" → "beijing"

**组合策略：**
- 片段少（2~3 个）→ 直接 fragment_combine，生成所有排列
- 片段多（4+ 个）→ 通过 pattern 参数提示组合模式，减少爆炸
- 用户记得大致结构（如"名字+生日"）→ 传入 pattern 提示

## Examples

**用户：** "我忘了密码了，好像是用我名字和生日组合的"

TODO 计划：
```
1. retrieve_memory(query="姓名 生日")                    → 记忆：姓名"张小红", 生日"1995-08-15"
2. fragment_combine(fragments=["zhangxiaohong","zhang","xiaohong","1995","0815","815"])
   → 生成候选: zhangxiaohong1995, xiaohong0815, zhang1995, ...
3. common_variant_expand(base_list=["xiaohong0815","zhang1995",...])
   → 变体: Xiaohong0815, xiaohong0815!, ZHANG1995, zh@ng1995, ...
4. respond                                               → 展示候选供辨认
```

**用户：** "密码里好像有 abc 和 666"

TODO 计划：
```
1. fragment_combine(fragments=["abc","666"])   → abc666, 666abc
2. common_variant_expand(base_list=["abc666","666abc"])
   → Abc666, ABC666, abc666!, 666abc!, ...
3. respond                                     → 展示候选
```

## 完成条件

生成候选口令列表后，调用 **respond** 展示供用户辨认。如果用户说"都不对"，可以追问更多线索后重新组合。
