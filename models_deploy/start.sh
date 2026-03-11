#!/bin/bash
set -e

export OMP_NUM_THREADS=1
export PYTORCH_ALLOC_CONF=expandable_segments:True


HOST="${VLLM_HOST:-0.0.0.0}"
QWEN_PORT="${QWEN_PORT:-6006}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.7}"
TP_SIZE="${TP_SIZE:-1}"

QWEN_PATH="${QWEN_PATH:-/root/autodl-tmp/PassAgent/models_deploy/models/Qwen3.5-35B-A3B-GPTQ-Int4}"

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

echo "启动 Qwen3.5-35B -> $HOST:$QWEN_PORT (tp=$TP_SIZE)"

python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_PATH" \
    --host "$HOST" \
    --port "$QWEN_PORT" \
    --tensor-parallel-size "$TP_SIZE" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --dtype auto \
    --max-model-len 32768 \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder \
    --language-mode \
    --enable-prefix-caching \
    --quantization moe_wna16 \
    --served-model-name "Qwen3.5-35B" &
echo $! >> "$PID_FILE"

echo ""
echo "模型已启动，按 Ctrl+C 停止全部服务"
echo "  Qwen3.5-35B: http://$HOST:$QWEN_PORT/v1"

wait -n
echo "有进程异常退出，正在清理..."
cleanup
