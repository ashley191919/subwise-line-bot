"""
SubWise Conversation Context Service

負責保存使用者最近一次操作的簡單上下文。
"""

# 暫時使用記憶體保存 Context
# Day 27 先做最小可用版本
_context_store = {}


def set_context(user_id, key, value):
    """
    保存指定使用者的 Context。
    """

    if user_id not in _context_store:
        _context_store[user_id] = {}

    _context_store[user_id][key] = value


def get_context(user_id, key, default=None):
    """
    取得指定使用者的 Context。
    """

    return _context_store.get(
        user_id,
        {}
    ).get(
        key,
        default
    )


def get_all_context(user_id):
    """
    取得指定使用者目前的所有 Context。
    """

    return _context_store.get(
        user_id,
        {}
    ).copy()


def clear_context(user_id):
    """
    清除指定使用者的 Context。
    """

    _context_store.pop(
        user_id,
        None
    )