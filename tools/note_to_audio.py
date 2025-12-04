# note_to_audio_tool.py
from io import BytesIO
from collections.abc import Generator
from typing import Any, Optional
import numpy as np
import re
import soundfile as sf
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class NoteToAudioTool(Tool):
    """
    A Dify plugin that converts a musical note name (e.g., 'C4', 'A#5') into a synthesized audio file.
    Supports sine, square, sawtooth, and triangle waveforms.
    Output format: WAV (44.1kHz, mono, float32).
    """

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # === 参数解析 ===
            note = tool_parameters.get("note")
            if not isinstance(note, str) or not note.strip():
                raise ValueError("Parameter 'note' is required and must be a non-empty string (e.g., 'C4', 'A#5').")

            note = note.strip().upper()
            duration = float(tool_parameters.get("duration", 0.5))
            waveform = str(tool_parameters.get("waveform", "sine")).lower()
            blur = float(tool_parameters.get("blur", 0.05))
            decay = float(tool_parameters.get("decay", 5.0))
            volume = float(tool_parameters.get("volume", 0.3))

            # 验证参数范围
            if duration <= 0 or duration > 10:
                raise ValueError("Duration must be between 0 and 10 seconds.")
            if blur < 0 or blur > 1:
                raise ValueError("Blur must be between 0 and 1.")
            if decay < 0:
                raise ValueError("Decay must be non-negative.")
            if volume <= 0 or volume > 1:
                raise ValueError("Volume must be between 0 and 1.")

            valid_waveforms = {"sine", "square", "sawtooth", "triangle"}
            if waveform not in valid_waveforms:
                raise ValueError(f"Waveform must be one of: {', '.join(valid_waveforms)}")

            # === 音名转频率 ===
            pitch_map = {
                "C": 0, "C#": 1, "DB": 1,
                "D": 2, "D#": 3, "EB": 3,
                "E": 4, "FB": 4, "F": 5,
                "F#": 6, "GB": 6, "G": 7,
                "G#": 8, "AB": 8, "A": 9,
                "A#": 10, "BB": 10, "B": 11
            }

            m = re.fullmatch(r"([A-G][#B]?)(\d+)", note)
            if not m:
                raise ValueError("Invalid note format. Use format like 'C4', 'A#5', 'Eb3'.")

            name, octave_str = m.groups()
            name = name.replace("B", "b")  # Normalize flat to sharp internally? Not needed; use map
            # Handle flats by converting to sharp equivalent if needed, but our map includes both
            base_name = name.upper()
            if base_name.endswith('B'):
                # e.g., 'EB' -> 'D#'
                natural = base_name[0]
                if natural == 'C':
                    raise ValueError("Cb is not supported.")
                prev_note = chr(ord(natural) - 1)
                if prev_note == 'E' or prev_note == 'B':
                    sharp_name = prev_note + '#'
                else:
                    sharp_name = prev_note + '#'
                if sharp_name in pitch_map:
                    base_name = sharp_name
                else:
                    raise ValueError(f"Unsupported flat note: {note}")
            elif base_name not in pitch_map:
                raise ValueError(f"Unknown note name: {base_name}")

            octave = int(octave_str)
            midi_num = 12 * (octave + 1) + pitch_map[base_name]
            freq = 440.0 * (2 ** ((midi_num - 69) / 12.0))

            # === 生成波形 ===
            sr = 44100
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)

            if waveform == "sine":
                wave = np.sin(2 * np.pi * freq * t)
            elif waveform == "square":
                wave = np.sign(np.sin(2 * np.pi * freq * t))
            elif waveform == "sawtooth":
                wave = 2 * (t * freq - np.floor(0.5 + t * freq))
            elif waveform == "triangle":
                wave = 2 * np.abs(2 * (t * freq - np.floor(0.5 + t * freq))) - 1
            else:
                wave = np.sin(2 * np.pi * freq * t)  # fallback

            # Apply blur (simple low-pass)
            if blur > 0:
                for i in range(1, len(wave)):
                    wave[i] = blur * wave[i] + (1 - blur) * wave[i - 1]

            # Apply decay envelope
            envelope = np.exp(-decay * t)
            wave = wave * envelope * volume

            # Ensure float32
            wave = wave.astype(np.float32)

            # === 写入内存 WAV ===
            buffer = BytesIO()
            sf.write(buffer, wave, sr, format='WAV', subtype='FLOAT')
            buffer.seek(0)
            audio_bytes = buffer.getvalue()

            # === 返回文件 ===
            filename = f"{note}_{waveform}.wav"
            yield self.create_blob_message(
                blob=audio_bytes,
                meta={
                    "mime_type": "audio/wav",
                    "filename": filename
                }
            )

        except Exception as e:
            raise ValueError(f"Failed to generate audio for note '{note}': {str(e)}")