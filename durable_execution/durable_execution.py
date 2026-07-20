import json
from pathlib import Path

LOG_FILE = Path("execution_log.json")


def run_activity(step_id: str, func, *args):
    """لایه‌ی مجری Activity: چک کردن لاگ قبلی پیش از اجرا"""
    log = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else {}

    # ۱. Replay Check: اگر قبلاً اجرا شده، اجرای واقعی را Skip کن
    if step_id in log:
        print(f"[REPLAY] Step '{step_id}' skipped! Restored from cache.")
        return log[step_id]

    # ۲. Real Execution: اجرای واقعی کد غیرقطعی (مثل LLM)
    print(f"[EXECUTE] Running '{step_id}'...")
    result = func(*args)

    # ۳. Commit: ثبت آنی خروجی روی دیسک
    log[step_id] = result
    LOG_FILE.write_text(json.dumps(log, indent=2))
    return result


# --- Workflow (ارکستریتور قطعی) ---
def my_agent_workflow():
    # گام اول: استخراج متن
    text = run_activity("step_1_read", lambda: "fake_pdf_content")

    # گام دوم: فراخوانی LLM (سنگین و هزینه‌دار)
    summary = run_activity("step_2_llm", lambda: f"Summary of {text}")

    # شبیه‌سازی کرش ناگهانی قبل از گام سوم
    log = json.loads(LOG_FILE.read_text())
    if "step_3_db" not in log:
        print("[CRASH] Power failure before step 3!")
        exit(1)

    # گام سوم: ذخیره در دیتابیس
    db_status = run_activity("step_3_db", lambda: f"Saved '{summary}' to DB")
    print(f"[DONE] Workflow completed: {db_status}")


if __name__ == "__main__":
    my_agent_workflow()

