#!/usr/bin/env python3
"""
Jarvis Simple - No heavy ML libraries
Uses macOS built-in speech recognition
"""

import subprocess
import os
import tempfile
import time

def speak(text):
    """Speak using macOS say command"""
    # Clean text for speaking
    text = text.replace('**', '').replace('*', '').replace('`', '')
    text = text.replace('#', '').replace('[', '').replace(']', '')
    subprocess.run(['say', '-v', 'Samantha', text])

def listen():
    """Record audio using macOS"""
    print("🎤 Recording for 5 seconds... Speak now!")
    
    # Record using sox (if available) or afrecord
    temp_file = tempfile.mktemp(suffix='.wav')
    
    try:
        # Try using sox
        subprocess.run([
            'rec', '-q', '-r', '16000', '-c', '1', temp_file, 
            'trim', '0', '5'
        ], timeout=10)
    except:
        # Fallback to afrecord (built-in)
        subprocess.run([
            'afrecord', '-d', '5', '-f', 'WAVE', temp_file
        ], timeout=10)
    
    return temp_file

def transcribe(audio_file):
    """Transcribe using whisper"""
    try:
        import mlx_whisper
        result = mlx_whisper.transcribe(audio_file)
        return result['text'].strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def get_response(text):
    """Get response from OpenClaw"""
    print(f"📤 Sending: {text}")
    
    result = subprocess.run(
        ['openclaw', 'agent', '--to', '+923147800991', '--message', text],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.stdout:
        return result.stdout.strip()
    return "Sorry, I couldn't get a response."

def main():
    print("=" * 50)
    print("🤖 JARVIS - Simple Voice Assistant")
    print("=" * 50)
    print("Press Enter to speak, or 'q' to quit")
    print()
    
    speak("Hello! I'm Jarvis. Press Enter when you want to talk to me.")
    
    while True:
        cmd = input("\n[Press Enter to speak, 'q' to quit] > ")
        
        if cmd.lower() == 'q':
            speak("Goodbye!")
            break
        
        # Record
        audio_file = listen()
        print("🔄 Processing...")
        
        # Transcribe
        text = transcribe(audio_file)
        
        # Clean up
        try:
            os.unlink(audio_file)
        except:
            pass
        
        if text:
            print(f"📝 You said: {text}")
            
            # Get response
            response = get_response(text)
            print(f"🤖 Jarvis: {response}")
            
            # Speak response
            speak(response)
        else:
            speak("Sorry, I didn't catch that. Try again.")

if __name__ == "__main__":
    main()
