import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class FactEntry:
    entity: str
    attribute: str
    value: Any
    updated_at: float = field(default_factory=time.time)


class LongTermMemoryStore:
    """پایگاه داده ساختاریافته برای ذخیره حقایق معنایی (Semantic LTM)"""

    def __init__(self):
        # ساختار: {entity: {attribute: FactEntry}}
        self._store: Dict[str, Dict[str, FactEntry]] = {}

    def upsert_fact(self, entity: str, attribute: str, value: Any):
        entity_key = entity.lower().strip()
        attr_key = attribute.lower().strip()

        if entity_key not in self._store:
            self._store[entity_key] = {}

        # بروزرسانی یا درج حقیقت جدید (Conflict Resolution)
        self._store[entity_key][attr_key] = FactEntry(
            entity=entity_key,
            attribute=attr_key,
            value=value
        )
        print(f"[LTM CONSOLIDATED] Updated '{entity_key}.{attr_key}' -> {value}")

    def query_entity(self, entity: str) -> Optional[Dict[str, Any]]:
        entity_key = entity.lower().strip()
        if entity_key in self._store:
            return {attr: entry.value for attr, entry in self._store[entity_key].items()}
        return None


class MemoryConsolidationWorker:
    """پردازنده پس‌زمینه برای استخراج حقایق از STM و انتقال به LTM"""

    def __init__(self, ltm: LongTermMemoryStore):
        self.ltm = ltm

    def process_short_term_buffer(self, conversation_turn: Dict[str, str]):
        """شبیه‌سازی استخراج ساختاریافته (Fact Extraction) توسط LLM"""
        user_input = conversation_turn.get("user", "")

        # شبیه‌سازی منطق استخراج حقیقت (در لایه تولید، این کار با Pydantic/LLM انجام می‌شود)
        if "my preferred language is" in user_input.lower():
            lang = user_input.lower().split("is")[-1].strip()
            self.ltm.upsert_fact(entity="user", attribute="preferred_language", value=lang)

        elif "i moved to" in user_input.lower():
            city = user_input.lower().split("to")[-1].strip()
            self.ltm.upsert_fact(entity="user", attribute="location", value=city)


# --- تست عملکرد ---
if __name__ == "__main__":
    ltm_store = LongTermMemoryStore()
    worker = MemoryConsolidationWorker(ltm=ltm_store)

    # تعامل ۱: کاربر زبان خود را اعلام می‌کند
    turn1 = {"user": "Hello, my preferred language is Python"}
    worker.process_short_term_buffer(turn1)

    # تعامل ۲: کاربر مکان خود را اعلام می‌کند
    turn2 = {"user": "I moved to Berlin"}
    worker.process_short_term_buffer(turn2)

    # تعامل ۳: تغییر مکان (تست Conflict Resolution)
    turn3 = {"user": "I moved to Munich"}
    worker.process_short_term_buffer(turn3)

    # استعلام حافظه تثبیت‌شده
    print("\n--- Current Semantic Long-Term Memory for 'user' ---")
    user_facts = ltm_store.query_entity("user")
    print(json.dumps(user_facts, indent=2))

