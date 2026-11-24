import { NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";

export async function GET() {
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const wsUrl = process.env.LIVEKIT_URL;

  if (!apiKey || !apiSecret || !wsUrl) {
    return NextResponse.json(
      { error: "LiveKit environment variables are missing" },
      { status: 500 }
    );
  }

  const roomName = `sunrise-salon-${Math.random().toString(36).substring(2, 8)}`;
  const participantName = `caller-${Math.random().toString(36).substring(2, 6)}`;

  const at = new AccessToken(apiKey, apiSecret, {
    identity: participantName,
    ttl: "15m",
  });

  at.addGrant({
    roomJoin: true,
    room: roomName,
    canPublish: true,
    canSubscribe: true,
  });

  return NextResponse.json({
    token: await at.toJwt(),
    url: wsUrl,
    roomName,
  });
}