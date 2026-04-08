#!/usr/bin/env python3
"""
Jarvis Lite - Lazy loading to avoid crashes
"""

import subprocess
import os
import sys

def main():
    print("=" * 50)
    print("🤖 JARVIS LITE")
    print("=" * 50)
    print("Commands: 'speak', 'quit'")
    print()
    
    # Use macOS say for greeting
    subprocess.run(['say', '-v', 'Samantha', 'Hello! I am Jarvis. Type speak to talk to me.'])
    
    while True:
        cmd = input("\n> ").strip().lower()
        
        if cmd in ['q', 'quit', 'exit']:
            subprocess.run(['say', '-v', 'Samantha', 'Goodbye!'])
            break
            
        elif cmd in ['s', 'speak']:
            # Record using macOS
            print("🎤 Recording for 5 seconds...")
            temp_file = '/tmp/jarvis_audio.wav'
            
            # Use sox for recording
            try:
                result = subprocess.run(
                    ['rec', '-q', '-r', '16000', '-c', '1', '-b', '16', temp_file, 'trim', '0', '5'],
                    timeout=10,
                    capture_output=True
                )
                print("✅ Recorded!")
            except FileNotFoundError:
                print("❌ 'sox' not installed. Installing...")
                subprocess.run(['brew', 'install', 'sox'])
                continue
            except subprocess.TimeoutExpired:
                print("Recording timed out")
                continue
            
            # Transcribe
            print("🔄 Transcribing...")
            try:
                # Import here to avoid crash at startup
                import mlx_whisper
                result = mlx_whisper.transcribe(temp_file)
                text = result['text'].strip()
                print(f"📝 You said: {text}")
            except Exception as e:
                print(f"Transcription error: {e}")
                continue
            
            if not text:
                subprocess.run(['say', '-v', 'Samantha', "Sorry, I didn't catch that."])
                continue
            
            # Send to OpenClaw
            print("💭 Thinking...")
            try:
                result = subprocess.run(
                    ['openclaw', 'agent', '--to', '+923147800991', '--message', text],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                response = result.stdout.strip() if result.stdout else "I processed your request."
                print(f"🤖 {response[:200]}...")
                
                # Clean and speak
                clean = response.replace('**', '').replace('*', '').replace('`', '')[:500]
                subprocess.run(['say', '-v', 'Samantha', clean])
                
            except Exception as e:
                print(f"Error: {e}")
                subprocess.run(['say', '-v', 'Samantha', 'Sorry, there was an error.'])
        
        else:
            print("Unknown command. Type 'speak' or 'quit'")

if __name__ == "__main__":
    main()
