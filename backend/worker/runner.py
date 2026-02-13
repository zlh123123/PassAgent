"""worker_loop 协程：FIFO 取任务、调 Agent Graph、塞事件"""
import asyncio
import logging

from langchain_core.messages import HumanMessage, AIMessage

from worker.queue import task_queue, ChatTask
from database.connection import SessionLocal
from services.session_service import save_message, get_messages
from agent.graph import agent_graph
from agent.memory.writer import extract_and_save_memories
from agent.memory.reader import retrieve_memory

logger = logging.getLogger(__name__)


async def _process_task(task: ChatTask):
    """处理单个聊天任务：通过 Agent Graph 执行。"""
    task.status = "processing"
    await task.event_queue.put({"event": "task_started", "data": {"task_id": task.task_id}})

    try:
        # 从 DB 加载对话历史
        db = SessionLocal()
        try:
            history = get_messages(db, task.user_id, task.session_id)
        finally:
            db.close()

        # 构建 LangGraph messages
        messages = []
        for msg in history:
            if msg["message_type"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        # 追加当前用户消息
        messages.append(HumanMessage(content=task.message))

        # 保存用户消息到 DB
        db = SessionLocal()
        try:
            save_message(db, task.session_id, task.user_id, task.message, "human")
        finally:
            db.close()

        # 使用一个能同时收集 agent_steps 的队列包装
        agent_steps: list[dict] = []

        class CollectingQueue:
            """包装 task.event_queue，同时收集 agent_step 事件。"""
            async def put(self, event):
                if event.get("event") == "agent_step":
                    agent_steps.append(event.get("data", {}))
                await task.event_queue.put(event)

        collecting_queue = CollectingQueue()

        # 预加载用户记忆，让 planner 第一轮决策就能看到记忆上下文
        preloaded_memories: list[dict] = []
        try:
            db = SessionLocal()
            try:
                preloaded_memories = await retrieve_memory(db, task.user_id, task.message)
            finally:
                db.close()
        except Exception as e:
            logger.warning("预加载记忆失败: %s", e)

        # 构建初始 state 并调用 graph
        initial_state = {
            "messages": messages,
            "user_id": task.user_id,
            "session_id": task.session_id,
            "memories": preloaded_memories,
            "tool_history": [],
            "next_action": None,
            "action_params": {},
            "uploaded_files": [],
            "loop_count": 0,
            "_event_queue": collecting_queue,
        }

        result = await agent_graph.ainvoke(initial_state)

        # 从 result 中提取最终回复
        final_messages = result.get("messages", [])
        full_content = ""
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage):
                full_content = msg.content
                break

        # 保存助手消息到 DB（附带 agent_steps）
        db = SessionLocal()
        try:
            message_id = save_message(
                db, task.session_id, task.user_id, full_content, "assistant",
                agent_steps=agent_steps if agent_steps else None,
            )
        finally:
            db.close()

        # 异步提取记忆（不阻塞主流程）
        try:
            db = SessionLocal()
            try:
                await extract_and_save_memories(
                    db, task.user_id, task.message, full_content,
                )
            finally:
                db.close()
        except Exception:
            pass  # 记忆提取失败不影响正常响应

        await task.event_queue.put({
            "event": "response_done",
            "data": {"message_id": message_id},
        })

        task.status = "success"

    except Exception as e:
        task.status = "fail"
        await task.event_queue.put({
            "event": "task_failed",
            "data": {"error": str(e)},
        })
    finally:
        await task.event_queue.put({"event": "done", "data": {}})


async def worker_loop():
    """Worker 主循环，持续从队列取任务处理"""
    while True:
        task = await task_queue.get()
        try:
            await _process_task(task)
        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            task_queue.task_done()
