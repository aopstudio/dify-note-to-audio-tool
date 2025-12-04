# Note to Audio Synthesizer Plugin for Dify

[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-blue)](https://github.com/langgenius/dify)

A Dify plugin that converts musical note names (e.g., `C4`, `A#5`, `Eb3`) into synthesized audio files in WAV format. Supports multiple waveform types and customizable synthesis parameters.

---

## 📌 Overview

This plugin enables users or LLMs to generate short synthesized tones from standard musical notes using common oscillator waveforms:

- **Sine wave** – pure tone
- **Square wave** – rich harmonic content
- **Sawtooth wave** – bright, buzzy sound
- **Triangle wave** – soft with odd harmonics

The output is a mono, 44.1kHz, float32 WAV file suitable for playback, analysis, or further audio processing.

---

## ⚙️ Parameters

| Parameter | Type | Required | Default | Description |
|----------|------|--------|--------|-------------|
| `note` | string | ✅ Yes | — | Musical note in scientific pitch notation (e.g., `C4`, `A#5`, `Eb3`). Octave range: 0–8. |
| `duration` | number | ❌ No | `0.5` | Duration in seconds (0.1–10). |
| `waveform` | select | ❌ No | `sine` | Waveform type: `sine`, `square`, `sawtooth`, or `triangle`. |
| `blur` | number | ❌ No | `0.05` | Low-pass smoothing factor (0 = none, 1 = max blur). |
| `decay` | number | ❌ No | `5.0` | Exponential decay rate (higher = faster fade-out). |
| `volume` | number | ❌ No | `0.3` | Output amplitude (0.01–1.0). |

---

## 🎵 Example Usage

### Input
```json
{
  "note": "A4",
  "duration": 1.0,
  "waveform": "Square Wave",
  "volume": 0.5
}
```

### Output
- File name: `A4_square.wav`
- Format: WAV (44.1 kHz, mono, float32)
- Content: A synthesized square wave at 440 Hz, lasting 1 second, with exponential decay and specified volume.

---

## 🧠 Supported Notes

Uses **scientific pitch notation**:
- Notes: `C`, `C#`/`Db`, `D`, `D#`/`Eb`, `E`, `F`, `F#`/`Gb`, `G`, `G#`/`Ab`, `A`, `A#`/`Bb`, `B`
- Octaves: `0` to `8` (e.g., `C0` ≈ 16.35 Hz, `C8` ≈ 4186 Hz)

> 🔔 Flats (e.g., `Eb3`) are automatically converted to their sharp equivalents (`D#3`) internally.

---

## 🛠️ Technical Details

- **Sample rate**: 44,100 Hz
- **Channel**: Mono
- **Dependencies**: `numpy`, `soundfile`
- **Waveform generation**: Pure NumPy-based synthesis
- **Blur effect**: Simple first-order low-pass filter
- **Envelope**: Exponential decay (`exp(-decay * t)`)

---

## 📁 Installation in Dify

1. Place `note_to_audio_tool.py` in your Dify plugin directory (e.g., `tools/note_to_audio.py`).
2. Ensure the plugin manifest (`plugin.yaml` or equivalent) includes the configuration provided in your spec.
3. Restart Dify or reload plugins.
4. The tool will appear as **“Note to Audio Synthesizer”** (or **“音名转音频合成器”** in Chinese).

---

## 🌐 Localization

Fully supports English and Simplified Chinese:

- **English (en_US)**: Default labels and descriptions
- **Chinese (zh_Hans)**: Fully translated UI strings

---
## Author

Created by [aopstudio](https://github.com/aopstudio)

---
## Repository

https://github.com/aopstudio/dify-note-to-audio-tool

---

> 🎶 Turn notes into sound—right inside your AI workflow!