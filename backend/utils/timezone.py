"""北京时间（UTC+8）工具函数"""
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now() -> datetime:
    """返回当前北京时间（带时区信息）"""
    return datetime.now(BEIJING_TZ)


def beijing_now_iso() -> str:
    """返回当前北京时间的 ISO 格式字符串"""
    return beijing_now().isoformat()
