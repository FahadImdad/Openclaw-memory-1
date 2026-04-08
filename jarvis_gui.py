#!/usr/bin/env python3
"""
Jarvis Voice Assistant - GUI Version
A simple GUI for voice commands to OpenClaw
"""

import tkinter as tk
from tkinter import ttk
import threading
import pyaudio
import numpy as np
import wave
import tempfile
import subprocess
import os

# Try importing the models
try:
    from openwakeword.model import Model
    import mlx_whisper
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: {e}")
    MODELS_AVAILABLE = False

# Audio settings
CHUNK = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
THRESHOLD = 0.5

class JarvisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis")
        self.root.geometry("400x300")
        self.root.configure(bg='#1a1a2e')
        
        # State
        self.listening = False
        self.wake_word_active = False
        self.audio_stream = None
        self.pyaudio_instance = None
        self.oww_model = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.root, 
            text="🤖 JARVIS", 
            font=('Helvetica', 24, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title.pack(pady=20)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=('Helvetica', 14),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=10)
        
        # Big button
        self.btn = tk.Button(
            self.root,
            text="🎤 SPEAK",
            font=('Helvetica', 18, 'bold'),
            fg='white',
            bg='#4a4a8a',
            activebackground='#6a6aaa',
            width=15,
            height=2,
            command=self.toggle_listen
        )
        self.btn.pack(pady=20)
        
        # Wake word toggle
        self.wake_var = tk.BooleanVar(value=False)
        wake_check = tk.Checkbutton(
            self.root,
            text="Always listen for 'Hey Jarvis'",
            variable=self.wake_var,
            command=self.toggle_wake_word,
            fg='#aaaaaa',
            bg='#1a1a2e',
            selectcolor='#2a2a4e',
            activebackground='#1a1a2e',
            activeforeground='#ffffff'
        )
        wake_check.pack(pady=10)
        
        # Output
        self.output = tk.Text(
            self.root,
            height=4,
            width=45,
            font=('Helvetica', 10),
            fg='#00ff00',
            bg='#0a0a1e',
            state='disabled'
        )
        self.output.pack(pady=10)
        
    def log(self, message):
        self.output.configure(state='normal')
        self.output.insert('end', message + '\n')
        self.output.see('end')
        self.output.configure(state='disabled')
        
    def set_status(self, status, color='#ffffff'):
        self.status_var.set(status)
        self.status_label.configure(fg=color)
        self.root.update()
        
    def toggle_listen(self):
        if self.listening:
            return
        threading.Thread(target=self.listen_and_transcribe, daemon=True).start()
        
    def listen_and_transcribe(self):
        self.listening = True
        self.btn.configure(state='disabled', bg='#ff4444')
        self.set_status("🎤 Listening...", '#ff4444')
        
        try:
            # Initialize audio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            # Record
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.set_status("🔄 Transcribing...", '#ffaa00')
            
            # Save and transcribe
            audio_data = b''.join(frames)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wf = wave.open(f.name, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(audio_data)
                wf.close()
                temp_path = f.name
            
            if MODELS_AVAILABLE:
                result = mlx_whisper.transcribe(temp_path)
                text = result['text'].strip()
            else:
                text = "[Whisper not available]"
            
            os.unlink(temp_path)
            
            if text:
                self.log(f"You: {text}")
                self.set_status("📤 Sending...", '#00aaff')
                self.send_to_openclaw(text)
            else:
                self.log("Couldn't understand that")
                
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.listening = False
            self.btn.configure(state='normal', bg='#4a4a8a')
            self.set_status("Ready", '#ffffff')
            
    def send_to_openclaw(self, text):
        try:
            result = subprocess.run(
                ['openclaw', 'agent', '--to', '+923147800991', '--message', text, '--deliver'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                self.log("✅ Sent to Jarvis!")
                self.set_status("✅ Sent!", '#00ff00')
            else:
                self.log(f"Error: {result.stderr[:100]}")
        except Exception as e:
            self.log(f"Send error: {e}")
            
    def toggle_wake_word(self):
        if self.wake_var.get():
            self.start_wake_word()
        else:
            self.stop_wake_word()
            
    def start_wake_word(self):
        if not MODELS_AVAILABLE:
            self.log("Models not available")
            self.wake_var.set(False)
            return
            
        self.wake_word_active = True
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        self.log("🎧 Wake word listening started")
        
    def stop_wake_word(self):
        self.wake_word_active = False
        self.log("🔇 Wake word listening stopped")
        
    def wake_word_loop(self):
        try:
            oww = Model(wakeword_models=["hey_jarvis_v0.1"], inference_framework='onnx')
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            while self.wake_word_active:
                audio = stream.read(CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(audio, dtype=np.int16)
                prediction = oww.predict(audio_np)
                
                for name, score in prediction.items():
                    if "jarvis" in name.lower() and score > THRESHOLD:
                        self.root.after(0, lambda: self.log("✨ Hey Jarvis detected!"))
                        self.root.after(0, self.toggle_listen)
                        oww.reset()
                        # Wait for recording to finish
                        while self.listening:
                            pass
                            
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Wake word error: {e}"))
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = JarvisApp()
    app.run()
