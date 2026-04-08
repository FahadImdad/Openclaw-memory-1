#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Real-time Two-Way Communication
Speak → Jarvis responds with voice!
"""

import tkinter as tk
import threading
import pyaudio
import numpy as np
import wave
import tempfile
import subprocess
import os
import json
import re

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
        self.root.geometry("450x400")
        self.root.configure(bg='#1a1a2e')
        
        self.listening = False
        self.wake_word_active = False
        self.speaking = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.root, 
            text="🤖 JARVIS", 
            font=('Helvetica', 28, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title.pack(pady=15)
        
        # Status indicator (big circle)
        self.canvas = tk.Canvas(self.root, width=100, height=100, bg='#1a1a2e', highlightthickness=0)
        self.canvas.pack(pady=10)
        self.status_circle = self.canvas.create_oval(10, 10, 90, 90, fill='#333366', outline='#4444aa', width=3)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=('Helvetica', 16),
            fg='#ffffff',
            bg='#1a1a2e'
        )
        self.status_label.pack(pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        # Speak button
        self.btn = tk.Button(
            btn_frame,
            text="🎤 SPEAK",
            font=('Helvetica', 16, 'bold'),
            fg='white',
            bg='#4a4a8a',
            activebackground='#6a6aaa',
            width=12,
            height=2,
            command=self.toggle_listen
        )
        self.btn.pack(side='left', padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ STOP",
            font=('Helvetica', 16, 'bold'),
            fg='white',
            bg='#8a4a4a',
            activebackground='#aa6a6a',
            width=10,
            height=2,
            command=self.stop_speaking
        )
        self.stop_btn.pack(side='left', padx=5)
        
        # Wake word toggle
        self.wake_var = tk.BooleanVar(value=False)
        wake_check = tk.Checkbutton(
            self.root,
            text="🎧 Always listen for 'Hey Jarvis'",
            variable=self.wake_var,
            command=self.toggle_wake_word,
            font=('Helvetica', 12),
            fg='#aaaaaa',
            bg='#1a1a2e',
            selectcolor='#2a2a4e',
            activebackground='#1a1a2e'
        )
        wake_check.pack(pady=10)
        
        # Conversation log
        log_frame = tk.Frame(self.root, bg='#1a1a2e')
        log_frame.pack(pady=10, fill='both', expand=True, padx=20)
        
        self.output = tk.Text(
            log_frame,
            height=6,
            font=('Helvetica', 11),
            fg='#00ff00',
            bg='#0a0a1e',
            wrap='word',
            state='disabled'
        )
        self.output.pack(fill='both', expand=True)
        
        # Configure tags for colored text
        self.output.tag_configure('user', foreground='#00aaff')
        self.output.tag_configure('jarvis', foreground='#00ff00')
        self.output.tag_configure('system', foreground='#888888')
        
    def log(self, message, tag='system'):
        self.output.configure(state='normal')
        self.output.insert('end', message + '\n', tag)
        self.output.see('end')
        self.output.configure(state='disabled')
        
    def set_status(self, status, color='#333366'):
        self.status_var.set(status)
        self.canvas.itemconfig(self.status_circle, fill=color)
        self.root.update()
        
    def toggle_listen(self):
        if self.listening or self.speaking:
            return
        threading.Thread(target=self.listen_and_respond, daemon=True).start()
        
    def stop_speaking(self):
        """Stop any ongoing speech"""
        subprocess.run(['killall', 'say'], capture_output=True)
        self.speaking = False
        self.set_status("Ready", '#333366')
        
    def listen_and_respond(self):
        self.listening = True
        self.btn.configure(state='disabled')
        self.set_status("🎤 Listening...", '#ff4444')
        
        # Play start sound
        os.system('afplay /System/Library/Sounds/Pop.aiff &')
        
        try:
            # Record audio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Play end sound
            os.system('afplay /System/Library/Sounds/Purr.aiff &')
            
            self.set_status("🔄 Processing...", '#ffaa00')
            
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
                text = "Test message - Whisper not available"
            
            os.unlink(temp_path)
            
            if text and len(text) > 2:
                self.log(f"You: {text}", 'user')
                self.set_status("💭 Thinking...", '#aa00ff')
                
                # Get response from OpenClaw
                response = self.get_jarvis_response(text)
                
                if response:
                    self.log(f"Jarvis: {response}", 'jarvis')
                    self.speak(response)
                else:
                    self.log("No response received", 'system')
            else:
                self.log("Didn't catch that - try again", 'system')
                
        except Exception as e:
            self.log(f"Error: {e}", 'system')
        finally:
            self.listening = False
            self.btn.configure(state='normal')
            if not self.speaking:
                self.set_status("Ready", '#333366')
            
    def get_jarvis_response(self, text):
        """Get response from OpenClaw agent"""
        try:
            result = subprocess.run(
                ['openclaw', 'agent', '--to', '+923147800991', '--message', text, '--json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    # Extract the assistant's reply
                    if 'reply' in data:
                        return self.clean_response(data['reply'])
                    elif 'content' in data:
                        return self.clean_response(data['content'])
                    elif 'message' in data:
                        return self.clean_response(data['message'])
                except json.JSONDecodeError:
                    # Not JSON, maybe plain text
                    return self.clean_response(result.stdout)
            
            return None
        except subprocess.TimeoutExpired:
            return "Sorry, that took too long. Try again?"
        except Exception as e:
            return f"Error getting response: {e}"
            
    def clean_response(self, text):
        """Clean up the response for speaking"""
        if not text:
            return None
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)  # Code
        text = re.sub(r'#{1,6}\s', '', text)  # Headers
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
        text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)  # Emojis
        return text.strip()
            
    def speak(self, text):
        """Speak text using macOS say command"""
        if not text:
            return
            
        self.speaking = True
        self.set_status("🔊 Speaking...", '#00ff00')
        
        def speak_thread():
            try:
                # Use Samantha voice (nice female voice on macOS)
                subprocess.run(
                    ['say', '-v', 'Samantha', '-r', '180', text],
                    check=True
                )
            except:
                pass
            finally:
                self.speaking = False
                self.root.after(0, lambda: self.set_status("Ready", '#333366'))
        
        threading.Thread(target=speak_thread, daemon=True).start()
            
    def toggle_wake_word(self):
        if self.wake_var.get():
            self.start_wake_word()
        else:
            self.stop_wake_word()
            
    def start_wake_word(self):
        if not MODELS_AVAILABLE:
            self.log("Wake word models not available", 'system')
            self.wake_var.set(False)
            return
            
        self.wake_word_active = True
        threading.Thread(target=self.wake_word_loop, daemon=True).start()
        self.log("🎧 Listening for 'Hey Jarvis'...", 'system')
        
    def stop_wake_word(self):
        self.wake_word_active = False
        self.log("🔇 Wake word disabled", 'system')
        
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
                if self.listening or self.speaking:
                    continue
                    
                audio = stream.read(CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(audio, dtype=np.int16)
                prediction = oww.predict(audio_np)
                
                for name, score in prediction.items():
                    if "jarvis" in name.lower() and score > THRESHOLD:
                        self.root.after(0, lambda: self.log("✨ Hey Jarvis!", 'system'))
                        self.root.after(0, self.toggle_listen)
                        oww.reset()
                        import time
                        time.sleep(0.5)
                        while self.listening or self.speaking:
                            time.sleep(0.1)
                            
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Wake word error: {e}", 'system'))
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Jarvis...")
    app = JarvisApp()
    app.run()
