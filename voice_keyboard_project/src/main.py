import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import VoiceKeyboardGUI
from audio_manager import AudioManager
from transcriber import Transcriber
from pynput.keyboard import Controller

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

class VoiceKeyboardApp:
    def __init__(self):
        self.keyboard = Controller()
        self.audio_manager = AudioManager(callback=self.on_audio_segment)
        self.transcriber = Transcriber()
        self.gui = VoiceKeyboardGUI()
        
        # Connect GUI signals
        self.gui.toggle_button.clicked.connect(self.toggle_recording)
        self.gui.mic_combo.currentIndexChanged.connect(self.update_device)
        
        print("Voice Keyboard initialized and ready!")
    
    def toggle_recording(self, checked):
        """Toggle recording state"""
        if checked:
            device_index = self.gui.mic_combo.currentData()
            self.audio_manager.start_recording(device_index)
            self.gui.status_label.setText("Status: Recording")
            print("Recording started...")
        else:
            self.audio_manager.stop_recording()
            self.gui.status_label.setText("Status: Not Recording")
            print("Recording stopped.")

    def update_device(self):
        """Update recording device"""
        if self.audio_manager.is_recording:
            self.audio_manager.stop_recording()
            device_index = self.gui.mic_combo.currentData()
            self.audio_manager.start_recording(device_index)
            print(f"Switched to microphone: {self.gui.mic_combo.currentText()}")

    def on_audio_segment(self, audio_file):
        """Handle transcription of audio segment"""
        text = self.transcriber.transcribe(audio_file)
        if text:
            print(f"Transcribed: {text}")
            self.keyboard.type(text + " ")
            # Update GUI with transcribed text
            self.gui.update_transcription_display(text)

def main():
    if not check_ffmpeg():
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "FFmpeg Not Found",
                             "FFmpeg is required but not found on your system. "
                             "Please install FFmpeg and make sure it's available in your system PATH.")
        return

    app = QApplication(sys.argv)
    voice_keyboard = VoiceKeyboardApp()
    voice_keyboard.gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
