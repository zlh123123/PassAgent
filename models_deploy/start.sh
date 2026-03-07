#!/bin/bash
set -e

export OMP_NUM_THREADS=1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOST="${VLLM_HOST:-0.0.0.0}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.9}"

# 模型路径
QWEN_PATH="${QWEN_PATH:-/root/autodl-tmp/PassAgent/models_deploy/models/Qwen3_5_27B}"

# 端口
QWEN_PORT="${QWEN_PORT:-6006}"

PID_FILE="/tmp/passagent_vllm_pids"
> "$PID_FILE"

cleanup() {
    echo "正在停止所有 vLLM 进程..."
    while read -r pid; do
        kill "$pid" 2>/dev/null && echo "已停止 PID $pid"
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "启动 Qwen3.5-27B -> $HOST:$QWEN_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_PATH" \
    --host "$HOST" \
    --port "$QWEN_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto \
    --max-model-len 8192 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --reasoning-parser deepseek_r1 \
    --enable-prefix-caching \
    --served-model-name "Qwen3.5-27B" &
echo $! >> "$PID_FILE"

echo ""
echo "模型已启动，按 Ctrl+C 停止全部服务"
echo "  Qwen3.5-27B: http://$HOST:$QWEN_PORT/v1"

wait -n
echo "有进程异常退出，正在清理..."
cleanup
