"""Task 数据类、全局 asyncio.Queue"""
import asyncio
from dataclasses import dataclass, field


@dataclass
class ChatTask:
    task_id: str
    user_id: str
    session_id: str
    message: str
    file_ids: list[str] = field(default_factory=list)
    event_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    status: str = "pending"  # pending / processing / success / fail


# 全局任务队列
task_queue: asyncio.Queue[ChatTask] = asyncio.Queue(maxsize=50)

# 活跃任务映射 task_id -> ChatTask
active_tasks: dict[str, ChatTask] = {}
