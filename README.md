# PassAgent - 基于LLM的密码安全智能助手

<div align="center">

![PassAgent Logo](https://img.shields.io/badge/PassAgent-🔐-blue?style=for-the-badge)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20-61DAFB.svg?logo=react&logoColor=white)](https://reactjs.org)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg?style=flat&logo=anthropic)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*一个集成多种AI技术的密码安全分析与推荐系统*

[功能特性](#功能特性) • [快速开始](#快速开始) • [项目架构](#项目架构) • [开发指南](#开发指南)

</div>

## 📋 项目简介

PassAgent 是一个基于大语言模型(LLM)的智能密码安全助手，旨在为用户提供全方位的密码安全服务。系统集成了密码转换分析、强度评估、安全检测、智能推荐等多项功能，通过AI技术帮助用户构建更安全的密码防护体系。

## ✨ 功能特性

### 🔄 密码转换分析
- **Hashcat规则生成**：分析两个密码之间的转换关系，自动生成对应的Hashcat规则
- **转换验证**：验证生成规则的正确性和有效性
- **批量分析**：支持大规模密码对的批量转换分析

### 🛡️ 密码强度评估
- **多维度评估**：结合传统算法、LLM分析和PassGPT等多种评估方法
- **实时评分**：提供0-100的强度评分和详细的安全建议
- **可视化展示**：直观展示密码的各项安全指标

### 🔍 安全检测
- **泄露检测**：基于海量泄露数据库检测密码是否已被泄露
- **合规性检查**：验证密码是否符合各种安全策略和行业标准
- **风险评估**：综合评估密码的安全风险等级

### 💡 智能密码推荐
- **文本语义推荐**：基于用户输入的文本描述生成个性化密码
- **图像内容推荐**：分析上传图片内容，生成相关的安全密码
- **地理位置推荐**：结合地图选点信息，生成易记且安全的密码
- **个性化定制**：根据用户偏好和安全要求定制推荐策略

### 🤖 多模态AI支持
- **大语言模型集成**：支持Qwen、Deepseek等多种LLM
- **计算机视觉**：图像内容理解和特征提取
- **意图理解**：自动识别用户的密码安全需求
- **工具编排**：智能选择和组合不同的安全分析工具

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js v20.10.0 (可选，用于前端开发)
- npm 10.2.5
- 8GB+ RAM
- 支持CUDA的GPU (可选，用于本地模型推理)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/zlh123123/PassAgent.git
   cd PassAgent
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置API密钥等信息
   ```

4. **初始化数据库**
   ```bash
   python scripts/init_database.py
   ```

5. **启动应用**
   ```bash
   python scripts/start_app.py
   ```

6. **访问应用**
  🌐 Web界面: http://localhost:8080


## 📁 项目结构



## 🔧 API文档

### 主要接口

#### 密码转换分析
```http
POST /api/v1/password/analyze/transformation
Content-Type: application/json

{
    "original_password": "password123",
    "target_password": "Password123!"
}
```

#### 密码强度评估
```http
POST /api/v1/password/analyze/strength
Content-Type: application/json

{
    "password": "MySecurePassword123!"
}
```

#### 密码推荐
```http
POST /api/v1/password/recommend
Content-Type: application/json

{
    "type": "text",
    "content": "我喜欢猫咪和咖啡",
    "requirements": {
        "length": 12,
        "include_special": true,
        "include_numbers": true
    }
}
```



## 🏗️ 项目架构

### 技术栈
- **后端框架**: FastAPI + uvicorn + MCP
- **前端框架**: React 18 + TypeScript + Ant Design
- **数据库**: SQLite + Milvus (向量数据库)
- **AI模型**: Qwen, Deepseek, PassGPT等
- **部署方案**: Docker + Docker Compose

### 系统架构图





## 📊 功能演示



## 🐳 Docker 部署

### 快速部署
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 生产环境部署
```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d
```



## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献方式
- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有贡献者的辛勤工作
- 感谢开源社区提供的优秀工具和库
- 特别感谢 Hashcat、PassGPT 等项目的启发

## 📞 联系我们

- **项目主页**: https://github.com/zlh123123/PassAgent
- **问题反馈**: https://github.com/zlh123123/PassAgent/issues
- **邮箱**: lh.zhang.work@gmail.com

## 🗺️ 开发路线图

- [ ] v1.0 - 基础功能实现


---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️ Star！**


</div>