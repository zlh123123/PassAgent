"""建表脚本"""
from sqlalchemy import text, inspect
from .connection import engine
from .models import Base


def _migrate_user_columns():
    """为已有数据库添加新列（SQLite ALTER TABLE）"""
    new_columns = {
        "font_size": "TEXT DEFAULT 'M'",
        "bubble_style": "TEXT DEFAULT 'rounded'",
        "gen_auto_mode": "INTEGER DEFAULT 1",
        "gen_security_weight": "TEXT DEFAULT '0.5'",
    }
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    existing = {col["name"] for col in insp.get_columns("users")}
    with engine.begin() as conn:
        for col_name, col_def in new_columns.items():
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))


def _migrate_memory_profile_columns():
    """为 user_memory_profiles 表补齐更新时间字段。"""
    new_columns = {
        "updated_at": "TEXT",
        "last_used_at": "TEXT",
    }
    insp = inspect(engine)
    if "user_memory_profiles" not in insp.get_table_names():
        return
    existing = {col["name"] for col in insp.get_columns("user_memory_profiles")}
    with engine.begin() as conn:
        for col_name, col_def in new_columns.items():
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE user_memory_profiles ADD COLUMN {col_name} {col_def}"))


def init_database():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    _migrate_user_columns()
    _migrate_memory_profile_columns()
    print("数据库表创建完成")


def drop_database():
    """删除所有表"""
    Base.metadata.drop_all(bind=engine)
    print("数据库表已删除")


if __name__ == "__main__":
    init_database()
