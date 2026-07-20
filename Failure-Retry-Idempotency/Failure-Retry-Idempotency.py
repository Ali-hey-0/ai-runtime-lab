import time
import random
import hashlib

def execute_idempotent_activity(task_id: str, step_name: str, action_fn, max_retries: int = 3):
    # ۱. تولید کلید یکتای Idempotency
    idempotency_key = hashlib.sha256(f"{task_id}:{step_name}".encode()).hexdigest()[:12]
    
    base_delay = 0.5
    for attempt in range(max_retries):
        try:
            # ارسال Idempotency-Key به هدر یا لایه اجرایی
            print(f"[ATTEMPT {attempt + 1}] Executing with Key: {idempotency_key}")
            return action_fn(idempotency_key)
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[PERMANENT FAILURE] Max retries reached for key {idempotency_key}.")
                raise e
            
            # ۲. محاسبه Full Jitter Backoff
            sleep_time = random.uniform(0, min(8.0, base_delay * (2 ** attempt)))
            print(f"[TRANSIENT ERROR] {e} -> Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

