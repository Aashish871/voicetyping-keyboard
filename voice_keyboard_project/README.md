# AI Voice Keyboard

A voice-to-text keyboard application using OpenAI's Whisper model for offline speech recognition.

## Features
- Real-time voice-to-text conversion
- Multiple microphone support
- System tray integration
- F9 shortcut for quick toggle
- Offline speech recognition using Whisper AI

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Select your preferred microphone from the dropdown menu
3. Click the microphone button or press F9 to start/stop recording
4. Speak clearly, and the text will be typed where your cursor is placed

## Shortcuts
- F9: Start/Stop recording
- Right-click tray icon for menu options

## Requirements
- Python 3.8+
- PyQt6
- OpenAI Whisper
- PyAudio
- Sounddevice

## License
MIT License