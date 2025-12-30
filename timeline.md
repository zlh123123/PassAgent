📅 第一阶段：基础设施与后端骨架 (Month 1)
目标： 跑通“数据流”。前端能调通登录，后端能加载模型，数据库跑起来。

第 1 周：项目初始化与数据库

[ ] Repo 搭建： 建立 Monorepo 结构，配置 Docker Compose。

[ ] 数据库设计： 实现 SQLAlchemy Models (users, sessions, messages, memories 等所有表)。

[ ] 基础服务： 搭建 FastAPI 框架，配置 Alembic 迁移工具。

[ ] 鉴权模块： 完成注册（交大邮箱验证）、登录、JWT Token 发放。

第 2 周：模型服务部署 (The Engine)

[ ] vLLM 部署： 在 Docker 中配置 vLLM，加载 几个LLM，测试 API 通断。

[ ] RoBERTa 集成： 在 FastAPI 内部写好 IntentClassifier 类，加载微调好的权重，测试推理速度。这个推理速度应该没问题，具体代码可以在第三周完成

[ ] Prompt 调试： 在 Playground 测试 Qwen 对“关键词提取”和“密码生成”的 Prompt 效果。

第 3 周：LangGraph 骨架搭建

[ ] State 定义： 定义 AgentState (messages, user_id, memories, etc.)。

[ ] Graph 编排： 写好 workflow，添加 Node 占位符（Start -> Intent -> ... -> End）。

[ ] 意图识别节点： 将 RoBERTa 接入 Graph，实现基于意图的路由逻辑。

第 4 周：工具库准备 (Tools Pre-work)

[ ] 封装基础工具： 编写 Python 函数封装 zxcvbn (强度), HIBP API (泄露), Hashcat (简单的命令行调用 wrapper)。这些比较好搞一些

[ ] 单元测试： 确保这些工具函数在不依赖 LLM 的情况下能独立工作。

🧠 第二阶段：Agent 核心逻辑与记忆模块 (Month 2)
目标： 后端 Agent 具备“智能”。能听懂人话，能记住偏好，能生成和恢复密码。

第 5 周：核心功能开发 - A组 (生成与评估)

[ ] 强度评估流： 完成 StrengthNode，对接 PassGPT（或规则库）+ Zxcvbn。

[ ] 口令生成流： 完成 GenNode，实现 LLM 提取参数 -> 规则生成 -> 验证 的闭环。

[ ] 关键词提取： 编写负责“槽位填充”的 LLM 调用逻辑，并输出 JSON。

第 6 周：核心功能开发 - B组 (恢复与记忆)

[ ] 记忆模块 (核心难点)： 实现 ContextRetriever (读) 和 MemoryExtractor (写)。处理向量存储或简单的 SQL 模糊匹配。

[ ] 模糊恢复流： 结合记忆模块，实现“从记忆中提取线索 -> 生成 Hashcat Mask/字典”的逻辑。

第 7 周：API 封装与 SSE 流式输出

[ ] 流式改造： 改造 LangGraph 的输出，使其通过 FastAPI 的 StreamingResponse 返回 SSE 格式数据。

[ ] 完善 API： 聊天接口 /api/chat，历史记录接口，文件上传接口。

第 8 周：后端联调与中间期缓冲

[ ] 集成测试： 模拟完整对话流程，修复状态传递中的 Bug。

[ ] Buffer Week： 处理之前遗留的难题（通常 Hashcat 的集成或 vLLM 的显存管理会出点问题）。

💻 第三阶段：前端开发与全栈联调 (Month 3)
目标： 界面美观，交互流畅，所见即所得。

第 9 周：前端框架与侧边栏

[ ] Next.js 初始化： 安装 Shadcn UI, Tailwind。

[ ] 侧边栏实现： 完成折叠/展开、历史记录列表、用户信息展示。

[ ] 设置页面： 头像修改、模型切换、主题切换。

第 10 周：聊天核心交互

[ ] 流式渲染： 编写 useChatStream Hook，解析 SSE 数据，实现打字机效果。

[ ] Markdown 渲染： 配置 React-Markdown，支持代码块高亮、表格渲染。

[ ] 多模态输入 UI： 实现图片/文件上传组件，在输入框中预览。

第 11 周：特色功能 UI

[ ] 图形口令组件： 实现地图选点/图片选点的前端交互逻辑。

[ ] 消息操作： 实现点赞/点踩、复制、导出 PDF 功能。

[ ] 反馈系统： 将点赞数据回传给后端 API。

第 12 周：全栈联调与优化

[ ] End-to-End 测试： 从登录到生成密码全流程跑通。

[ ] 性能优化： 优化首屏加载，优化 LLM 响应延迟（预加载等）。

📝 第四阶段：实验、论文与收尾 (Month 4)
目标： 产出毕设所需的“数据”和“文档”。代码只是载体，论文才是产出。

第 13 周：实验数据收集 (Crucial for Thesis)

[ ] 消融实验： 跑脚本，测试“有无记忆模块”、“有无意图识别(RoBERTa vs LLM)”对成功率的影响。

[ ] 性能基准： 测试不同模型 (Qwen 1.5B vs 7B) 在密码猜解上的准确率 (Top-100)。

[ ] 攻击实验： 运行 Hashcat 撞库实验，收集破解率数据。

第 14 周：论文撰写 & 数据可视化

[ ] 绘图： 画架构图（就是刚才那个 Mermaid 的详细版）、时序图、实验数据柱状图。

[ ] 撰写： 完成论文的“系统设计”、“实验评估”章节。

[ ] 演示准备： 录制 Demo 视频（防止答辩时现场翻车）。

第 15 周：最终修补 (Polish)

[ ] Bug Fix： 修复边界条件下的 Crash。

[ ] UI 美化： 统一色调，调整间距。

[ ] 文档： 完善 GitHub README，编写部署文档。

第 16 周：答辩准备

[ ] PPT 制作。

[ ] 模拟答辩。
