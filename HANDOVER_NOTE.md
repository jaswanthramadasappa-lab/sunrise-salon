# Sunrise Salon — AI Voice Receptionist Handover Guide

Welcome to your new AI Voice Receptionist for **Sunrise Salon**. This guide explains what your receptionist handles automatically, what it leaves to your staff, and how you can update your salon details anytime.

---

## What Your AI Receptionist Does
* **Answers calls 24/7 from your website:** Customers click **Call Sunrise Salon** on your page and speak naturally—just like a regular phone call.
* **Answers salon questions accurately:** Shares your address (*12 Lake Road, Indiranagar, Bengaluru*), stylist schedules, service prices, payment methods (cash, UPI, cards), parking info, and policies.
* **Books, reschedules, and cancels appointments:** Checks real-time stylist availability in IST (30-minute slots) before confirming any booking.
* **Prevents double-bookings:** Even if two customers try to book the exact same time slot at the exact same second, the system guarantees only one booking goes through.
* **Handles interruptions & silence politely:** Stops speaking immediately if a customer interrupts, and gently checks in if the line goes quiet.

---

## What It Will NOT Do (Safety & Privacy)
* **Will not guess or make up information:** If a customer asks about something not on file (such as membership plans or packages), it will clearly say it doesn't have that info and offer to pass the question to your staff.
* **Will not quote exact prices for variable services:** For Hair Colour (*"From Rs 2,500, depends on hair length"*), it will never invent a fixed price.
* **Will not book services you don't offer:** Politely declines requests for nail art, waxing, makeup, tattoos, or home service.
* **Will not share private information:** Never reveals staff personal phone numbers or another customer's appointment details, even if someone tries to trick it.
* **Will not waive the 2-hour cancellation policy:** Customers can still cancel less than 2 hours before their slot, but the receptionist will inform them that it is not a free cancellation.

---

## How to Update Hours, Prices, Services, or FAQs
All of Sunrise Salon's information is stored in your database—**no code changes or redeployment are needed**. Any update takes effect on the very next call.

1. Open your **Neon Database Console** → **Tables** (or **SQL Editor**).
2. Choose the table you want to update:
   * **Change a price or add a service:** Open the `services` table, edit the `price_display` column, or add a new row linked to the stylist.
   * **Change stylist working days or hours:** Open the `stylists` table and update `working_days` (`0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat`), `start_time`, or `end_time`.
   * **Update or add an FAQ (e.g., new discounts or holiday hours):** Open the `faqs` table and edit the `answer` or add a new row.
   * **Update address, closed days, or non-offered services:** Open the `businesses` table.
3. Click **Save**—the receptionist will immediately use the updated details on the next incoming call.