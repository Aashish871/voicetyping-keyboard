import pyaudio
import numpy as np
import threading
import time

class AudioManager:
    def __init__(self, callback=None):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 16000
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.callback = callback
        self.recording_thread = None
        self.current_device_index = None

    def start_recording(self, device_index=None):
        """Start continuous recording from selected device"""
        if self.is_recording:
            return

        self.current_device_index = device_index
        self.is_recording = True
        
        # Initialize audio stream
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.CHUNK
        )
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.stream = None

    def _record(self):
        """Continuous recording function"""
        while self.is_recording:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                if self.callback:
                    self.callback(audio_data)
            except Exception as e:
                print(f"Recording error: {e}")
                break

    def get_input_devices(self):
        """Get list of available input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels']
                })
        return devices

    def __del__(self):
        """Cleanup resources"""
        self.stop_recording()
        self.audio.terminate()