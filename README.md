# Sunrise Salon — AI Voice Receptionist

I made this project as a voice receptionist for Sunrise Salon. The goal is simple: let customers ask about salon services and appointments by speaking naturally instead of searching through information themselves.

## What the project includes

- A website where a customer can start a voice conversation.
- A LiveKit-based voice session.
- A Python receptionist agent that uses salon information from the database.
- Appointment tools for checking availability, booking, and cancellation.
- A PostgreSQL database for business details, stylists, services, FAQs, and appointment data.

## Try the website

[Open the Sunrise Salon call page](https://sunrise-salon-l8siutbw8-agentai6.vercel.app/)

The page is deployed, but please test the complete voice and appointment flow before treating it as ready for real customer bookings.

## How the receptionist works

When a call starts, the agent loads the salon's business details, service list, stylist schedules, and FAQs. It uses that information to answer questions and calls database tools for appointment availability or booking-related actions.

The agent is configured with:

- **LiveKit Agents** for the voice session.
- **Groq Whisper large-v3-turbo** for speech recognition.
- **Groq-hosted GPT-OSS 120B** for the language model.
- **Edge TTS** with the en-IN-NeerjaNeural voice for spoken responses.
- **Silero VAD** for detecting when the caller is speaking.

The AI models run through Groq's hosted inference service. The voice session uses LiveKit, while the application and database need to be deployed and maintained separately.

## Run it locally

### What you need

- Python and Docker / Docker Compose
- Node.js and npm for the web app
- LiveKit project credentials
- Groq API key
- PostgreSQL database settings

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/jaswanthramadasappa-lab/sunrise-salon.git
   cd sunrise-salon
   ```

2. Copy `.env.example` to your local `.env` file and fill in the values you need. Keep this file private.

3. Start the database and supporting services:

   ```bash
   docker compose up --build
   ```

4. Install the web app dependencies and start the frontend:

   ```bash
   cd web
   npm install
   npm run dev
   ```

5. Start the agent from the `agent` folder using the LiveKit Agents CLI after its Python dependencies and environment are configured.

Check the environment example and service configuration for the exact ports and required variables. If something does not start, check the service logs first.

## Demo salon data

The seed data is only a sample configuration. It currently includes:

- Haircuts, styling, hair colour, hair spa, facial, and clean-up services.
- Three stylists with different working schedules.
- FAQs about payments, walk-ins, parking, late arrival, discounts, and cancellation.
- Asia/Kolkata as the salon timezone.

Please confirm the salon address, prices, hours, and policies with the owner before using this information publicly.

## What I still need to verify

I have not added made-up performance numbers. Before calling this production-ready, I still need to test the complete customer journey, including successful and unavailable bookings, cancellation, duplicate booking attempts, interruptions, and unclear caller requests. Latency should be measured on the running system and reported with actual results.

## Repository layout

```
agent/       Python voice agent and database access
db/          PostgreSQL schema and seed data
web/         Next.js customer call page
docker-compose.yml
.env.example
HANDOVER_NOTE.md
```

This is my PorsAI Forward Deployed Engineer Intern take-home project. The code and configuration are in this repository; the handover note explains the salon-side information and precautions.
