from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QComboBox, QLabel, QSystemTrayIcon, QMenu,
                           QTextEdit, QStyle)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QShortcut, QKeySequence
import sys
import sounddevice as sd
import json
import os

class VoiceKeyboardGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Keyboard")
        self.setFixedSize(400, 300)
        
        # Initialize the system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.setup_tray()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Microphone selection
        mic_label = QLabel("Select Microphone:")
        self.mic_combo = QComboBox()
        self.populate_mic_devices()
        
        # Status and last transcription
        self.status_label = QLabel("Status: Not Recording")
        self.last_text_label = QLabel("Last transcribed text will appear here")
        self.last_text_label.setWordWrap(True)
        
        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Transcribed text will appear here...")
        
        # Toggle button with icon
        self.toggle_button = QPushButton("Start Recording (F9)")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(150, 50)
        self.setup_button_icon()
        
        # Add widgets to layout
        layout.addWidget(mic_label)
        layout.addWidget(self.mic_combo)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_text_label)
        layout.addWidget(self.text_display)
        layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set up keyboard shortcut
        self.setup_shortcut()
        
        # Load saved settings
        self.load_settings()

    def setup_tray(self):
        """Set up system tray icon with proper path handling"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'mic-icon.svg')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
        else:
            print(f"Warning: Icon not found at {icon_path}")
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_button_icon(self):
        """Set up the microphone button icon"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'mic-icon.svg')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.toggle_button.setIcon(icon)
            self.toggle_button.setIconSize(QSize(32, 32))
        else:
            print(f"Warning: Button icon not found at {icon_path}")

    def populate_mic_devices(self):
        """Get available audio input devices"""
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        for device in input_devices:
            self.mic_combo.addItem(f"{device['name']}", device['index'])

    def setup_shortcut(self):
        """Set up F9 shortcut for toggle recording"""
        shortcut = QShortcut(QKeySequence("F9"), self)
        shortcut.activated.connect(self.toggle_recording)

    def toggle_recording(self):
        """Toggle recording state"""
        self.toggle_button.setChecked(not self.toggle_button.isChecked())
        if self.toggle_button.isChecked():
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording"""
        self.toggle_button.setText("Stop Recording (F9)")
        self.status_label.setText("Status: Recording")
        self.text_display.clear()
        selected_device = self.mic_combo.currentData()
        self.save_settings()

    def stop_recording(self):
        """Stop recording"""
        self.toggle_button.setText("Start Recording (F9)")
        self.status_label.setText("Status: Not Recording")

    def update_transcription_display(self, text):
        """Update the text display with new transcription"""
        current_text = self.text_display.toPlainText()
        if current_text:
            self.text_display.append(text)
        else:
            self.text_display.setText(text)
        self.text_display.verticalScrollBar().setValue(
            self.text_display.verticalScrollBar().maximum()
        )
        self.last_text_label.setText(f"Last: {text[:50]}...")

    def save_settings(self):
        """Save current settings"""
        settings = {
            "selected_mic": self.mic_combo.currentIndex()
        }
        os.makedirs("config", exist_ok=True)
        with open("config/settings.json", "w") as f:
            json.dump(settings, f, indent=4)

    def load_settings(self):
        """Load saved settings"""
        try:
            with open("config/settings.json", "r") as f:
                settings = json.load(f)
                self.mic_combo.setCurrentIndex(settings.get("selected_mic", 0))
        except (FileNotFoundError, json.JSONDecodeError):
            default_settings = {
                "selected_mic": 0
            }
            os.makedirs("config", exist_ok=True)
            with open("config/settings.json", "w") as f:
                json.dump(default_settings, f, indent=4)

    def closeEvent(self, event):
        """Override close event to minimize to tray"""
        event.ignore()
        self.hide()