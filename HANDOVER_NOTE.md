# Sunrise Salon — Owner Handover

Hi! This note is for the person who will manage Sunrise Salon's AI receptionist after the project handover.

The idea behind this project is to let customers talk to the salon through the website and get help with common questions and appointment requests.

## Website

Customer call page: https://sunrise-salon-l8siutbw8-agentai6.vercel.app/

The website is deployed. Before sharing it with customers, please test a complete call and confirm that the voice agent and database are reachable.

## What the receptionist is set up to do

The agent is configured to:

- Answer questions using the salon's services, prices, stylist schedules, and FAQs stored in the database.
- Check appointment availability.
- Create an appointment after collecting the customer's name, phone number, service, date, and time.
- Cancel an appointment using the customer's phone number and appointment date.
- Keep replies short and avoid inventing information that is not in the salon data.

The current code has tools for checking availability, booking, and cancellation. Rescheduling is not implemented as a separate tool yet.

## Salon details in the sample database

Please confirm these details with the salon owner before using them as real business information. They come from the project's seed data:

- **Business:** Sunrise Salon
- **Address:** 12 Lake Road, Indiranagar, Bengaluru
- **Timezone:** Asia/Kolkata (IST)
- **Appointment slot length:** 30 minutes
- **Free cancellation:** Up to 2 hours before the appointment
- **Closed day:** Sunday
- **Payment methods:** Cash, UPI, and cards
- **Walk-ins:** Welcome; booked customers are served first
- **Parking:** Street parking only

Sample services and prices:

| Service | Price shown in the sample data |
|---|---|
| Women's haircut | Rs 600 |
| Men's haircut | Rs 400 |
| Blow dry and styling | Rs 500 |
| Hair colour | From Rs 2,500; depends on hair length |
| Hair spa | Rs 1,200 |
| Facial | Rs 1,500 |
| Clean-up | Rs 800 |

The sample data also lists three stylists and their working schedules. Check the `db/seed.sql` file for the exact entries.

## Updating salon information

The project stores business details, stylists, services, FAQs, and appointments in PostgreSQL.

1. Open the PostgreSQL database used by the project.
2. Back up the database before making changes.
3. Update the appropriate table:
   - `businesses`: address, timezone, closed days, cancellation policy, and general business notes.
   - `services`: service names and displayed prices.
   - `stylists`: stylist names, specialties, working days, and working hours.
   - `faqs`: answers about payment, walk-ins, parking, discounts, and other salon policies.
4. Save the changes and make a test call to confirm the receptionist is using the updated information.

Do not assume the database is Neon unless that is the provider configured for your deployment. Use the database provider and connection details set in your environment.

## Important safety and maintenance notes

- Never share your database URL, LiveKit secret, Groq key, or other credentials with customers.
- Keep secrets in environment variables; do not commit your real `.env` file to GitHub.
- Confirm prices and policies with the salon owner before publishing them.
- The receptionist should not reveal another customer's appointment details or staff personal phone numbers.
- Hair colour has a variable price in the sample data; the receptionist should quote the displayed starting price rather than promise a fixed total.
- Services such as nail art, waxing, makeup, tattoos, and home service are marked as not offered in the sample configuration.
- The project has a concurrency test file, but run and review the tests against the actual deployed database before relying on booking behavior under simultaneous requests.
- Test voice interruptions, failed calls, appointment conflicts, cancellations, and database outages before using this with real customers.

## Project files

- `agent/main.py`: LiveKit voice agent, prompt, speech services, and appointment tools.
- `agent/db.py`: database operations.
- `agent/test_concurrency.py`: concurrency test.
- `db/schema.sql`: database schema.
- `db/seed.sql`: sample salon data.
- `web/`: Next.js website and call interface.
- `.env.example`: environment variable names and sample configuration.

This is a project handover guide, not a guarantee that every production scenario has been tested. Please verify the deployed setup and business information before relying on it for live appointments.
