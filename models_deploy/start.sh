#!/bin/bash
set -e

# 设置环境变量以避免 OpenMP 线程数错误
export OMP_NUM_THREADS=1

# ============================================================
# PassAgent 模型服务本地启动脚本（非 Docker）
# 前提：已安装 vllm，模型已下载到 models/ 目录
# 用法：bash models_deploy/start.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL_DIR="${MODEL_DIR:-$SCRIPT_DIR/models}"
HOST="${VLLM_HOST:-0.0.0.0}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.9}"
ENABLE_OMNI="${ENABLE_OMNI:-1}"

# 模型路径
QWEN_7B_PATH="${QWEN_7B_PATH:-$MODEL_DIR/Qwen3-4b}"
QWEN_1_7B_PATH="${QWEN_1_7B_PATH:-$MODEL_DIR/PassRules}"

# 端口
QWEN_3_4B_PORT="${QWEN_3_4B_PORT:-6006}"
PASSRULES_PORT="${PASSRULES_PORT:-6008}"

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

# ---------- 启动 Qwen3-4b（Agent 主力模型） ----------
echo "启动 Qwen3-4b -> $HOST:$QWEN_3_4B_PORT"
python -m vllm.entrypoints.openai.api_server \
    --model "$QWEN_7B_PATH" \
    --host "$HOST" \
    --port "$QWEN_3_4B_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    --dtype auto \
    --max-model-len 8192 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --reasoning-parser deepseek_r1 \
    --served-model-name "Qwen3-4b" &
echo $! >> "$PID_FILE"

# ---------- 启动 PassRules 微调模型 ----------
# echo "启动 PassRules -> $HOST:$PASSRULES_PORT"
# python -m vllm.entrypoints.openai.api_server \
#     --model "$QWEN_1_7B_PATH" \
#     --host "$HOST" \
#     --port "$PASSRULES_PORT" \
#     --gpu-memory-utilization "$GPU_MEM_UTIL" \
#     --trust-remote-code \
#     --dtype auto &
# echo $! >> "$PID_FILE"

# ---------- 可选：启动 Qwen-Omni ----------
# QWEN_OMNI_PATH="${QWEN_OMNI_PATH:-$MODEL_DIR/Qwen2_5_omni}"
# if [ "${ENABLE_OMNI}" = "1" ] && [ -d "$QWEN_OMNI_PATH" ]; then
#     QWEN_OMNI_PORT="${QWEN_OMNI_PORT:-8082}"
#     echo "启动 Qwen2_5_omni -> $HOST:$QWEN_OMNI_PORT"
#     echo "  Qwen2_5_omni: http://$HOST:$QWEN_OMNI_PORT/v1"
#     python -m vllm.entrypoints.openai.api_server \
#         --model "$QWEN_OMNI_PATH" \
#         --host "$HOST" \
#         --port "$QWEN_OMNI_PORT" \
#         --gpu-memory-utilization "$GPU_MEM_UTIL" \
#         --trust-remote-code \
#         --dtype auto &
#     echo $! >> "$PID_FILE"
# fi

echo ""
echo "所有模型已启动，按 Ctrl+C 停止全部服务"
echo "  Qwen3-4b:  http://$HOST:$QWEN_3_4B_PORT/v1"

# 等待任一进程退出
wait -n
echo "有进程异常退出，正在清理..."
cleanup
