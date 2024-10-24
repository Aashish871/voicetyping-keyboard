"""
Voice Keyboard Application Package
A voice-to-text application using Whisper AI for offline speech recognition.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Export main classes for easy import
from .audio_manager import AudioManager
from .transcriber import Transcriber
from .gui import VoiceKeyboardGUI

# Version info
VERSION_INFO = {
    "version": __version__,
    "whisper_support": ["tiny", "base", "small", "medium", "large"],
    "features": [
        "Real-time voice-to-text",
        "Multiple microphone support",
        "System tray integration",
        "F9 shortcut support",
        "Settings persistence"
    ]
}