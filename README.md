# Whisper Subtitler

A lightweight drag-and-drop desktop GUI for transcribing video files (`.mkv`, `.mp4`, `.mov`, etc.) and generating clean, sentence-based `.srt` subtitles using Stable-Whisper.

## Features
- **Drag-and-Drop Interface:** Drop video files directly into the window.
- **Natural Sentence Splitting:** Regroups transcribed segments strictly around terminal punctuation (`.`, `?`, `!`).
- **Clean Subtitles:** Disables distracting word-by-word karaoke/highlighting tags.
- **Adjustable Model Selection:** Choose between `tiny`, `base`, `small`, `medium`, `turbo`, and `large-v3`.
- **Custom Line Length:** Configure maximum words per subtitle cue to prevent screen crowding.

## System Requirements
- Python 3.9+
- **FFmpeg** available on system `PATH` (e.g., `winget install Gyan.FFmpeg`).
- **NVIDIA GPU Acceleration (Optional):** Install PyTorch with CUDA:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  ```

## Installation

### Local Editable Install (Development)

```bash
git clone https://github.com/rpraleigh/whisper-subtitler.git
cd whisper-subtitler
pip install -e .
```

### Install Directly via Pip / GitHub

```bash
pip install git+https://github.com/rpraleigh/whisper-subtitler.git
```

## Usage

Run the registered console command from any command prompt:

```bash
subtitler
```
