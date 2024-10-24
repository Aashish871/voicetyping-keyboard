import whisper
import numpy as np
import threading
from queue import Queue
import torch
import time

class Transcriber:
    def __init__(self, model_size="tiny", language="en"):
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        self.language = language
        self.is_running = False
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
        self.transcription_thread = None
        self.callback = None
        self.silence_threshold = 0.01
        self.silence_duration = 0.5  # seconds
        self.last_audio_time = time.time()
        
        # Use CUDA if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            self.model.to(self.device)

    def start(self, callback=None):
        """Start the transcription process"""
        self.callback = callback
        self.is_running = True
        self.transcription_thread = threading.Thread(target=self._process_audio)
        self.transcription_thread.start()

    def stop(self):
        """Stop the transcription process"""
        self.is_running = False
        if self.transcription_thread:
            self.transcription_thread.join()
        self.transcription_thread = None
        self._clear_buffer()

    def add_audio(self, audio_data):
        """Add audio data to the buffer"""
        with self.buffer_lock:
            self.audio_buffer.extend(audio_data)
            self.last_audio_time = time.time()

    def _clear_buffer(self):
        """Clear the audio buffer"""
        with self.buffer_lock:
            self.audio_buffer = []

    def _process_audio(self):
        """Process audio data continuously"""
        while self.is_running:
            current_time = time.time()
            
            # Check if we have enough silence to process
            if (current_time - self.last_audio_time) > self.silence_duration:
                with self.buffer_lock:
                    if len(self.audio_buffer) > 0:
                        # Convert buffer to numpy array
                        audio_data = np.array(self.audio_buffer)
                        self.audio_buffer = []
                
                        # Process if we have enough audio
                        if len(audio_data) > self.RATE:  # Only process if more than 1 second
                            text = self._transcribe(audio_data)
                            if text and self.callback:
                                self.callback(text)
            
            time.sleep(0.1)  # Prevent CPU overuse

    def _transcribe(self, audio_data):
        """Transcribe audio data using Whisper"""
        try:
            # Normalize audio
            audio_data = audio_data.astype(np.float32)
            audio_data = audio_data / np.max(np.abs(audio_data))

            # Transcribe using Whisper
            result = self.model.transcribe(
                audio_data,
                language=self.language,
                fp16=False,
                task="transcribe"
            )
            
            return result["text"].strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return None