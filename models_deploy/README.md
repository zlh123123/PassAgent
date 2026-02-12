# 模型服务部署

## 目录结构

```text
models_deploy/
├── Dockerfile
├── entrypoint.sh
├── README.md
└── models/              # 模型权重放这里
    ├── Qwen2.5-7B-Instruct-GPTQ-Int4/
    ├── Qwen-1.7B-FineTuned/
    └── Qwen2.5-Omni-7B-GPTQ-Int4/
```

## 下载模型

不管用哪种方式启动，都需要先把模型权重下载到 `models/` 目录下：

```bash
cd models_deploy
pip install huggingface_hub

# Qwen2.5-7B（必需）
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4 --local-dir models/Qwen2.5-7B-Instruct-GPTQ-Int4

# Qwen-1.7B 微调（必需，替换为实际模型地址）
# huggingface-cli download your-org/Qwen-1.7B-FineTuned --local-dir models/Qwen-1.7B-FineTuned

# Qwen-Omni（可选）
# huggingface-cli download Qwen/Qwen2.5-Omni-7B-GPTQ-Int4 --local-dir models/Qwen2.5-Omni-7B-GPTQ-Int4
```

## 方式一：Docker 启动

### 1. 构建镜像

```bash
cd models_deploy
docker build -t passagent-model .
```

### 2. 启动容器

默认启动 Qwen2.5-7B（8080）和 Qwen-1.7B（8081）两个常驻模型：

```bash
docker run -d \
  --gpus all \
  --name passagent-model \
  -v $(pwd)/models:/app/models \
  -p 8080:8080 \
  -p 8081:8081 \
  passagent-model
```

如果显存够，可以同时开 Omni（8082）：

```bash
docker run -d \
  --gpus all \
  --name passagent-model \
  -v $(pwd)/models:/app/models \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 8082:8082 \
  -e ENABLE_OMNI=1 \
  -e GPU_MEM_UTIL=0.30 \
  passagent-model
```

### 3. 验证服务

```bash
# Qwen2.5-7B
curl http://localhost:8080/v1/models

# Qwen-1.7B
curl http://localhost:8081/v1/models
```

## 方式二：从源码启动

### 1. 环境准备

需要 Python 3.12、CUDA 12.x、GPU。

```bash
cd models_deploy

uv venv --python 3.12 --seed
source .venv/bin/activate

# 安装 vLLM
uv pip install vllm==0.15.0 --torch-backend=auto

# 安装 vllm-omni（多模态支持）
git clone https://github.com/vllm-project/vllm-omni.git /tmp/vllm-omni
cd /tmp/vllm-omni
uv pip install -e .
cd -
```

### 2. 启动服务

同时启动两个常驻模型：

```bash
# Qwen2.5-7B（端口 8080）
python -m vllm.entrypoints.openai.api_server \
  --model models/Qwen2.5-7B-Instruct-GPTQ-Int4 \
  --host 0.0.0.0 \
  --port 8080 \
  --gpu-memory-utilization 0.45 \
  --trust-remote-code \
  --dtype auto &

# Qwen-1.7B 微调（端口 8081）
python -m vllm.entrypoints.openai.api_server \
  --model models/Qwen-1.7B-FineTuned \
  --host 0.0.0.0 \
  --port 8081 \
  --gpu-memory-utilization 0.45 \
  --trust-remote-code \
  --dtype auto &

wait
```

### 3. 验证

```bash
curl http://localhost:8080/v1/models
curl http://localhost:8081/v1/models
```

启动成功后，后端 `config.py` 中的 `LLM_BASE_URL` 默认指向 `http://localhost:8080/v1`，无需额外配置。
