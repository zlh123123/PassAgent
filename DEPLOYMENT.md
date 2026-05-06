# PassAgent 部署与启动手册

本文记录当前 PassAgent 的双服务器部署方式，以及后续从 DeepSeek 在线 LLM 切回 AutoDL 本地 Qwen/vLLM 大模型的操作步骤。

## 1. 当前部署结构

```text
用户浏览器
  ↓
公网服务器 123.60.145.78
  - nginx: 对外监听 80
  - 前端 Next.js: 127.0.0.1:3000
  - 后端入口: /api/ → 127.0.0.1:18000
  ↓ 反向 SSH 隧道
AutoDL / SeetaCloud
  - 后端 FastAPI: 127.0.0.1:6006
  - PassTSL: CPU ONNX，按需加载
  - Pass2Rule: CPU PyTorch，按需加载
  - LLM: 当前使用 DeepSeek API
```

当前线上访问地址：

```text
http://123.60.145.78
```

## 2. 端口约定

| 服务 | 所在机器 | 监听地址 | 说明 |
| --- | --- | --- | --- |
| nginx | 公网服务器 | `0.0.0.0:80` | 对外入口 |
| 前端 Next.js | 公网服务器 | `127.0.0.1:3000` | 由 nginx 代理 |
| 反向隧道入口 | 公网服务器 | `127.0.0.1:18000` | nginx `/api/` 转发到这里 |
| 后端 FastAPI | AutoDL | `127.0.0.1:6006` | AutoDL 当前开放 HTTP 端口之一 |
| Qwen/vLLM | AutoDL | `127.0.0.1:6008` | 切回本地大模型时使用，避免和后端抢 `6006` |

## 3. 公网服务器启动

登录公网服务器：

```bash
ssh root@123.60.145.78
```

启动前端和 nginx：

```bash
systemctl start passagent-frontend
systemctl start nginx
```

查看状态：

```bash
systemctl status passagent-frontend --no-pager -l
systemctl status nginx --no-pager -l
```

验证前端：

```bash
curl -I http://127.0.0.1/
```

正常应看到：

```text
HTTP/1.1 200 OK
```

## 4. AutoDL 后端启动

登录 AutoDL：

```bash
ssh -p 16845 root@connect.cqa1.seetacloud.com
```

进入后端目录：

```bash
cd /root/autodl-tmp/PassAgent/backend
```

一键启动后端和反向 SSH 隧道：

```bash
./start_passagent_autodl.sh
```

这个脚本会启动：

```text
FastAPI 后端: 127.0.0.1:6006
反向 SSH 隧道: AutoDL 127.0.0.1:6006 → 公网服务器 127.0.0.1:18000
```

验证 AutoDL 后端：

```bash
curl http://127.0.0.1:6006/health
```

正常返回：

```json
{"status":"healthy"}
```

验证公网服务器能通过隧道访问 AutoDL：

```bash
ssh root@123.60.145.78 'curl http://127.0.0.1:18000/health'
```

正常返回：

```json
{"status":"healthy"}
```

## 5. 公网完整验证

在本地电脑验证前端：

```bash
curl -I http://123.60.145.78/
```

验证后端 API：

```bash
curl -i http://123.60.145.78/api/projects
```

正常应返回：

```json
{"projects":[]}
```

如果前端正常但 API 不通，优先检查 AutoDL 后端和反向 SSH 隧道。

## 6. 当前 DeepSeek LLM 配置

当前线上后端使用 DeepSeek 在线 API，不依赖 AutoDL GPU。

AutoDL 的后端配置文件：

```bash
/root/autodl-tmp/PassAgent/backend/.env
```

应包含：

```env
LLM_BASE_URL="https://api.deepseek.com/v1"
LLM_MODEL="deepseek-chat"
LLM_API_KEY="你的 DeepSeek API Key"
```

注意：不要把真实 API Key 提交到 Git。

修改 `.env` 后，需要重启 AutoDL 后端：

```bash
cd /root/autodl-tmp/PassAgent/backend
./start_passagent_autodl.sh
```

## 7. 切回 AutoDL 本地 Qwen/vLLM 大模型

### 7.1 什么时候需要切回本地大模型

当前 DeepSeek 方案适合无显卡模式，启动简单、稳定。

如果需要使用 AutoDL 上的本地 Qwen3.5-35B 模型，则必须切换到有 GPU 的实例模式，并启动 vLLM 服务。

### 7.2 推荐端口安排

AutoDL 只开放 `6006` 和 `6008` 作为 HTTP 自定义服务端口。

推荐保持：

```text
后端 FastAPI: 6006
Qwen/vLLM: 6008
```

不要让 vLLM 使用默认 `6006`，否则会和 FastAPI 后端冲突。

### 7.3 启动 Qwen/vLLM

登录 AutoDL：

```bash
ssh -p 16845 root@connect.cqa1.seetacloud.com
```

进入模型部署目录：

```bash
cd /root/autodl-tmp/PassAgent/models_deploy
```

确认模型目录存在：

```bash
ls -lah /root/autodl-tmp/PassAgent/models_deploy/models/Qwen3.5-35B-A3B-GPTQ-Int4
```

启动 vLLM 到 `6008`：

```bash
QWEN_PORT=6008 bash start.sh
```

如果希望放在后台运行，建议使用 `screen`：

```bash
screen -S passagent-vllm
cd /root/autodl-tmp/PassAgent/models_deploy
QWEN_PORT=6008 bash start.sh
```

启动后按：

```text
Ctrl + A，然后按 D
```

即可把 `screen` 会话挂到后台。

重新进入会话：

```bash
screen -r passagent-vllm
```

验证 vLLM：

```bash
curl http://127.0.0.1:6008/v1/models
```

正常情况下会返回模型列表。

### 7.4 修改后端 `.env` 使用本地 Qwen

编辑 AutoDL 后端 `.env`：

```bash
cd /root/autodl-tmp/PassAgent/backend
nano .env
```

把 LLM 配置改成：

```env
LLM_BASE_URL="http://127.0.0.1:6008/v1"
LLM_API_KEY="EMPTY"
LLM_MODEL="Qwen3.5-35B"
```

保存后重启后端和隧道：

```bash
cd /root/autodl-tmp/PassAgent/backend
./start_passagent_autodl.sh
```

### 7.5 验证后端已经使用本地 Qwen

先验证 vLLM 本身：

```bash
curl http://127.0.0.1:6008/v1/models
```

再验证后端：

```bash
curl http://127.0.0.1:6006/health
```

最后从公网验证 API：

```bash
curl -i http://123.60.145.78/api/projects
```

如果 API 能通，说明：

```text
前端 → nginx → 反向隧道 → AutoDL 后端 → 本地 Qwen/vLLM
```

这条链路已经恢复。

### 7.6 切回 DeepSeek

如果 GPU 不够、vLLM 启动失败，或者只是需要快速演示，可以切回 DeepSeek。

编辑 AutoDL 后端 `.env`：

```bash
cd /root/autodl-tmp/PassAgent/backend
nano .env
```

改回：

```env
LLM_BASE_URL="https://api.deepseek.com/v1"
LLM_MODEL="deepseek-chat"
LLM_API_KEY="你的 DeepSeek API Key"
```

然后重启：

```bash
./start_passagent_autodl.sh
```

如需停止 vLLM：

```bash
screen -r passagent-vllm
```

进入后按 `Ctrl + C` 停止。

## 8. PassTSL 与 Pass2Rule 模型说明

这两个模型不需要单独启动服务，都是后端工具按需加载。

### PassTSL

配置项：

```env
PASSTSL_MODEL_PATH="/root/autodl-tmp/PassAgent/models_deploy/models/passtsl/passtsl.onnx"
```

当前使用 ONNX Runtime CPU 推理。

### Pass2Rule

配置项：

```env
PASS2RULE_MODEL_DIR="/root/autodl-tmp/PassAgent/models_deploy/models/pass2rule"
PASS2RULE_CHECKPOINT_PATH="/root/autodl-tmp/PassAgent/models_deploy/models/pass2rule/best_model.pt"
PASS2RULE_DEVICE="cpu"
```

当前建议保持 `PASS2RULE_DEVICE="cpu"`，因为：

- 无显卡模式可以稳定运行；
- Mac 本地的 MPS 对部分 PyTorch Transformer 算子支持不完整；
- Pass2Rule 是辅助工具，不需要单独占 GPU。

如果后续希望有 GPU 时自动使用 GPU，可以改成：

```env
PASS2RULE_DEVICE="auto"
```

`auto` 的选择顺序是：

```text
CUDA GPU → Apple MPS → CPU
```

## 9. 常用日志

公网服务器前端日志：

```bash
journalctl -u passagent-frontend -f
```

公网服务器 nginx 日志：

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

AutoDL 后端日志：

```bash
cd /root/autodl-tmp/PassAgent/backend
tail -f logs/backend.log
```

AutoDL 隧道日志：

```bash
tail -f logs/tunnel.log
```

vLLM 日志：

如果使用 `screen` 启动：

```bash
screen -r passagent-vllm
```

## 10. 常见问题

### 前端能打开，但聊天/登录 API 不通

检查 AutoDL 后端：

```bash
curl http://127.0.0.1:6006/health
```

检查公网服务器隧道入口：

```bash
ssh root@123.60.145.78 'curl http://127.0.0.1:18000/health'
```

检查公网 API：

```bash
curl -i http://123.60.145.78/api/projects
```

### vLLM 启动时报端口占用

确认没有把 vLLM 放到 `6006`：

```bash
QWEN_PORT=6008 bash start.sh
```

### vLLM 启动时报显存不足

可以尝试降低：

```bash
GPU_MEM_UTIL=0.6 QWEN_PORT=6008 bash start.sh
```

如果仍然失败，切回 DeepSeek。

### AutoDL 重启后服务全没了

重新执行：

```bash
ssh -p 16845 root@connect.cqa1.seetacloud.com
cd /root/autodl-tmp/PassAgent/backend
./start_passagent_autodl.sh
```

如果使用本地 Qwen/vLLM，还需要重新启动 vLLM：

```bash
screen -S passagent-vllm
cd /root/autodl-tmp/PassAgent/models_deploy
QWEN_PORT=6008 bash start.sh
```
