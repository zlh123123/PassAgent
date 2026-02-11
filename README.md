# PassAgent - 基于 LLM Agent 的口令安全助手

<div align="center">

![PassAgent Logo](https://img.shields.io/badge/PassAgent-🔐-blue?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*基于 LangGraph 多步推理 Agent 的口令安全分析、生成与记忆恢复系统*

[功能特性](#功能特性) • [系统架构](#系统架构) • [快速开始](#快速开始) • [项目结构](#项目结构)

</div>

## 项目简介

PassAgent 是一个基于大语言模型 Agent 的口令安全助手。系统采用 LangGraph 构建多步推理 Agent，通过 Planner 节点自主决策工具调用链路，结合用户记忆系统实现个性化服务。支持口令强度评估、智能口令生成、口令记忆恢复、泄露检查和图形口令等场景。

## 功能特性

### 口令强度评估
- zxcvbn 熵值评估、字符组成分析、键盘模式检测
- 弱口令库匹配（Top100 / Top1000 / RockYou）
- 重复字符检测、PCFG 结构模式分析
- PassGPT 概率估计、Pass2Rule 规则变换分析
- 拼音组合检测、日期模式检测
- 结合用户记忆的个人信息关联检测

### 智能口令生成
- 基于种子词（个人信息、偏好）的变换生成
- 助记短语型口令、可发音随机口令
- 多模态输入支持：上传图片/音频，由 Qwen-Omni 提取关键词作为生成素材
- 自动获取目标网站密码策略，确保生成结果合规
- 生成后自动反向验证强度

### 口令记忆恢复
- 片段排列组合 + 常见变体扩展
- Hashcat 规则生成（微调模型）
- 日期格式扩展
- 结合用户记忆中的事实线索辅助恢复

### 泄露检查
- HIBP k-Anonymity 密码泄露查询
- 邮箱关联泄露事件查询
- 泄露事件详情查看
- 常见变体批量泄露检查

### 图形口令
- 图片选点口令、地图选点口令

### 用户记忆系统
- 三类记忆：PREFERENCE（偏好）、FACT（事实）、CONSTRAINT（约束）
- Agent 自动从对话中提取记忆，支持用户手动管理
- 语义检索：text2vec-base-chinese 向量化 + 余弦相似度匹配
- 全量偏好/约束 + Top-K 语义事实的两阶段检索策略

## 系统架构

```
┌──────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   Frontend   │────▶│   Backend + Agent    │────▶│   Model Service     │
│   (Next.js)  │ SSE │   (FastAPI+LangGraph)│HTTP │   (vLLM)            │
│   Port 3000  │◀────│   Port 8000          │◀────│   Port 8080         │
└──────────────┘     └──────────┬───────────┘     └─────────────────────┘
                                │                   GPU Container
                                ▼                   - Qwen2.5-7B (4bit) 常驻
                     ┌──────────────────┐           - Qwen-1.7B 微调 (4bit) 常驻
                     │   SQLite         │           - Qwen-Omni-7B (4bit) 按需
                     │   passagent.db   │
                     └──────────────────┘
```

### Agent 工作流

```
START → Planner(LLM决策) → Router(条件分支) → Tool(执行) → 回到Planner
                ↓ action=="respond"
            Respond(生成回复) → Write Memory(写入记忆) → END
```

Planner 通过 Function Calling 自主决策调用哪些工具，支持跨 skill 组合调用，最大循环 10 次。

### 任务队列

单 Worker 协程 FIFO 处理，每个 Task 持有独立的 `asyncio.Queue` 作为 Worker 与 SSE 连接之间的事件桥梁，支持多用户排队。

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 20+
- 支持 CUDA 的 GPU（模型推理服务）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/zlh123123/PassAgent.git
   cd PassAgent
   ```

2. **后端**
   ```bash
   cd backend
   uv sync          # 安装 Python 依赖
   cp .env.example .env
   # 编辑 .env，配置 JWT 密钥、邮件服务、HIBP API Key 等
   ```

3. **前端**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   ```

4. **模型服务**
   ```bash
   bash scripts/download_models.sh    # 下载模型权重
   ```

5. **初始化数据库**
   ```bash
   bash scripts/init_db.sh
   ```

6. **Docker 部署**
   ```bash
   docker-compose up -d
   ```

7. **访问**
   - 前端：http://localhost:3000
   - 后端 API：http://localhost:8000
   - 模型服务：http://localhost:8080

## 项目结构

```
PassAgent/
├── backend/
│   ├── main.py                          # FastAPI 入口
│   ├── config.py                        # 环境变量、常量配置
│   ├── database/                        # SQLite 连接、ORM 模型、建表
│   ├── schemas/                         # Pydantic 请求/响应模型
│   ├── routers/                         # API 路由（auth/user/session/chat/upload/feedback/memory）
│   ├── services/                        # 业务逻辑（认证/邮件/会话/文件）
│   ├── worker/                          # 任务队列 + Worker 协程
│   ├── agent/
│   │   ├── graph.py                     # LangGraph 状态图定义
│   │   ├── state.py                     # Agent 状态 TypedDict
│   │   ├── planner.py                   # Planner 节点（Function Calling 决策）
│   │   ├── response.py                  # Respond 节点（生成回复 + 引导建议）
│   │   ├── memory/                      # 记忆读取、写入、embedding
│   │   └── tools/                       # 工具集
│   │       ├── strength/                #   强度评估（11 个工具）
│   │       ├── generation/              #   口令生成（6 个工具）
│   │       ├── recovery/                #   记忆恢复（4 个工具）
│   │       ├── leak/                    #   泄露检查（4 个工具）
│   │       └── graphical/               #   图形口令（1 个工具）
│   ├── utils/                           # LLM 客户端、安全工具、依赖注入
│   └── data/                            # 弱口令库、键盘模式、拼音字典等
│
├── frontend/                            # Next.js 前端
│   └── src/
│       ├── app/                         # 页面（首页/登录/注册/聊天）
│       ├── components/                  # 组件（sidebar/chat/graphical/settings）
│       ├── hooks/                       # 自定义 hooks（auth/chat/sessions/memories/files）
│       ├── lib/                         # API 封装、SSE 解析、工具函数
│       └── providers/                   # Context Providers（auth/theme）
│
├── model_service/                       # vLLM 模型推理服务
├── scripts/                             # 初始化、模型下载脚本
└── docker-compose.yml
```

## API 概览

所有接口（除 auth 外）需要 `Authorization: Bearer <jwt_token>`。

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/send-code` | 发送验证码 |
| | `POST /api/auth/register` | 注册 |
| | `POST /api/auth/login` | 登录 |
| 用户 | `GET/PUT /api/user/profile` | 获取/更新个人信息 |
| 会话 | `POST/GET /api/sessions` | 创建/列表会话 |
| | `DELETE /api/sessions/{id}` | 删除会话 |
| | `GET /api/sessions/{id}/messages` | 获取消息历史 |
| 对话 | `POST /api/chat/{session_id}` | 发送消息（SSE 流式响应） |
| 文件 | `POST /api/upload` | 上传图片/音频 |
| | `GET /api/files` | 文件列表 |
| | `DELETE /api/files/{id}` | 删除文件 |
| 反馈 | `POST /api/messages/{id}/feedback` | 点赞/点踩 |
| 记忆 | `GET/POST /api/memories` | 查看/添加记忆 |
| | `DELETE /api/memories/{id}` | 删除记忆 |

核心对话接口 `POST /api/chat/{session_id}` 通过 SSE 推送 `task_queued` → `task_started` → `agent_step` → `response_chunk` → `response_done` → `done` 事件流。

详细 API 文档见 [API.md](API.md)。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 15, React, TypeScript, Tailwind CSS |
| 后端 | FastAPI, LangGraph, SQLAlchemy, Pydantic |
| 模型推理 | vLLM, Qwen2.5-7B, Qwen-Omni-7B |
| 数据库 | SQLite |
| 向量化 | text2vec-base-chinese |
| 部署 | Docker Compose |

## 许可证

MIT License - 见 [LICENSE](LICENSE)。
