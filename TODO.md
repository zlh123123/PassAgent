# 前端界面

## 登录注册界面
- [ ] 这个还是要尽快做一下，用交大邮箱注册，验证码、忘记密码等

## 侧边栏

收起状态下，
- [ ] Logo放最左上角
- [ ] Logo下方是新建对话、查看上传过的文件、询问记录三个按钮（仅icon）
- [ ] 最下方为用户头像，用户头像下方为侧边栏缩回伸出按钮
- [ ] 点击用户头像，出现设置、帮助、退出登录这些功能
- [ ] 设置包括头像、外观、模型API
- [ ] 设置这里还要考虑修改密码

伸出状态下，
- [ ] Logo放最左上角，如果左边有空位的话加上PassAgent的名字
- [ ] Logo下方是新建对话、查看上传过的文件、询问记录三个按钮（icon+文字说明）
- [ ] 历史记录项展示所有的历史记录
- [ ] 历史记录按时间排序（时间可展示）
- [ ] 历史记录提供模糊搜索功能
- [ ] 最下方是用户头像，用户头像的右侧为侧边栏缩回伸出按钮

## 主界面
- [ ] 欢迎使用 PassAgent🤗改成Logo+名称
- [ ] 上传文件功能在输入聊天框时要显示

## 对话界面
- [ ] 主要是要展示运行顺序，以及实现流式输出，这个可以采用LangGraph的SSE数据包实现，后续调研一下
- [ ] 每一个回复添加重新生成、复制、点赞、点踩以及导出到PDF的按钮

# 数据库设计

1. users（用户表）
- user_id (主键)
- email (唯一，交大邮箱)
- password_hash (加密密码)
- avatar_url (头像URL)
- theme (外观设置：light/dark)
- created_at (注册时间)
2. user_api_configs（用户API配置表）
- config_id (主键)
- user_id (外键 → users)
- model_type (qwen/deepseek/local)
- api_key (加密存储)
- model_name (具体模型名称)
- is_default (是否默认使用)
- created_at
3. sessions（会话表）
- session_id (主键)
- user_id (外键 → users)
- title (会话标题)，这一步可以通过LLM做
- created_at
- updated_at
4. messages（消息表）
- message_id (主键)
- session_id (外键 → sessions)
- user_id (外键 → users)
- content (消息内容)
- message_type (user/assistant)
- created_at
5. feedback（用户反馈表）
- feedback_id (主键)
- message_id (外键 → messages，唯一)
- user_id (外键 → users)
- feedback_type (like/dislike/null)
- created_at
6. uploaded_files（上传文件表）
- file_id (主键)
- user_id (外键 → users)
- session_id (外键 → sessions，可选关联)
- filename (原文件名)
- file_path (存储路径)
- file_size (文件大小)
- file_type (MIME类型)
- uploaded_at
7. password_analysis（密码分析记录表）
- analysis_id (主键)
- session_id (外键 → sessions)
- user_id (外键 → users)
- original_password_hash (原密码哈希)
- target_password_hash (目标密码哈希)
- hashcat_rule (生成的规则)
- strength_score (强度评分 0-100)
- is_leaked (是否泄露)
- analysis_type (transformation/strength/recommendation)
- created_at
- 这张表格打算根据不同analysis_type，提供对应不同的metadata进行说明

8. user_memories (用户记忆表)

memory_id (主键)

user_id (外键 → users)

content (文本内容): 例如 "宠物是一只名叫旺财的狗", "喜欢使用特殊符号 # 和 @", "生日是 1995年"

memory_type (枚举):

+ PREFERENCE: 偏好（如：喜欢强密码、不喜欢包含 'l' 和 '1'）

+ FACT: 事实/背景（如：公司名、宠物名、纪念日）

+ CONSTRAINT: 约束（如：密码长度通常设为16位）

embedding (向量数据, Blob/Array): 用于语义匹配 (Optional, 推荐)

created_at: 创建时间

last_accessed_at: 最后一次被调用的时间（用于LRU或权重计算）


# 后端

MCP这块要改用langgraph框架，需要更新后端文件架构

# 5个需求
需求分类：BERT-wwm-ext (Whole Word Masking) 或 RoBERTa-wwm-ext

https://huggingface.co/hfl/chinese-roberta-wwm-ext
https://github.com/ymcui/Chinese-BERT-wwm

🛡️ Agent 功能需求清单 (User-Facing Features) v2.0
1. 口令强度评估 (Strength Assessment)
含义： 用户提供一个现有的文本口令，Agent 分析其安全性。
用户输入示例：
“帮我看看 123456 安全吗？”
“测试一下我的密码强度。”
Agent 行为： 计算熵值、检查字符组合、匹配常见弱口令列表，给出评分（弱/中/强）及改进建议。
主要4个功能：zxcvbn（熵值）、PCFG（结构分析）、passgpt（概率）、LLM（口令重用）
在此功能下还需要提供口令增强的建议，这个的具体做法还需要再考虑一下
3. 口令生成与推荐 (Password Generation)
含义： 用户需要一个新的、安全的文本口令。支持多种输入形式作为“种子”，生成既安全又包含用户个性化信息的口令。
输入形式支持：
纯文本助记符： 用户直接输入关键词（如“zly”, “2023”）。
多模态信息（图片/音频）： 用户上传图片（如宠物照、风景照）或音频（如一段话、环境音）。
用户输入示例：
“我要注册一个新账号，帮我生成个密码。”
“用这张猫的照片帮我生成一个密码。”（上传图片）
“根据这段录音生成一个口令。”（上传音频）
“我要注册 GitHub，帮我生成一个符合要求的密码。”（触发隐式爬虫/规则库）
Agent 行为：
多模态解析： 调用 Qwen2-Audio / Qwen2-VL (或 Qwen-Omni) 模型，将图片/音频内容转换为文本描述（如图片 -> "cat_sleeping_sofa"，音频 -> "hello_world"）。
生成逻辑： 将解析出的文本或用户输入的文本作为助记词，通过变换大小写、插入特殊符号、乱序等方式增强安全性。
合规适配： 如果识别到目标网站，自动加载该网站的密码策略进行适配。
4. 模糊记忆恢复 (Memory Recovery)
含义： 用户忘记了旧密码，但记得一些片段。Agent 帮助用户“拼凑”出可能的密码列表，而不是生成新密码。
用户输入示例：
“我忘了旧密码，只记得里面有 zly 和 2023。”
“帮我找回密码，好像是 admin 开头，后面是个年份。”
Agent 行为： 基于用户提供的片段，进行排列组合（不随意添加随机字符），生成一份“可能的密码候选列表”供用户尝试。
5. 口令泄露检查 (Leak Check)
含义： 检查用户的口令或账号是否出现在已知的互联网数据泄露事件中（基于 HIBP 等库）。
用户输入示例：
“查一下 password123 有没有泄露过。”
“我的邮箱 test@example.com 安全吗？”
Agent 行为： 查询泄露数据库，返回泄露次数或安全状态。
6. 图形口令设置 (Graphical Password) [独立模式]
含义： 提供一种非文本的口令设置方式，允许用户通过在图片或地图上选点来作为凭证（不涉及文本转换，位置即密码）。
用户输入示例：
“我想设置一个图形密码。”
“启动地图口令模式。”
“我想用图片做密码。”
Agent 行为： 识别到该意图后，唤起前端的图形交互组件（弹窗或 Webview），引导用户进行选点操作。
📝 意图分类标签更新
STRENGTH_CHECK (强度评估)
GENERATION (生成推荐 - 支持 文本/图片/音频 输入)
RECOVERY (记忆恢复)
LEAK_CHECK (泄露检查)
GRAPHICAL_MODE (图形口令 - 独立入口)

# 这里还需要加一个记忆模块

这里估计要另外设计一张表，就负责保存用户偏好，然后就除了用户输入的原始密码不能存之外其他都可以存

在对用户进行回复的时候要考虑一下用户的输出和记忆模块中的东西

对于记忆写入，基本上就是对于口令推荐和模糊记忆恢复这两个功能；剩下三个功能用户只需要提供待处理的口令即可，这些口令不写入记忆

对于记忆读取，就是作为口令推荐和模糊记忆恢复这两个功能的第一步：

调用策略：

全量检索 (针对全局偏好)： 总是拉取 memory_type = PREFERENCE 的最近几条记录（例如：“用户不喜欢用问号”）。

语义检索 (针对特定任务)：

当进入 口令生成 (Generation) 或 记忆恢复 (Recovery) 模式时。

使用用户的当前 Query 生成向量，去 user_memories 中检索 Top-K 最相关的事实。

例子： 用户输入 "帮我生成一个包含我女儿名字的密码"。

检索： 检索到记忆 "女儿的名字叫 Alice"。


最后有关这个模块也可以给用户提供自定义，就像gemini的记忆功能一样，用户输入自己的句子即可+

# 整体的流程

graph TD
    %% --- 样式定义 ---
    classDef user fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef brain fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef memory fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef action fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    
    %% --- 角色 ---
    User((👤 用户)):::user
    
    %% --- 核心大脑 ---
    subgraph Agent_Brain [🤖 PassAgent 核心大脑]
        direction TB
        Intent[1. 意图识别 &<br>关键词提取]:::brain
        Logic[2. 逻辑分发 &<br>参数组装]:::brain
        Response[4. 结果整合 &<br>回复生成]:::brain
    end

    %% --- 记忆模块 ---
    subgraph Memory_System [🧠 记忆系统]
        MemDB[(长期记忆库<br>User Preferences<br>& Facts)]:::memory
        MemRead{读取记忆}:::memory
        MemWrite{写入/更新记忆}:::memory
    end

    %% --- 功能执行层 ---
    subgraph Capabilities [🛠️ 功能执行层]
        Strength[🛡️ 强度评估]:::action
        Gen[🔑 口令生成]:::action
        Recover[🧩 记忆恢复]:::action
        Leak[⚠️ 泄露检查]:::action
        Graph[🎨 图形口令]:::action
    end

    %% --- 流程连线 ---
    
    %% 1. 输入与理解
    User -- "输入指令/文件" --> Intent
    
    %% 2. 记忆读取 (辅助理解和参数补充)
    MemDB -.-> MemRead
    MemRead -- "检索偏好/背景" --> Intent
    
    %% 3. 逻辑分发 (将 提取的参数 + 记忆上下文 传给工具)
    Intent --> Logic
    
    %% 4. 执行具体功能
    Logic -- "分发任务" --> Strength & Gen & Recover & Leak & Graph
    
    %% 5. 结果返回
    Strength & Gen & Recover & Leak & Graph --> Response
    
    %% 6. 记忆写入 (关键步骤：复用提取的信息)
    Intent -- "提取到的新事实<br>(非敏感信息)" --> MemWrite
    MemWrite -.-> MemDB
    
    %% 7. 最终反馈
    Response -- "流式输出" --> User
---

不同推理参数：beam search没有topk、tem这些参数

不同训练集大小：数据合成方式？

不同模型：当时在微信群里说了，不同参数量的模型在性能方面差异不大，选用那种没有经过指令微调的模型效果更好，最后选的是qwen1.7b。后续也可以换其他型号模型测试

横向对比

生成量：top66到top100的变化不大，最高测试top500（显存生成top1000不够），目前top500的准确率有75%

此外测试的有：训练集的不同提示词（这个结果是当top比较小的时候有一些提升，高top下基本没提升）

不同训练的学习率：测试了更高学习率，发现对于简单规则性能提升，复杂规则性能下降，估计是在简单规则上有点过拟合

统计了我们的模型能猜出不在best66里的规则的占比：（这个在passllm里也干了）

qwen3-1.7b_withprompt:

处理数据集: test_results_complex.json

模型成功: 35

Best66 成功: 16

重叠: 13

模型独有成功: 22

处理数据集: test_results_simple.json

模型成功: 73

Best66 成功: 82

重叠: 61

模型独有成功: 12

处理数据集: test_set.json

模型成功: 71

Best66 成功: 57

重叠: 45

此外，考虑会不会是因为将原子规则作为token，那测试集中如果存在没训进去的规则，那模型一定不会输出。但实际上看下来并非，而且将所有规则都token化并不现实

---

毕设这块，最开始的意图识别agent是先用RoBERTa-wwm-ext区分出大类（目前是5个功能+其他），再针对每个大类去单独设计提示词用LLM去提取关键词。目前是把RoBERTa-wwm-ext的微调训完了（这个的数据集是用deepseek合成的，在测试集上准确率有99以上，还测试了推理速度，非常快可以忽略不计）

然后，目前在做关键词提取的测试集用来测试设计的提示词的准确率。但是这里对于强度评估和泄露检查以及多因子认证三个功能比较好实现（相当于前两个提取口令即可，多因子认证提取是用图片还是地图即可），但是对于口令推荐和记忆恢复两功能如何提取还需要考虑

最后就是在前端界面这块，一是设计了一个首页，而是对于聊天界面，换用了langgraph的一个开源UI框架，这个是用react做的，对于流式传输有支持，就不需要另外开发了

---

然后就是可能需要补充的实验：

+ pass2edit里的跨站攻击
+ passllm中不同模型、不同提示词、不同训练集大小对性能的影响
+ 撞库性能：为了发挥hsahcat的性能，比如我先对着一个小密码集（N个）中每个密码都生成top-66的规则，然后在这66\*N个规则中取出现概率最高的M个规则，把这些规则用上后，能生成M\*N个口令，拿去撞大的密码库
+ 
