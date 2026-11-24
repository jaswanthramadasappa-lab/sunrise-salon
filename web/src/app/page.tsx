"use client";

import { useState, useCallback } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  BarVisualizer,
  useVoiceAssistant,
  useLocalParticipant,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { Phone, PhoneOff, Mic, MicOff, MapPin, Clock, Sparkles } from "lucide-react";

function ActiveCallUI({ onDisconnect }: { onDisconnect: () => void }) {
  const { state, audioTrack } = useVoiceAssistant();
  const { isMicrophoneEnabled, localParticipant } = useLocalParticipant();

  const toggleMic = () => {
    localParticipant.setMicrophoneEnabled(!isMicrophoneEnabled);
  };

  const statusLabel: Record<string, string> = {
    connecting: "Connecting to receptionist...",
    initializing: "Connecting to receptionist...",
    listening: "Listening to you...",
    thinking: "Thinking...",
    speaking: "Receptionist is speaking...",
  };

  return (
    <div className="flex flex-col items-center space-y-6 py-4">
      <div className="flex items-center gap-2 rounded-full bg-amber-50 px-4 py-1.5 text-sm font-medium text-amber-800 border border-amber-200">
        <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
        {statusLabel[state] || "On Call"}
      </div>

      <div className="h-24 w-full flex items-center justify-center rounded-2xl bg-stone-50 border border-stone-200 px-6">
        <BarVisualizer
          state={state}
          barCount={7}
          trackRef={audioTrack}
          className="h-14 w-48"
        />
      </div>

      <div className="flex items-center gap-4 pt-2">
        <button
          onClick={toggleMic}
          className={`flex items-center gap-2 rounded-full px-5 py-3 text-sm font-medium transition ${
            isMicrophoneEnabled
              ? "bg-stone-100 text-stone-700 hover:bg-stone-200"
              : "bg-amber-100 text-amber-900 hover:bg-amber-200"
          }`}
        >
          {isMicrophoneEnabled ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
          {isMicrophoneEnabled ? "Mute" : "Unmuted"}
        </button>

        <button
          onClick={onDisconnect}
          className="flex items-center gap-2 rounded-full bg-rose-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-rose-700 transition"
        >
          <PhoneOff className="h-4 w-4" />
          End Call
        </button>
      </div>
    </div>
  );
}

export default function SunriseSalonPage() {
  const [token, setToken] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCall = useCallback(async () => {
    setIsConnecting(true);
    setError(null);
    try {
      const res = await fetch("/api/token");
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to start call");
      setToken(data.token);
      setWsUrl(data.url);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not connect");
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const endCall = useCallback(() => {
    setToken(null);
    setWsUrl(null);
  }, []);

  return (
    <main className="min-h-screen bg-[#FAF8F5] text-stone-800 flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-xl shadow-stone-200/60 border border-stone-100">
        {/* Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 text-amber-700">
            <Sparkles className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-stone-900">
            Sunrise Salon
          </h1>
          <p className="text-sm text-stone-500">
            AI Voice Receptionist &bull; Instant Bookings &amp; Inquiries
          </p>
        </div>

        {/* Call Area */}
        {token && wsUrl ? (
          <LiveKitRoom
            token={token}
            serverUrl={wsUrl}
            connect={true}
            audio={true}
            video={false}
            onDisconnected={endCall}
          >
            <ActiveCallUI onDisconnect={endCall} />
            <RoomAudioRenderer />
          </LiveKitRoom>
        ) : (
          <div className="flex flex-col items-center space-y-5 py-4">
            <button
              onClick={startCall}
              disabled={isConnecting}
              className="group flex items-center gap-3 rounded-full bg-stone-900 px-8 py-4 text-base font-medium text-white shadow-lg shadow-stone-900/20 hover:bg-stone-800 disabled:opacity-60 transition cursor-pointer"
            >
              <Phone className="h-5 w-5 text-amber-400 group-hover:scale-110 transition" />
              {isConnecting ? "Connecting..." : "Call Sunrise Salon"}
            </button>

            <p className="text-xs text-stone-400 text-center max-w-xs">
              Speak naturally to check availability, book, reschedule, or cancel an appointment. You can interrupt anytime.
            </p>

            {error && (
              <p className="text-xs text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}
          </div>
        )}

        {/* Footer Info */}
        <div className="mt-8 pt-6 border-t border-stone-100 space-y-2 text-xs text-stone-500">
          <div className="flex items-center gap-2">
            <MapPin className="h-3.5 w-3.5 text-amber-600 shrink-0" />
            <span>12 Lake Road, Indiranagar, Bengaluru</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5 text-amber-600 shrink-0" />
            <span>Mon–Sat &bull; Closed Sundays &bull; 30-min slots (IST)</span>
          </div>
        </div>
      </div>
    </main>
  );
}