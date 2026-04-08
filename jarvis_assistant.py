#!/usr/bin/env python3
"""
Jarvis Voice Assistant
Listens for "Hey Jarvis" and sends your command to OpenClaw
"""

import pyaudio
import numpy as np
import wave
import tempfile
import subprocess
import os
from openwakeword.model import Model
import mlx_whisper

# Audio settings
CHUNK = 1280  # OpenWakeWord expects 80ms chunks at 16kHz
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5  # How long to record after wake word

# Wake word threshold (adjust if too sensitive or not sensitive enough)
THRESHOLD = 0.5

def play_sound(sound_type):
    """Play a sound to indicate listening/done"""
    if sound_type == "wake":
        os.system('afplay /System/Library/Sounds/Pop.aiff &')
    elif sound_type == "done":
        os.system('afplay /System/Library/Sounds/Purr.aiff &')

def record_command(stream, seconds=RECORD_SECONDS):
    """Record audio after wake word detected"""
    print("🎤 Listening...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    return b''.join(frames)

def transcribe_audio(audio_data):
    """Transcribe audio using mlx-whisper"""
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(RATE)
        wf.writeframes(audio_data)
        wf.close()
        temp_path = f.name
    
    try:
        result = mlx_whisper.transcribe(temp_path)
        return result['text'].strip()
    finally:
        os.unlink(temp_path)

def send_to_openclaw(text):
    """Send command to OpenClaw via CLI"""
    print(f"📤 Sending: {text}")
    # Use openclaw agent command with delivery
    result = subprocess.run(
        ['openclaw', 'agent', '--to', '+923147800991', '--message', text, '--deliver'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Sent!")
        if result.stdout:
            print(f"Response: {result.stdout[:200]}...")
    else:
        print(f"❌ Error: {result.stderr}")

def main():
    print("🤖 Jarvis Voice Assistant")
    print("=" * 40)
    print("Say 'Hey Jarvis' to activate")
    print("Press Ctrl+C to quit")
    print("=" * 40)
    
    # Initialize wake word model (use onnx version)
    owwModel = Model(
        wakeword_models=["hey_jarvis_v0.1"],
        inference_framework='onnx'
    )
    
    # Initialize audio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("\n👂 Listening for 'Hey Jarvis'...\n")
    
    try:
        while True:
            # Get audio chunk
            audio = stream.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(audio, dtype=np.int16)
            
            # Check for wake word
            prediction = owwModel.predict(audio_np)
            
            # Check if "hey_jarvis" was detected
            for mdl_name, score in prediction.items():
                if "jarvis" in mdl_name.lower() and score > THRESHOLD:
                    print(f"\n✨ Wake word detected! (score: {score:.2f})")
                    play_sound("wake")
                    
                    # Record command
                    audio_data = record_command(stream)
                    play_sound("done")
                    
                    # Transcribe
                    print("🔄 Transcribing...")
                    text = transcribe_audio(audio_data)
                    
                    if text:
                        print(f"📝 You said: {text}")
                        send_to_openclaw(text)
                    else:
                        print("❓ Couldn't understand that")
                    
                    print("\n👂 Listening for 'Hey Jarvis'...\n")
                    
                    # Reset model state
                    owwModel.reset()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
