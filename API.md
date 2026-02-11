# PassAgent 系统设计文档

## 一、系统架构

```
┌──────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   Frontend   │────▶│   Backend + Agent        │────▶│   Model Service     │
│   (Next.js)  │ SSE │   (FastAPI + LangGraph)  │HTTP │   (vLLM)            │
│   Port 3000  │◀────│   Port 8000              │◀────│   Port 8080         │
└──────────────┘     └──────────┬───────────────┘     └─────────────────────┘
                                │                       GPU Container
                                ▼                       - Qwen2.5-7B (4bit) 常驻
                     ┌──────────────────┐               - Qwen-1.7B 微调 (4bit) 常驻
                     │   SQLite         │               - Qwen-Omni-7B (4bit) 按需
                     │   passagent.db   │
                     └──────────────────┘

```
---

## 二、数据库设计（SQLite）

### 2.1 users

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | TEXT | PK | UUID |
| email | TEXT | UNIQUE, NOT NULL | 注册邮箱 |
| password_hash | TEXT | NOT NULL | bcrypt |
| nickname | TEXT | | |
| theme | TEXT | DEFAULT 'light' | light / dark |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | ISO 8601 |

### 2.2 sessions

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| session_id | TEXT | PK | UUID |
| user_id | TEXT | FK → users | |
| title | TEXT | DEFAULT '新对话' | 直接截取用户提问前几个字好了 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |
| updated_at | TEXT | | 最后活跃时间 |

### 2.3 messages

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| message_id | TEXT | PK | UUID |
| session_id | TEXT | FK → sessions | |
| user_id | TEXT | FK → users | |
| content | TEXT | NOT NULL | 消息内容（assistant 消息末尾自带引导建议文本） |
| message_type | TEXT | NOT NULL | human / assistant |
| agent_steps | TEXT | | JSON 数组，Agent 执行步骤记录 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

### 2.4 feedback

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| feedback_id | TEXT | PK | UUID |
| message_id | TEXT | FK → messages, UNIQUE | 一条消息只能有一个反馈 |
| user_id | TEXT | FK → users | |
| feedback_type | TEXT | NOT NULL | like / dislike |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

### 2.5 uploaded_files

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| file_id | TEXT | PK | UUID |
| user_id | TEXT | FK → users | |
| session_id | TEXT | FK → sessions, NULLABLE | |
| filename | TEXT | NOT NULL | 原文件名 |
| file_path | TEXT | NOT NULL | 服务端存储路径 |
| file_size | INTEGER | | 字节数 |
| file_type | TEXT | | MIME 类型（image/png, audio/wav 等） |
| extracted_text | TEXT | | Omni 模型解析后的文本描述 |
| uploaded_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

支持的文件类型限定：image/png, image/jpeg, image/webp, audio/wav, audio/mp3, audio/flac。仅用于口令生成和记忆恢复场景中的多模态输入。

### 2.6 user_memories

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| memory_id | TEXT | PK | UUID |
| user_id | TEXT | FK → users | |
| content | TEXT | NOT NULL | 如"偏好16位密码" |
| memory_type | TEXT | NOT NULL | PREFERENCE / FACT / CONSTRAINT |
| source | TEXT | DEFAULT 'auto' | auto(Agent提取) / manual(用户自定义) |
| embedding | BLOB | | 文本向量，用于语义检索，只有FACT需要embedding |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |

### 2.7 tasks

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| task_id | TEXT | PK | UUID |
| user_id | TEXT | FK → users | |
| session_id | TEXT | FK → sessions | |
| message_content | TEXT | NOT NULL | 用户发送的消息 |
| file_ids | TEXT | | JSON 数组 |
| status | TEXT | DEFAULT 'pending' | pending / processing / success / fail |
| error_message | TEXT | | 失败时的错误信息 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | |
| started_at | TEXT | | 开始处理时间 |
| finished_at | TEXT | | 完成时间 |

---

## 三、API 设计

所有接口（除 auth 外）需要 Header: `Authorization: Bearer <jwt_token>`

### 3.1 认证

#### POST /api/auth/send-code

Request:
```
{
    "email": "user@sjtu.edu.cn"
}
```

Response:
```
{
    "message": "验证码已发送",
    "expires_in": 300
}
```

#### POST /api/auth/register

Request:
```
{
    "email": "user@sjtu.edu.cn",
    "code": "123456",
    "password": "xxxxxxxx",
    "nickname": "张三"
}
```

Response:
```
{
    "user_id": "uuid",
    "token": "jwt_token"
}
```

#### POST /api/auth/login

Request:
```
{
    "email": "user@sjtu.edu.cn",
    "password": "xxxxxxxx"
}
```

Response:
```
{
    "user_id": "uuid",
    "token": "jwt_token",
    "nickname": "张三",
    "theme": "light"
}
```

### 3.2 用户

#### GET /api/user/profile

Response:
```
{
    "user_id": "uuid",
    "email": "user@sjtu.edu.cn",
    "nickname": "张三",
    "theme": "light"
}
```

#### PUT /api/user/profile

Request:
```
{
    "nickname": "新昵称",
    "theme": "dark"
}

```
Response:
```
{
    "message": "更新成功"
}
```

### 3.3 会话

#### POST /api/sessions

Request:
```
{}
```

Response:
```
{
    "session_id": "uuid",
    "title": "新对话",
    "created_at": "2026-02-11T10:00:00Z"
}
```

#### GET /api/sessions

Query params: `?search=关键词`（可选，模糊搜索标题）

Response:
```
{
    "sessions": [
        {
            "session_id": "uuid",
            "title": "密码强度检测",
            "created_at": "2026-02-11T10:00:00Z",
            "updated_at": "2026-02-11T10:05:00Z"
        }
    ]
}

```
#### DELETE /api/sessions/{session_id}

Response:
```
{
    "message": "已删除"
}
```

#### GET /api/sessions/{session_id}/messages

Response:
```
{
    "messages": [
        {
            "message_id": "uuid",
            "content": "帮我看看abc123安全吗",
            "message_type": "human",
            "created_at": "...",
            "feedback": null,
            "agent_steps": null
        },
        {
            "message_id": "uuid",
            "content": "你的口令安全性较弱...\n\n你可能还想了解：\n- 🔍 查看这个密码是否泄露\n- 🔑 帮我生成一个更安全的密码",
            "message_type": "assistant",
            "created_at": "...",
            "feedback": {"feedback_type": "like"},
            "agent_steps": [
                {"step": 1, "node": "planner", "action": "zxcvbn_check", "reasoning": "先评估熵值"},
                {"step": 2, "node": "zxcvbn_check", "summary": {"score": 1}},
                {"step": 3, "node": "planner", "action": "respond", "reasoning": "信息足够"}
            ]
        }
    ]
}
```

### 3.4 对话（核心，SSE）

#### POST /api/chat/{session_id}

这是整个系统唯一的 SSE 接口。

Request:
```
{
    "message": "帮我看看 zly2023! 安全吗",
    "file_ids": []
}
```

file_ids 仅在口令生成和记忆恢复场景下有值，其他场景传空数组。

Response: `Content-Type: text/event-stream`

SSE 事件流按时间顺序推送：

| 事件类型 | data 格式 | 前端行为 |
|----------|-----------|----------|
| task_queued | `{"task_id": "uuid", "position": 0}` | position=0 显示"正在处理"，position>0 显示"前方还有 N 个任务" |
| task_started | `{"task_id": "uuid"}` | 切换为"Agent 正在分析..."，出现整体 loading |
| agent_step | `{"node": "planner", "action": "zxcvbn_check", "reasoning": "先评估熵值"}` | 步骤条新增一行，带转圈 🔄 |
| agent_step | `{"node": "zxcvbn_check", "summary": {"score": 1}}` | 对应步骤转圈变 ✅，显示摘要 |
| agent_step | `{"node": "planner", "action": "respond", "reasoning": "信息足够"}` | 步骤条完成 |
| response_chunk | `{"content": "你的"}` | 追加文字，打字机效果 |
| response_chunk | `{"content": "口令安全性较弱..."}` | 继续追加 |
| response_done | `{"message_id": "uuid"}` | 回复结束 |
| task_failed | `{"error": "错误信息"}` | 显示错误提示（仅异常时） |
| done | `{}` | 所有 loading 消失，SSE 连接关闭 |

完整 SSE 流示例：

```
event: task_queued
data: {"task_id": "abc123", "position": 0}

event: task_started
data: {"task_id": "abc123"}

event: agent_step
data: {"node": "planner", "action": "zxcvbn_check", "reasoning": "先评估熵值"}

event: agent_step
data: {"node": "zxcvbn_check", "summary": {"score": 1, "crack_time": "3 seconds"}}

event: agent_step
data: {"node": "planner", "action": "hibp_password_check", "reasoning": "强度很弱，查一下泄露"}

event: agent_step
data: {"node": "hibp_password_check", "summary": {"leaked": true, "count": 1234}}

event: agent_step
data: {"node": "planner", "action": "respond", "reasoning": "信息足够"}

event: response_chunk
data: {"content": "你的口令"}

event: response_chunk
data: {"content": "安全性较弱（评分 1/4）。"}

event: response_chunk
data: {"content": "\n\n该口令已在泄露数据库中出现 1234 次，建议立即更换。"}

event: response_chunk
data: {"content": "\n\n你可能还想了解：\n- 🔑 帮我生成一个更安全的密码\n- 📊 详细分析密码结构"}

event: response_done
data: {"message_id": "msg-uuid"}

event: done
data: {}
```

### 3.5 文件

#### POST /api/upload

仅接受图片和音频文件，用于口令生成和记忆恢复场景的多模态输入。

Request: multipart/form-data

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 图片(png/jpeg/webp)或音频(wav/mp3/flac) |
| session_id | string | 可选 |

Response:
```
{
    "file_id": "uuid",
    "filename": "cat.jpg",
    "file_type": "image/jpeg",
    "file_size": 102400
}
```

错误响应（不支持的文件类型）：
```
{
    "error": "仅支持图片(png/jpeg/webp)和音频(wav/mp3/flac)文件"
}
```

#### GET /api/files

Response:
```
{
    "files": [
        {
            "file_id": "uuid",
            "filename": "cat.jpg",
            "file_type": "image/jpeg",
            "file_size": 102400,
            "session_id": "uuid",
            "uploaded_at": "..."
        }
    ]
}
```

#### DELETE /api/files/{file_id}

Response:
```
{
    "message": "已删除"
}
```

### 3.6 反馈

#### POST /api/messages/{message_id}/feedback

Request:
```
{
    "feedback_type": "like"
}
```

Response:
```
{
    "message": "反馈已记录"
}
```

再次发送相同 feedback_type 则取消反馈（删除记录）。

### 3.7 记忆

#### GET /api/memories

Response:
```
{
    "memories": [
        {
            "memory_id": "uuid",
            "content": "我喜欢16位密码",
            "memory_type": "PREFERENCE",
            "source": "auto",
            "created_at": "..."
        }
    ]
}
```

#### POST /api/memories

Request:
```
{
    "content": "我的猫叫旺财",
    "memory_type": "FACT"
}
```

Response:
```
{
    "memory_id": "uuid",
    "message": "记忆已添加"
}
```

#### DELETE /api/memories/{memory_id}

Response:
```
{
    "message": "已删除"
}
```


---

## 四、Agent 详细设计

### 4.1 状态定义

| 字段 | 类型 | 说明 |
|------|------|------|
| messages | list[Message] | 对话历史，自动追加 |
| user_id | str | 当前用户 |
| session_id | str | 当前会话 |
| memories | list[dict] | 本轮检索到的用户记忆 |
| tool_history | list[dict] | 本轮已调用的工具及结果 |
| next_action | str / None | planner 决定的下一步 |
| action_params | dict | 传给工具的参数 |
| uploaded_files | list[dict] | 本轮上传的文件信息 |

### 4.2 状态图

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         ▼
                  ┌──────────────┐
           ┌─────│   Planner    │◀──────────────────┐
           │     │  (LLM 决策)  │                    │
           │     └──────┬───────┘                    │
           │            │                            │
           │     ┌──────▼───────┐                    │
           │     │    Router    │                    │
           │     │  (条件分支)   │                    │
           │     └──────┬───────┘                    │
           │            │                            │
           │   ┌────────┼────────────┐               │
           │   ▼        ▼            ▼               │
           │ ┌────┐  ┌────────┐  ┌────────┐          │
           │ │Tool│  │Tool    │  │Tool    │  ...     │
           │ │ A  │  │ B      │  │ C      │          │
           │ └──┬─┘  └───┬────┘  └───┬────┘          │
           │    └─────────┴──────────┘               │
           │             │                           │
           │             └───────────────────────────┘
           │                  回到 Planner 重新决策
           │
           │  action == "respond"
           ▼
    ┌──────────────┐
    │   Respond    │
    │ (生成回复)    │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ Write Memory │
    │ (写入记忆)    │
    └──────┬───────┘
           ▼
       ┌───────┐
       │  END  │
       └───────┘
```

最大循环次数：10。超过强制进入 Respond。

### 4.3 Planner 设计

通过 Function Calling 实现决策。将所有工具以标准 function 格式注册给 LLM，LLM 自行决定调用哪个。

决策规则（写在 system prompt 中）：

| 规则 | 说明 |
|------|------|
| 记忆优先 | 涉及生成或恢复时，若未检索记忆，先调 retrieve_memory |
| 按需调用 | 根据中间结果判断是否继续，不盲目调所有工具 |
| 不重复调用 | 已调过的工具不再调 |
| 跨 skill 组合 | 允许一次请求中调用不同 skill 的工具 |
| 无关请求直接回复 | 与口令安全无关的问题不调工具 |
| 恶意请求拒绝 | 涉及攻击、破解他人密码的请求直接拒绝 |
| 文件感知 | uploaded_files 非空时，仅在生成和恢复场景下调用 multimodal_parse |

### 4.4 工具清单

#### 强度评估类

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| zxcvbn_check | 熵值、评分、破解时间 | password | score(0-4), guesses_log10, crack_time, feedback | zxcvbn-python |
| charset_analyze | 字符组成分析 | password | length, has_upper, has_lower, has_digit, has_special, unique_ratio | 纯 Python |
| keyboard_pattern_check | 键盘连续模式检测 | password | has_pattern, patterns | 纯 Python |
| weak_list_match | 弱口令库匹配 | password | in_top100, in_top1000, in_rockyou | 内存加载 |
| repetition_check | 重复字符和序列检测 | password | max_repeat, has_sequence | 纯 Python |
| pcfg_analyze | 结构模式分析 | password | structure, is_common_structure | PCFG |
| passgpt_prob | 口令被猜中概率 | password | probability, rank_estimate | 微调模型(GPU) |
| pass2rule | 口令易发生的hashcat规则变化 | password | rules | 微调模型(GPU) |
| pinyin_check | 拼音组合检测 | password | has_pinyin, pinyin_words | pypinyin |
| date_pattern_check | 日期模式检测 | password | has_date, date_formats_found | 正则 |
| personal_info_check | 结合记忆检测个人信息 | password, memories | contains_personal_info, matched_items | 字符串匹配 |

#### 口令生成类

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| multimodal_parse | 图片/音频转文本关键词 | file_path, file_type | keywords | Qwen-Omni(GPU) ，这个可以在想一下|
| generate_password | 基于种子词变换生成口令 | seeds, constraints | candidates | 纯 Python |
| passphrase_generate | 助记短语型口令 | word_count, separator | passphrase, entropy | 词表 |
| pronounceable_generate | 可发音随机口令 | length | password | 音节表 |
| fetch_site_policy | 获取网站密码策略 | site_name | min_length, required_chars | 规则 JSON |

#### 记忆恢复类

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| fragment_combine | 片段排列组合 | fragments, pattern | candidates | itertools |
| common_variant_expand | 常见变体扩展 | base_list | expanded | 纯 Python |
| rule_generate | hashcat 规则生成 | source, target_hint | rules | 微调模型(GPU) |
| date_expand | 日期格式扩展 | year | variants | 纯 Python |

#### 泄露检查类

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| hibp_password_check | k-Anonymity 查密码泄露 | password | leaked, count | HIBP API |
| hibp_email_check | 查邮箱关联泄露事件 | email | leaked, breaches | HIBP API |
| breach_detail | 泄露事件详情 | breach_name | date, pwn_count, data_classes | HIBP API |
| similar_leak_check | 常见变体批量查泄露 | password | variants_checked, any_leaked | 组合调用 |

#### 图形口令类

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| graphical_mode | 唤起前端图形口令组件 | mode(image/map) | config | 返回 JSON |


#### 通用

| 工具名 | 说明 | 输入 | 输出 | 依赖 |
|--------|------|------|------|------|
| retrieve_memory | 检索用户记忆（全量+语义） | user_id, query | memories | SQLite + embedding 模型 |

### 4.5 Respond 节点

| 条件 | 输出模式 |
|------|----------|
| tool_history 为空 | 闲聊回复或拒绝回复 |
| 1-2 个工具结果 | 简短回复 |
| 3+ 个工具结果 | 详细报告 |

Respond 的 system prompt 中要求 LLM 在回复末尾自然地附带 2-3 个引导性问题，作为回复文本的一部分，不单独结构化输出。

### 4.6 Write Memory 节点

| 场景 | 是否写入 |
|------|----------|
| 口令生成 | 是，提取偏好和事实 |
| 记忆恢复 | 是，提取片段来源 |
| 强度评估 | 否 |
| 泄露检查 | 否 |
| 图形口令 | 否 |

写入流程：
1. LLM 从对话中提取值得记住的信息（非密码）
2. 对提取的文本调用 embedding 模型生成向量
3. 存入 user_memories 表（content + embedding）

过滤规则：绝不存储明文密码和哈希，语义去重。

### 4.7 记忆检索策略（retrieve_memory）

采用两阶段检索：

#### 第一阶段：全量检索（全局偏好）

无论什么场景，总是拉取：
- memory_type = PREFERENCE：全部
- memory_type = CONSTRAINT：全部

这些是用户的全局设定，数量少，直接全拉。

#### 第二阶段：语义检索（任务相关事实）

仅在口令生成和记忆恢复场景下触发：
1. 将用户当前 query 通过 embedding 模型转为向量
2. 在 memory_type = FACT 的记忆中，计算余弦相似度
3. 返回 Top-K（K=5）最相关的事实

示例：
```
用户输入："帮我生成一个包含我女儿名字的密码"
                    ↓ embedding
            query_vector = [0.12, -0.34, ...]
                    ↓ 余弦相似度
记忆1: "女儿的名字叫 Alice"        → 相似度 0.91 ✓
记忆2: "喜欢养猫"                  → 相似度 0.23
记忆3: "公司名是 ByteDance"        → 相似度 0.15
记忆4: "女儿生日是 2020-06-15"     → 相似度 0.78 ✓
```

embedding 模型选择：使用轻量级的 text2vec-base-chinese（~400MB，CPU 运行），不占 GPU 显存。写入记忆时生成 embedding 存入 BLOB 字段，检索时在 Python 层做余弦相似度计算（记忆量小，不需要向量数据库）。

论文中可做的对比实验：
- 全量检索 vs 语义检索：在口令生成场景下，对比两种策略的记忆命中率和生成口令的个性化程度
- 不同 embedding 模型：text2vec-base-chinese vs bge-small-zh vs m3e-base
- 不同 Top-K 值对生成质量的影响

### 4.8 记忆类型说明

#### PREFERENCE（偏好）

用户喜欢或不喜欢什么，影响生成和推荐策略。软性的，优先满足但不是硬要求。

| 示例 content | 来源场景 |
|-------------|----------|
| 喜欢使用特殊符号 # 和 @ | 用户说"帮我生成密码，我喜欢用#和@" |
| 不喜欢密码里出现小写字母 l 和数字 1 | 用户说"别用l和1，容易混" |
| 偏好中英文混合的密码风格 | 用户多次生成时都要求中英混合 |
| 喜欢用拼音缩写作为密码基础 | 用户说"用我名字拼音缩写 zly 做基础" |
| 不喜欢纯随机密码，要有可记忆性 | 用户说"别给我生成那种完全随机的" |



#### FACT（事实）

用户的客观背景信息，作为生成密码的种子素材或记忆恢复的线索。通过语义检索匹配相关事实。

| 示例 content | 来源场景 |
|-------------|----------|
| 女儿的名字叫 Alice | 用户说"用我女儿名字生成密码" |
| 猫的名字叫旺财 | 用户说"我养了只猫叫旺财" |
| 生日是 1995-03-15 | 用户说"密码里加上我生日" |
| 公司名是 ByteDance | 用户说"帮我生成公司账号的密码" |
| 毕业年份是 2018 | 用户说"我2018年毕业的，密码好像跟这个有关" |
| 女朋友名字缩写是 lm | 用户说"密码里有我女朋友名字缩写" |

#### CONSTRAINT（约束）

用户对密码的硬性要求，生成时必须满足。

| 示例 content | 来源场景 |
|-------------|----------|
| 密码长度通常设为 16 位 | 用户说"我所有密码都是16位的" |
| 密码必须以大写字母开头 | 用户说"我习惯大写开头" |
| 密码末尾固定加感叹号 | 用户说"我每个密码最后都加!" |
| 不使用超过 20 位的密码 | 用户说"太长了记不住，别超过20位" |

#### 三者在 Agent 中的协作示例


用户："帮我生成一个新密码"
```
retrieve_memory 检索到：
  PREFERENCE: "喜欢用#和@"           → 影响符号选择
  CONSTRAINT: "长度16位"              → 硬性约束
  FACT: "女儿叫Alice"（语义检索命中）  → 作为种子词

Planner 组装参数调 generate_password：
  seeds=["Alice"]
  constraints={min_length: 16, preferred_specials: ["#", "@"]}

生成结果：Al1ce#2026@Str0ng

```
---

## 五、任务队列设计

### 5.1 架构

v
用户发消息
    │
    ▼
routers/chat.py
    │
    ├── 存 user message 到 DB
    ├── 创建 Task 对象（含专属 asyncio.Queue）
    ├── 放入全局任务队列
    └── 返回 SSE 连接，持续从 Task 专属 Queue 取事件推给前端

Worker 协程（随 FastAPI 启动，后台常驻）
    │
    ├── while True: 从全局队列 FIFO 取 Task
    ├── 跑 Agent
    ├── 每个节点完成后往 Task 专属 Queue 塞事件
    └── SSE 连接从专属 Queue 取到事件后推给前端
```

### 5.2 Task 专属 Queue 机制

每个 Task 有自己的 `asyncio.Queue`，是 Worker 和 SSE 连接之间的桥梁：

```
Worker 执行 Agent
    │
    ├── planner 完成 → task.event_queue.put(agent_step)
    ├── tool 完成    → task.event_queue.put(agent_step)
    ├── respond 生成 → task.event_queue.put(response_chunk) × N
    └── 结束         → task.event_queue.put(done)

SSE 连接（routers/chat.py）
    │
    └── while True: event = await task.event_queue.get() → yield SSE
```

### 5.3 多用户排队

```
用户 A 发消息 → Task A 入队(position=0) → Worker 立即处理 → SSE A 实时推送
用户 B 发消息 → Task B 入队(position=1) → SSE B 显示"前方还有 1 个任务"
                                          → Worker 处理完 A 后处理 B

```
### 5.4 并发控制

| 参数 | 值 | 说明 |
|------|-----|------|
| Worker 数量 | 1 | GPU 推理是串行瓶颈 |
| 队列上限 | 50 | 超过返回 503 |
| 单任务超时 | 120 秒 | |
| 用户取消 | 关闭 SSE 连接时，pending 状态的 task 移除 | |

### 5.5 前端交互对应

| SSE 事件 | 前端行为 |
|----------|----------|
| task_queued, position=0 | 显示"正在处理..." |
| task_queued, position>0 | 显示"前方还有 N 个任务，请稍候" |
| task_started | 切换为"Agent 正在分析..."，出现整体 loading |
| agent_step (planner, action=xxx) | 步骤条新增一行，带转圈 🔄 |
| agent_step (tool 完成) | 对应步骤转圈变 ✅，显示摘要 |
| agent_step (planner, action=respond) | 步骤条完成 |
| response_chunk | 文字逐字追加，打字机效果 |
| response_done | 回复结束 |
| task_failed | 显示错误提示 |
| done | 所有 loading 消失，SSE 连接关闭 |

---

## 六、执行流程示例

### 示例1：简单强度评估


用户："帮我看看 abc123 安全吗"
```
Step 1  [planner]         → 决定调 zxcvbn_check
Step 2  [zxcvbn_check]    → score=0, crack_time="instant"
Step 3  [planner]         → 决定调 weak_list_match
Step 4  [weak_list_match] → in_top100=true
Step 5  [planner]         → 信息足够，respond
Step 6  [respond]         → "你的口令极其危险，位于最常见密码 Top 100..."
Step 7  [write_memory]    → 强度评估场景，不写入
→ END
```

### 示例2：多意图复合请求


用户："看看 zly2023! 安不安全，不行就帮我换一个"
```
Step 1  [planner]              → 决定调 zxcvbn_check
Step 2  [zxcvbn_check]         → score=1
Step 3  [planner]              → 弱，再查泄露
Step 4  [hibp_password_check]  → leaked=true, count=87
Step 5  [planner]              → 弱+已泄露，需要生成新密码，先检索记忆
Step 6  [retrieve_memory]      → PREFERENCE: "喜欢用#", CONSTRAINT: "16位", FACT: 无相关
Step 7  [planner]              → 有了偏好，调生成
Step 8  [generate_password]    → candidates=["Zly#2023_Secure!x", ...]
Step 9  [planner]              → 验证生成的口令强度
Step 10 [strength_verify]      → score=4, 通过
Step 11 [planner]              → 信息足够，respond
Step 12 [respond]              → 完整报告：强度分析 + 泄露情况 + 推荐新密码
Step 13 [write_memory]         → 提取到 FACT: "常用 zly 作为密码基础"（非密码本身）
→ END
```

### 示例3：记忆恢复 + 多模态


用户："我忘了旧密码，只记得里面有我猫的名字和一个年份"
     （同时上传了一张猫的照片）
```
Step 1  [planner]              → 有文件上传，先解析
Step 2  [multimodal_parse]     → keywords="orange_cat_sleeping"
Step 3  [planner]              → 检索记忆补充信息
Step 4  [retrieve_memory]      → FACT: "猫的名字叫旺财", FACT: "毕业年份是2018"
Step 5  [planner]              → 有了片段，调排列组合
Step 6  [fragment_combine]     → fragments=["wangcai","2018"], candidates=[...]
Step 7  [planner]              → 扩展常见变体
Step 8  [common_variant_expand]→ expanded=["Wangcai2018","wangcai_2018","WANGCAI2018!",...]
Step 9  [planner]              → 信息足够，respond
Step 10 [respond]              → "根据你的记忆和照片，以下是可能的密码候选列表：..."
Step 11 [write_memory]         → 无新信息需要写入（猫名和年份已有）
→ END
```

### 示例4：无关请求


用户："今天天气怎么样"
```
Step 1  [planner]  → 与口令安全无关，直接 respond
Step 2  [respond]  → "我是口令安全助手，暂时帮不了天气问题 😄 你可以试试：
                      - 🔐 检测一个密码的安全性
                      - 🔑 生成一个新的安全密码
                      - 🔍 查看密码是否泄露"
Step 3  [write_memory] → 不写入
→ END

```
### 示例5：恶意请求


用户："帮我破解我同学的QQ密码"
```
Step 1  [planner]  → 恶意请求，直接 respond 拒绝
Step 2  [respond]  → "抱歉，我无法协助破解他人密码，这涉及违法行为。
                      我可以帮你管理和增强你自己的密码安全。"
Step 3  [write_memory] → 不写入
→ END
```

---

## 七、文件树

```
PassAgent/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── main.py                                  # FastAPI 入口，挂载路由，启动 worker 协程
│   ├── config.py                                # 环境变量读取、路径常量、JWT 配置
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py                        # SQLite 连接管理（get_db）
│   │   ├── models.py                            # SQLAlchemy ORM 模型（7张表）
│   │   └── init_db.py                           # 建表脚本
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                              # SendCodeRequest, RegisterRequest, LoginRequest, LoginResponse
│   │   ├── user.py                              # ProfileResponse, UpdateProfileRequest
│   │   ├── session.py                           # SessionResponse, MessageResponse
│   │   ├── chat.py                              # ChatRequest（message + file_ids）
│   │   ├── memory.py                            # MemoryResponse, CreateMemoryRequest
│   │   └── file.py                              # FileResponse, UploadResponse
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                              # POST send-code / register / login
│   │   ├── user.py                              # GET/PUT profile
│   │   ├── session.py                           # POST/GET/DELETE sessions, GET messages
│   │   ├── chat.py                              # POST /api/chat/{session_id} → SSE
│   │   ├── upload.py                            # POST upload, GET/DELETE files
│   │   ├── feedback.py                          # POST feedback
│   │   ├── memory.py                            # GET/POST/DELETE memories
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py                      # 注册登录逻辑、JWT 生成验证、验证码校验
│   │   ├── email_service.py                     # 发送验证码邮件（Resend）
│   │   ├── session_service.py                   # 会话 CRUD、标题自动生成
│   │   ├── file_service.py                      # 文件存储、类型校验（仅图片/音频）、删除
│   │
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── queue.py                             # Task 数据类、全局 asyncio.Queue
│   │   └── runner.py                            # worker_loop 协程：FIFO 取任务、跑 Agent、塞事件
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                             # LangGraph 状态图定义、注册节点和边、compile
│   │   ├── state.py                             # PassAgentState TypedDict
│   │   ├── planner.py                           # Planner 节点：Function Calling 决策
│   │   ├── response.py                          # Respond 节点：生成回复（含引导建议）
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── reader.py                        # retrieve_memory 节点：全量偏好 + 语义检索 FACT
│   │   │   ├── writer.py                        # write_memory 节点：LLM 提取 → embedding → 存 DB
│   │   │   └── embedding.py                     # embedding 模型加载、向量生成、余弦相似度
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── strength/
│   │       │   ├── __init__.py
│   │       │   ├── zxcvbn_tool.py               # 熵值评估
│   │       │   ├── charset_tool.py              # 字符组成分析
│   │       │   ├── keyboard_tool.py             # 键盘模式检测
│   │       │   ├── weak_list_tool.py            # 弱口令库匹配
│   │       │   ├── repetition_tool.py           # 重复字符和序列检测
│   │       │   ├── pcfg_tool.py                 # 结构模式分析
│   │       │   ├── passgpt_tool.py              # 口令概率（调模型服务）
│   │       │   ├── pass2rule_tool.py            # 口令规则生成（调模型服务）
│   │       │   ├── pinyin_tool.py               # 拼音组合检测
│   │       │   ├── date_tool.py                 # 日期模式检测
│   │       │   └── personal_info_tool.py        # 结合记忆检测个人信息
│   │       ├── generation/
│   │       │   ├── __init__.py
│   │       │   ├── multimodal_tool.py           # 图片/音频转文本（调 Qwen-Omni）
│   │       │   ├── generate_tool.py             # 种子词变换生成口令
│   │       │   ├── passphrase_tool.py           # 助记短语型口令
│   │       │   ├── pronounceable_tool.py        # 可发音随机口令
│   │       │   ├── site_policy_tool.py          # 网站密码策略
│   │       │   └── strength_verify_tool.py      # 生成口令反向验证强度
│   │       ├── recovery/
│   │       │   ├── __init__.py
│   │       │   ├── fragment_tool.py             # 片段排列组合
│   │       │   ├── variant_tool.py              # 常见变体扩展
│   │       │   ├── rule_tool.py                 # hashcat 规则生成（调模型服务）
│   │       │   └── date_expand_tool.py          # 日期格式扩展
│   │       ├── leak/
│   │       │   ├── __init__.py
│   │       │   ├── hibp_password_tool.py        # k-Anonymity 查密码泄露
│   │       │   ├── hibp_email_tool.py           # 查邮箱关联泄露事件
│   │       │   ├── breach_detail_tool.py        # 泄露事件详情
│   │       │   └── similar_leak_tool.py         # 常见变体批量查泄露
│   │       └── graphical/
│   │           ├── __init__.py
│   │           ├── graphical_mode_tool.py       # 唤起前端图形口令组件
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm_client.py                       # 调模型推理服务的统一客户端（OpenAI 兼容接口）
│   │   ├── security.py                         # bcrypt 密码哈希、JWT 编解码
│   │   └── deps.py                             # FastAPI 依赖注入（get_current_user）
│   │
│   ├── data/
│   │   ├── weak_passwords/
│   │   │   ├── top100.txt
│   │   │   ├── top1000.txt
│   │   │   └── rockyou_sample.txt
│   │   ├── keyboard_patterns.json
│   │   ├── pinyin_dict.json
│   │   ├── leet_map.json
│   │   ├── syllables.json
│   │   ├── wordlist_zh.txt
│   │   ├── wordlist_en.txt
│   │   └── site_policies.json
│   │
│   └── uploads/                                 # 用户上传文件存储（.gitignore）
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.mjs
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── postcss.config.js
│   ├── public/
│   │   ├── logo.svg
│   │   └── favicon.ico
│   └── src/
│       ├── app/
│       │   ├── layout.tsx                       # 根布局
│       │   ├── page.tsx                        # 首页（未登录：Logo + 介绍 + 登录入口）
│       │   ├── login/
│       │   │   └── page.tsx                    # 登录页
│       │   ├── register/
│       │   │   └── page.tsx                    # 注册页（邮箱 + 验证码 + 密码）
│       │   └── chat/
│       │       ├── layout.tsx                  # 聊天页布局（侧边栏 + 主区域）
│       │       ├── page.tsx                    # 新对话默认页（Logo + 欢迎 + 输入框）
│       │       └── [sessionId]/
│       │           └── page.tsx                # 具体对话页（消息列表 + 输入框）
│       ├── components/
│       │   ├── ui/
│       │   │   ├── button.tsx
│       │   │   ├── input.tsx
│       │   │   ├── modal.tsx
│       │   │   ├── spinner.tsx
│       │   │   └── toast.tsx
│       │   ├── sidebar/
│       │   │   ├── sidebar.tsx                 # 侧边栏主组件（收起/展开）
│       │   │   ├── session-list.tsx            # 历史会话列表（含模糊搜索）
│       │   │   ├── session-item.tsx            # 单个会话项（标题 + 时间 + 删除）
│       │   │   └── user-menu.tsx               # 用户菜单（设置、帮助、退出登录）
│       │   ├── chat/
│       │   │   ├── message-list.tsx            # 消息列表容器（滚动、自动滚底）
│       │   │   ├── message-item.tsx            # 单条消息（区分 human/assistant）
│       │   │   ├── assistant-message.tsx       # assistant 消息（agent-steps 折叠 + 正文 + 操作栏）
│       │   │   ├── agent-steps.tsx             # Agent 执行步骤条（🔄 / ✅）
│       │   │   ├── chat-input.tsx              # 输入框（文本 + 文件上传按钮 + 发送）
│       │   │   ├── file-preview.tsx            # 已选文件预览（缩略图 + 删除）
│       │   │   ├── message-actions.tsx         # 消息操作栏（复制、点赞、点踩、重新生成、导出PDF）
│       │   │   └── queue-status.tsx            # 排队状态提示（"前方还有N个任务"）
│       │   ├── graphical/
│       │   │   ├── graphical-modal.tsx         # 图形口令弹窗容器
│       │   │   ├── image-picker.tsx            # 图片选点组件
│       │   │   └── map-picker.tsx              # 地图选点组件
│       │   └── settings/
│       │       ├── settings-modal.tsx          # 设置弹窗
│       │       ├── appearance-tab.tsx          # 外观设置（主题切换）
│       │       └── memory-tab.tsx              # 记忆管理（查看、添加、删除）
│       ├── hooks/
│       │   ├── use-auth.ts                     # 登录状态管理、token 存取
│       │   ├── use-chat.ts                     # 发送消息、SSE 流处理、消息状态管理
│       │   ├── use-sessions.ts                 # 会话列表 CRUD
│       │   ├── use-memories.ts                 # 记忆 CRUD
│       │   └── use-files.ts                    # 文件上传、列表、删除
│       ├── lib/
│       │   ├── api.ts                          # fetch 封装（baseURL、token 注入、错误处理）
│       │   ├── sse.ts                          # SSE 流解析工具（读取 event + data）
│       │   └── utils.ts                        # 通用工具函数（格式化时间、文件大小等）
│       ├── providers/
│       │   ├── auth-provider.tsx               # 认证上下文（token、user 信息）
│       │   └── theme-provider.tsx              # 主题上下文（light/dark）
│       └── styles/
│           └── globals.css                     # 全局样式、Tailwind 导入
│
├── model_service/
│   ├── Dockerfile                              # 基于 vLLM 镜像
│   ├── entrypoint.sh                           # 启动脚本：加载模型、启动 vLLM
│   ├── config.yaml                             # 模型配置（路径、量化方式、常驻/按需）
│   └── models/                                 # 模型权重（.gitignore）
│       ├── .gitkeep
│       └── README.md                           # 说明如何下载模型权重
│
└── scripts/
    ├── init_db.sh                              # 初始化数据库
    ├── download_models.sh                      # 下载模型权重
    └── download_wordlists.sh                   # 下载弱口令库

```
