import os
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import asyncpg

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])

    async def get_business_context(self, slug: str) -> dict:
        async with self.pool.acquire() as conn:
            biz = await conn.fetchrow("SELECT * FROM businesses WHERE slug = $1", slug)
            if not biz:
                raise ValueError(f"Business '{slug}' not found in database.")

            stylists = await conn.fetch(
                "SELECT * FROM stylists WHERE business_id = $1 ORDER BY name", biz["id"]
            )
            services = await conn.fetch(
                """
                SELECT s.*, st.name AS stylist_name
                FROM services s
                JOIN stylists st ON s.stylist_id = st.id
                WHERE s.business_id = $1
                ORDER BY s.name
                """,
                biz["id"],
            )
            faqs = await conn.fetch(
                "SELECT topic, answer FROM faqs WHERE business_id = $1", biz["id"]
            )
            return {
                "business": dict(biz),
                "stylists": [dict(r) for r in stylists],
                "services": [dict(r) for r in services],
                "faqs": [dict(r) for r in faqs],
            }

    async def check_availability(self, business_id, service_name: str, date_str: str, tz_name: str) -> dict:
        tz = ZoneInfo(tz_name)
        target_date = date.fromisoformat(date_str)
        weekday = target_date.weekday()

        async with self.pool.acquire() as conn:
            svc = await conn.fetchrow(
                """
                SELECT s.id AS service_id, s.name AS service_name, s.price_display,
                       st.id AS stylist_id, st.name AS stylist_name,
                       st.working_days, st.start_time, st.end_time,
                       b.slot_duration_minutes, b.closed_days
                FROM services s
                JOIN stylists st ON s.stylist_id = st.id
                JOIN businesses b ON s.business_id = b.id
                WHERE s.business_id = $1 AND LOWER(s.name) LIKE LOWER($2)
                LIMIT 1
                """,
                business_id,
                f"%{service_name}%",
            )
            if not svc:
                return {"available": False, "reason": f"Service '{service_name}' is not offered."}

            day_name = DAY_NAMES[weekday]
            if day_name in svc["closed_days"]:
                return {"available": False, "reason": f"We are closed on {day_name}s."}

            if weekday not in svc["working_days"]:
                working_day_names = [DAY_NAMES[d] for d in svc["working_days"]]
                return {
                    "available": False,
                    "reason": f"{svc['stylist_name']} is not in on {day_name}. They work on {', '.join(working_day_names)} from {svc['start_time'].strftime('%I:%M %p')} to {svc['end_time'].strftime('%I:%M %p')}.",
                }

            # Generate all 30-min slots for that stylist
            slot_mins = svc["slot_duration_minutes"]
            cur = datetime.combine(target_date, svc["start_time"], tzinfo=tz)
            end = datetime.combine(target_date, svc["end_time"], tzinfo=tz)
            now = datetime.now(tz)

            booked_rows = await conn.fetch(
                """
                SELECT slot_start FROM bookings
                WHERE stylist_id = $1 AND status = 'booked'
                  AND slot_start >= $2 AND slot_start < $3
                """,
                svc["stylist_id"],
                cur,
                end,
            )
            booked_times = {r["slot_start"].astimezone(tz) for r in booked_rows}

            open_slots = []
            while cur + timedelta(minutes=slot_mins) <= end:
                if cur > now and cur not in booked_times:
                    open_slots.append(cur.strftime("%H:%M"))
                cur += timedelta(minutes=slot_mins)

            return {
                "available": len(open_slots) > 0,
                "stylist": svc["stylist_name"],
                "service": svc["service_name"],
                "price": svc["price_display"],
                "date": date_str,
                "open_slots": open_slots,
            }

    async def book_appointment(
        self, business_id, service_name: str, date_str: str, time_str: str,
        customer_name: str, customer_phone: str, tz_name: str
    ) -> dict:
        tz = ZoneInfo(tz_name)
        target_date = date.fromisoformat(date_str)
        target_time = time.fromisoformat(time_str)
        slot_start = datetime.combine(target_date, target_time, tzinfo=tz)

        if slot_start <= datetime.now(tz):
            return {"success": False, "reason": "That time slot is in the past."}

        async with self.pool.acquire() as conn:
            svc = await conn.fetchrow(
                """
                SELECT s.id AS service_id, s.name AS service_name,
                       st.id AS stylist_id, st.name AS stylist_name,
                       st.working_days, st.start_time, st.end_time,
                       b.slot_duration_minutes
                FROM services s
                JOIN stylists st ON s.stylist_id = st.id
                JOIN businesses b ON s.business_id = b.id
                WHERE s.business_id = $1 AND LOWER(s.name) LIKE LOWER($2)
                LIMIT 1
                """,
                business_id,
                f"%{service_name}%",
            )
            if not svc:
                return {"success": False, "reason": f"Service '{service_name}' not found."}

            if target_date.weekday() not in svc["working_days"]:
                return {"success": False, "reason": f"{svc['stylist_name']} does not work on that day."}

            if not (svc["start_time"] <= target_time < svc["end_time"]):
                return {"success": False, "reason": f"{svc['stylist_name']} only works from {svc['start_time'].strftime('%I:%M %p')} to {svc['end_time'].strftime('%I:%M %p')}."}

            slot_end = slot_start + timedelta(minutes=svc["slot_duration_minutes"])

            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO bookings (business_id, stylist_id, service_id, customer_name, customer_phone, slot_start, slot_end, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 'booked')
                    RETURNING id
                    """,
                    business_id, svc["stylist_id"], svc["service_id"],
                    customer_name, customer_phone, slot_start, slot_end,
                )
                return {
                    "success": True,
                    "booking_id": str(row["id"])[:8],
                    "service": svc["service_name"],
                    "stylist": svc["stylist_name"],
                    "slot": slot_start.strftime("%A, %d %b %Y at %I:%M %p IST"),
                }
            except asyncpg.UniqueViolationError:
                return {
                    "success": False,
                    "reason": "Sorry, that exact slot was just booked by another caller. Please choose another available time.",
                }

    async def cancel_appointment(self, business_id, customer_phone: str, tz_name: str, free_cancel_hours: int) -> dict:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        async with self.pool.acquire() as conn:
            booking = await conn.fetchrow(
                """
                SELECT b.id, b.slot_start, s.name AS service_name, st.name AS stylist_name
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                JOIN stylists st ON b.stylist_id = st.id
                WHERE b.business_id = $1 AND b.customer_phone = $2 AND b.status = 'booked' AND b.slot_start > $3
                ORDER BY b.slot_start ASC
                LIMIT 1
                """,
                business_id, customer_phone, now,
            )
            if not booking:
                return {"success": False, "reason": "No upcoming booking found for that phone number."}

            hours_until = (booking["slot_start"].astimezone(tz) - now).total_seconds() / 3600
            is_free = hours_until >= free_cancel_hours

            await conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = $1", booking["id"])
            return {
                "success": True,
                "service": booking["service_name"],
                "stylist": booking["stylist_name"],
                "was_free_cancellation": is_free,
                "note": "Cancelled free of charge." if is_free else f"Cancelled, but since it is less than {free_cancel_hours} hours before the appointment, it is not a free cancellation.",
            }

    async def reschedule_appointment(
        self, business_id, customer_phone: str, new_date_str: str, new_time_str: str, tz_name: str
    ) -> dict:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        new_start = datetime.combine(date.fromisoformat(new_date_str), time.fromisoformat(new_time_str), tzinfo=tz)

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                booking = await conn.fetchrow(
                    """
                    SELECT b.id, b.stylist_id, b.service_id, s.name AS service_name,
                           st.name AS stylist_name, st.working_days, st.start_time, st.end_time,
                           biz.slot_duration_minutes
                    FROM bookings b
                    JOIN services s ON b.service_id = s.id
                    JOIN stylists st ON b.stylist_id = st.id
                    JOIN businesses biz ON b.business_id = biz.id
                    WHERE b.business_id = $1 AND b.customer_phone = $2 AND b.status = 'booked' AND b.slot_start > $3
                    ORDER BY b.slot_start ASC
                    LIMIT 1
                    """,
                    business_id, customer_phone, now,
                )
                if not booking:
                    return {"success": False, "reason": "No upcoming booking found for that phone number."}

                if new_start.weekday() not in booking["working_days"] or not (booking["start_time"] <= new_start.time() < booking["end_time"]):
                    return {"success": False, "reason": f"{booking['stylist_name']} is not available at that day or time."}

                new_end = new_start + timedelta(minutes=booking["slot_duration_minutes"])
                try:
                    await conn.execute(
                        "UPDATE bookings SET slot_start = $1, slot_end = $2 WHERE id = $3",
                        new_start, new_end, booking["id"],
                    )
                    return {
                        "success": True,
                        "service": booking["service_name"],
                        "stylist": booking["stylist_name"],
                        "new_slot": new_start.strftime("%A, %d %b %Y at %I:%M %p IST"),
                    }
                except asyncpg.UniqueViolationError:
                    return {"success": False, "reason": "That new slot is already taken. Please pick another time."}