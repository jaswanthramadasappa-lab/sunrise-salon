import asyncio
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from db import Database

load_dotenv()

async def run_concurrency_test():
    db = Database()
    await db.connect()

    biz_ctx = await db.get_business_context(os.getenv("BUSINESS_SLUG", "sunrise-salon"))
    biz = biz_ctx["business"]

    # Pick next Monday (weekday 0) so Anita Rao is guaranteed to be working
    today = date.today()
    days_ahead = (0 - today.weekday() + 7) % 7 or 7
    test_date = (today + timedelta(days=days_ahead)).isoformat()
    test_time = "11:00"

    print(f"Firing 5 simultaneous booking requests for Anita Rao on {test_date} at {test_time} IST...")

    tasks = [
        db.book_appointment(
            biz["id"], "Haircut (men)", test_date, test_time,
            f"Caller {i}", f"999990000{i}", biz["timezone"]
        )
        for i in range(1, 6)
    ]

    results = await asyncio.gather(*tasks)
    successes = [r for r in results if r.get("success")]
    failures = [r for r in results if not r.get("success")]

    print(f"\nResults: {len(successes)} succeeded, {len(failures)} rejected.")
    for idx, r in enumerate(results, 1):
        print(f"  Caller {idx}: {r}")

    assert len(successes) == 1, "FAIL: More than one caller booked the same slot!"
    print("\nPASS: Exactly 1 booking succeeded; all concurrent duplicates were blocked by PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(run_concurrency_test())