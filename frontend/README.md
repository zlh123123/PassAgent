# Frontend README

实机部署方式是：

- 模型服务运行在云服务器
- 后端运行在云服务器
- 前端运行在本地
- 本地通过 SSH 隧道访问云服务器上的后端

对应链路：

`本地 Frontend -> SSH 隧道 -> 云端 Backend:8000 -> 云端 Model Service:6006`

## 1. 云服务器准备

需要在云服务器上启动两个服务：

1. 模型服务，监听 `127.0.0.1:6006`
2. PassAgent backend，监听 `0.0.0.0:8000` 或 `127.0.0.1:8000`

backend 的环境变量在 `backend/.env`中配置，至少确认下面几项：

```env
LLM_BASE_URL="http://127.0.0.1:6006/v1"
PASSTSL_MODEL_PATH="/你的服务器路径/PassAgent/models_deploy/models/passtsl/passtsl.onnx"
```

如果后端也跑在云服务器上，就不需要再把 `6006` 映射回本地。`6006` 只给云服务器上的 backend 内部访问。

## 2. 云服务器启动 Backend

在云服务器上执行：

```bash
cd /path/to/PassAgent/backend
uv sync
uv run python main.py
```

默认监听端口是 `8000`。

可以先验证：

```bash
curl http://127.0.0.1:8000/health
```

返回 `{"status":"healthy"}` 说明后端正常。

## 3. 本地创建前端环境变量

前端实际读取的是 `NEXT_PUBLIC_BACKEND_URL`。

模板文件见：

[`frontend/.env.example`](/Users/zhanglinghao/Desktop/PassAgent/frontend/.env.example)

本地开发时，建议复制成 `frontend/.env.local`：

```bash
cp .env.example .env.local
```

或手动创建 `frontend/.env.local`，内容如下：

```env
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

这里写本地 `127.0.0.1:8000`，因为你会用 SSH 隧道把它转发到云服务器上的 backend。

## 4. 本地建立 SSH 隧道

在本地执行：

```bash
ssh -CNg -L 8000:127.0.0.1:8000 -p 16845 root@connect.cqa1.seetacloud.com
```

这条命令的含义是：

- 本地访问 `127.0.0.1:8000`
- 实际会通过 SSH 转发到云服务器的 `127.0.0.1:8000`

注意：

- 即使 autodl 只开放了 `6006` 和 `6008` 作为公网 HTTP 端口，也不影响这个方案
- 因为这里不是直接访问云服务器公网 `8000`
- 而是先连 SSH，再访问云服务器内部 `127.0.0.1:8000`

## 5. 本地启动 Frontend

在本地执行：

```bash
cd /path/to/PassAgent/frontend
pnpm install
pnpm dev
```

默认访问：

```text
http://127.0.0.1:3000
```

