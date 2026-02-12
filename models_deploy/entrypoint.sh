#!/bin/bash
set -e

source /app/.venv/bin/activate

MODEL_DIR="/app/models"
HOST="${VLLM_HOST:-0.0.0.0}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.45}"

# 模型路径
QWEN_7B_PATH="${QWEN_7B_PATH:-$MODEL_DIR/Qwen2.5-7B-Instruct-GPTQ-Int4}"
QWEN_1_7B_PATH="${QWEN_1_7B_PATH:-$MODEL_DIR/Qwen-1.7B-FineTuned}"
QWEN_OMNI_PATH="${QWEN_OMNI_PATH:-$MODEL_DIR/Qwen2.5-Omni-7B-GPTQ-Int4}"

# 端口
QWEN_7B_PORT="${QWEN_7B_PORT:-8080}"
QWEN_1_7B_PORT="${QWEN_1_7B_PORT:-8081}"
QWEN_OMNI_PORT="${QWEN_OMNI_PORT:-8082}"

# 启动 Qwen2.5-7B（常驻）
echo "启动 Qwen2.5-7B -> $HOST:$QWEN_7B_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_7B_PATH" \
    --host "$HOST" \
    --port "$QWEN_7B_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto &

# 启动 Qwen-1.7B 微调模型（常驻）
echo "启动 Qwen-1.7B -> $HOST:$QWEN_1_7B_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_1_7B_PATH" \
    --host "$HOST" \
    --port "$QWEN_1_7B_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto &

# 可选：启动 Qwen-Omni（设 ENABLE_OMNI=1 开启）
if [ "${ENABLE_OMNI}" = "1" ] && [ -d "$QWEN_OMNI_PATH" ]; then
    echo "启动 Qwen-Omni -> $HOST:$QWEN_OMNI_PORT"
    python -m vllm.entrypoints.openai.api_server \
        --model "$QWEN_OMNI_PATH" \
        --host "$HOST" \
        --port "$QWEN_OMNI_PORT" \
        --gpu-memory-utilization "$GPU_MEM_UTIL" \
        --trust-remote-code \
        --dtype auto &
fi

# 等待所有后台进程，任一退出则整体退出
wait -n
exit $?
