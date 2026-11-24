import asyncio
import gc
import logging
import os
import re
import uuid
import numpy as np
import onnxruntime as ort
from kokoro_onnx import Kokoro
from livekit.agents import tts, APIConnectOptions

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MALLOC_ARENA_MAX", "2")

logger = logging.getLogger("kokoro-tts")
_KOKORO_INSTANCE: Kokoro | None = None


def _get_kokoro(model_path: str, voices_path: str) -> Kokoro:
    global _KOKORO_INSTANCE
    if _KOKORO_INSTANCE is None:
        orig_session = ort.InferenceSession

        def _low_mem_session(path_or_bytes, sess_options=None, providers=None, **kwargs):
            opts = sess_options or ort.SessionOptions()
            opts.intra_op_num_threads = 1
            opts.inter_op_num_threads = 1
            opts.enable_cpu_mem_arena = False
            opts.enable_mem_pattern = False
            return orig_session(
                path_or_bytes,
                sess_options=opts,
                providers=providers or ["CPUExecutionProvider"],
                **kwargs,
            )

        ort.InferenceSession = _low_mem_session
        try:
            _KOKORO_INSTANCE = Kokoro(model_path, voices_path)
        finally:
            ort.InferenceSession = orig_session
        gc.collect()
    return _KOKORO_INSTANCE


class KokoroTTS(tts.TTS):
    def __init__(
        self,
        model_path: str = "/app/models/kokoro-v1.0.onnx",
        voices_path: str = "/app/models/voices-v1.0.bin",
        voice: str = "af_heart",
        speed: float = 1.0,
    ):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=24000,
            num_channels=1,
        )
        self._model_path = model_path
        self._voices_path = voices_path
        self._voice = voice
        self._speed = speed

    def synthesize(
        self, text: str, *, conn_options: APIConnectOptions = APIConnectOptions()
    ) -> tts.ChunkedStream:
        return _KokoroChunkedStream(
            tts=self, input_text=text, conn_options=conn_options
        )


class _KokoroChunkedStream(tts.ChunkedStream):
    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        text = (self._input_text or "").strip()
        text = re.sub(r"\b\d{7,15}\b", lambda m: " ".join(m.group(0)), text)
        for bad, good in (
            ("\u202f", " "),
            ("\u00a0", " "),
            ("’", "'"),
            ("‘", "'"),
            ("—", ", "),
            ("–", ", "),
        ):
            text = text.replace(bad, good)
        text = re.sub(
            r"\b(\d{1,2}):00\s*(a\.?m\.?|p\.?m\.?)\b",
            r"\1 \2",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return

        kokoro = await asyncio.to_thread(
            _get_kokoro, self._tts._model_path, self._tts._voices_path
        )
        samples, sample_rate = await asyncio.to_thread(
            kokoro.create,
            text,
            voice=self._tts._voice,
            speed=self._tts._speed,
            lang="en-us",
        )
        pad = np.zeros(int(sample_rate * 0.12), dtype=np.float32)
        samples = np.concatenate([samples, pad])
        pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
        logger.info(f"Kokoro synthesized {len(pcm)} bytes for: {text!r}")

        output_emitter.initialize(
            request_id=str(uuid.uuid4()),
            sample_rate=sample_rate,
            num_channels=1,
            mime_type="audio/pcm",
        )
        output_emitter.push(pcm)
        output_emitter.flush()