#!/bin/bash
set -e

# ============================================================
# PassAgent 模型服务本地启动脚本（非 Docker）
# 前提：已安装 vllm，模型已下载到 models/ 目录
# 用法：bash models_deploy/start.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL_DIR="${MODEL_DIR:-$SCRIPT_DIR/models}"
HOST="${VLLM_HOST:-0.0.0.0}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.45}"

# 模型路径
QWEN_7B_PATH="${QWEN_7B_PATH:-$MODEL_DIR/Qwen2.5-7B-Instruct-GPTQ-Int4}"
QWEN_1_7B_PATH="${QWEN_1_7B_PATH:-$MODEL_DIR/Qwen-1.7B-FineTuned}"

# 端口
QWEN_7B_PORT="${QWEN_7B_PORT:-8080}"
QWEN_1_7B_PORT="${QWEN_1_7B_PORT:-8081}"

# PID 文件，方便停止
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

# ---------- 启动 Qwen2.5-7B（Agent 主力模型） ----------
echo "启动 Qwen2.5-7B -> $HOST:$QWEN_7B_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_7B_PATH" \
    --host "$HOST" \
    --port "$QWEN_7B_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto \
    --max-model-len 8192 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --chat-template "$QWEN_7B_PATH/tokenizer_config.json" &
echo $! >> "$PID_FILE"

# ---------- 启动 Qwen-1.7B 微调模型 ----------
echo "启动 Qwen-1.7B -> $HOST:$QWEN_1_7B_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_1_7B_PATH" \
    --host "$HOST" \
    --port "$QWEN_1_7B_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto &
echo $! >> "$PID_FILE"

# ---------- 可选：启动 Qwen-Omni ----------
QWEN_OMNI_PATH="${QWEN_OMNI_PATH:-$MODEL_DIR/Qwen2.5-Omni-7B-GPTQ-Int4}"
if [ "${ENABLE_OMNI}" = "1" ] && [ -d "$QWEN_OMNI_PATH" ]; then
    QWEN_OMNI_PORT="${QWEN_OMNI_PORT:-8082}"
    echo "启动 Qwen-Omni -> $HOST:$QWEN_OMNI_PORT"
    python -m vllm.entrypoints.openai.api_server \
        --model "$QWEN_OMNI_PATH" \
        --host "$HOST" \
        --port "$QWEN_OMNI_PORT" \
        --gpu-memory-utilization "$GPU_MEM_UTIL" \
        --trust-remote-code \
        --dtype auto &
    echo $! >> "$PID_FILE"
fi

echo ""
echo "所有模型已启动，按 Ctrl+C 停止全部服务"
echo "  Qwen2.5-7B:  http://$HOST:$QWEN_7B_PORT/v1"
echo "  Qwen-1.7B:   http://$HOST:$QWEN_1_7B_PORT/v1"

# 等待任一进程退出
wait -n
echo "有进程异常退出，正在清理..."
cleanup
