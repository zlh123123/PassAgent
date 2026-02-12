FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 系统依赖
RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3.12-dev \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# 创建虚拟环境并安装 vllm
RUN uv venv --python 3.12 --seed && \
    . .venv/bin/activate && \
    uv pip install vllm==0.15.0 --torch-backend=auto

# 安装 vllm-omni
RUN . .venv/bin/activate && \
    git clone https://github.com/vllm-project/vllm-omni.git /tmp/vllm-omni && \
    cd /tmp/vllm-omni && \
    uv pip install -e . && \
    rm -rf /tmp/vllm-omni/.git

# 模型挂载点
VOLUME /app/models

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Qwen2.5-7B: 8080, Qwen-1.7B: 8081, Omni(可选): 8082
EXPOSE 8080 8081 8082

ENTRYPOINT ["/app/entrypoint.sh"]
