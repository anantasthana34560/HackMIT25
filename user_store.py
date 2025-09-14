import json
import os
from typing import Dict, Any


STORE_PATH = os.path.join(os.path.dirname(__file__), "user_store.json")


def _ensure_store() -> None:
    if not os.path.exists(STORE_PATH):
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)


def load_store() -> Dict[str, Any]:
    _ensure_store()
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_store(store: Dict[str, Any]) -> None:
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def get_user(key: str) -> Dict[str, Any]:
    store = load_store()
    return store.get(key, {"preferences": {}, "state": {}, "history": []})


def update_user(key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    store = load_store()
    user = store.get(key, {"preferences": {}, "state": {}, "history": []})
    # Shallow merge for top-level keys
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(user.get(k), dict):
            user[k].update(v)
        else:
            user[k] = v
    store[key] = user
    save_store(store)
    return user


