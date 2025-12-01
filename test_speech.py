# guido_fixed.py - Improved version with better speech detection
import pyaudio
import json
import os
import time
import wave
from vosk import Model, KaldiRecognizer

class GuidoFixedAssistant:
    def __init__(self):
        self.model_path = "vosk-model-small-en-us-0.15"
        self.rate = 16000
        self.model = None
        self.recognizer = None
        self.audio = None
        
        self.setup_vosk()
        self.setup_procedures()
        
    def setup_vosk(self):
        """Initialize Vosk with better error handling"""
        if not os.path.exists(self.model_path):
            print("❌ Vosk model not found at:", self.model_path)
            print("💡 Make sure 'vosk-model-small-en-us-0.15' folder exists in current directory")
            return False
        
        try:
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.rate)
            self.audio = pyaudio.PyAudio()
            print("✅ Vosk initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Vosk setup failed: {e}")
            return False
    
    def setup_procedures(self):
        """Setup car maintenance procedures"""
        self.procedures = {
            "tire_change": {
                "title": "How to Change a Car Tire",
                "steps": [
                    "Find a safe, flat location and turn on hazard lights",
                    "Apply parking brake and place wheel wedges",
                    "Remove hubcap and loosen lug nuts",
                    "Jack up the vehicle about 6 inches",
                    "Remove lug nuts and take off flat tire",
                    "Mount spare tire and hand-tighten lug nuts",
                    "Lower vehicle and tighten lug nuts in star pattern",
                    "Replace hubcap and check tire pressure",
                    "Stow all equipment and have spare tire repaired"
                ]
            },
            "oil_change": {
                "title": "How to Change Engine Oil", 
                "steps": [
                    "Run engine for 5 minutes to warm oil, then turn off",
                    "Locate oil drain plug and oil filter",
                    "Place drain pan under drain plug", 
                    "Remove drain plug and drain old oil completely",
                    "Replace drain plug and washer",
                    "Remove old oil filter and lubricate new filter gasket",
                    "Install new oil filter hand-tight",
                    "Add new engine oil through fill hole",
                    "Check oil level with dipstick",
                    "Run engine and check for leaks",
                    "Properly dispose of old oil and filter"
                ]
            }
        }
    
    def listen_with_visual_feedback(self, duration=5):
        """Listen with visual feedback so you know it's working"""
        if not self.recognizer:
            return None
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=4096
        )
        
        print(f"🎤 Listening for {duration} seconds...")
        print("💡 SPEAK NOW! Say: 'Guido wake up'")
        print("📊 Audio level: [", end="")
        
        speech_detected = False
        frames = []
        
        # Listen for the specified duration
        for i in range(int(self.rate / 4096 * duration)):
            try:
                data = stream.read(4096, exception_on_overflow=False)
                frames.append(data)
                
                # Simple audio level indicator
                audio_level = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) 
                                for i in range(0, min(len(data), 100), 2))
                
                # Visual feedback
                if audio_level > 1000:
                    print("█", end="", flush=True)
                    speech_detected = True
                else:
                    print(".", end="", flush=True)
                
                # Check for speech recognition
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    if text:
                        stream.stop_stream()
                        stream.close()
                        print("] ✅ Speech detected!")
                        return text
                        
            except OSError as e:
                print(f"\n❌ Audio error: {e}")
                break
        
        print("]")  # End the progress bar
        
        # Check final result
        result = json.loads(self.recognizer.FinalResult())
        text = result.get('text', '').lower()
        
        stream.stop_stream()
        stream.close()
        
        if text:
            print(f"✅ Detected: '{text}'")
        elif speech_detected:
            print("❓ Audio detected but couldn't understand speech")
        else:
            print("🔇 No audio detected - check microphone")
        
        return text if text else None
    
    def speak(self, message):
        """Simulate speech output"""
        print(f"🤖 Guido: {message}")
    
    def process_command(self, command):
        """Process voice commands with fuzzy matching"""
        if not command:
            return True
        
        print(f"🔍 Command: '{command}'")
        
        # More flexible activation phrases
        activation_keywords = ['guido', 'wake', 'up', 'hello', 'hey', 'start']
        if sum(keyword in command for keyword in activation_keywords) >= 2:
            self.speak("Hello! I'm Guido, your car maintenance assistant!")
            self.speak("I can help with tire changes, oil changes, or tool delivery.")
            return True
        
        # Tool commands
        if any(word in command for word in ['tool', 'hammer', 'wrench', 'screwdriver', 'bolt']):
            if 'hammer' in command:
                self.speak("Delivering the hammer to your workstation.")
            elif 'range' in command or 'spanner' in command:
                self.speak("Here is the wrench.")
            elif 'screwdriver' in command:
                self.speak("Screwdriver coming right up!")
            else:
                self.speak("Which tool would you like me to bring?")
            return True
        
        # Maintenance procedures
        if any(word in command for word in ['tire', 'tyre', 'wheel']):
            self.guide_tire_change()
            return True
            
        if any(word in command for word in ['oil', 'engine']):
            self.guide_oil_change()
            return True
        
        # System commands
        if any(word in command for word in ['stop', 'sleep', 'deactivate', 'bye']):
            self.speak("Goodbye! Say 'Guido wake up' when you need me.")
            return False
        
        if 'time' in command:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
            return True
        
        self.speak("I can help with car maintenance. Try asking for tools or procedures.")
        return True
    
    def guide_tire_change(self):
        """Guide through tire change"""
        procedure = self.procedures["tire_change"]
        self.speak(procedure["title"])
        time.sleep(1)
        
        for i, step in enumerate(procedure['steps'], 1):
            self.speak(f"Step {i}: {step}")
            time.sleep(2)
    
    def guide_oil_change(self):
        """Guide through oil change"""
        procedure = self.procedures["oil_change"]
        self.speak(procedure["title"])
        time.sleep(1)
        
        for i, step in enumerate(procedure['steps'], 1):
            self.speak(f"Step {i}: {step}")
            time.sleep(2)
    
    def run_interactive_test(self):
        """Interactive test mode"""
        print("\n" + "="*60)
        print("🚗 GUIDO INTERACTIVE TEST MODE")
        print("💻 Testing speech recognition...")
        print("="*60)
        
        while True:
            print(f"\n🎤 Press Enter to start listening (or type 'quit' to exit): ")
            user_input = input().strip().lower()
            
            if user_input == 'quit':
                break
            
            print("🔄 Starting listening...")
            command = self.listen_with_visual_feedback(duration=6)
            
            if command:
                self.process_command(command)
            else:
                print("❌ No command recognized. Try speaking louder or closer to microphone.")
    
    def close(self):
        """Clean up"""
        if self.audio:
            self.audio.terminate()

# SIMPLE TEST - Run this first!
def simple_voice_test():
    """Very simple test to check basic functionality"""
    import speech_recognition as sr
    
    print("🎯 SIMPLE VOICE TEST (Using Google as backup)")
    print("💡 This will help us verify your microphone works")
    
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🔊 Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=2)
            print("🎤 Speak now! Say anything...")
            audio = r.listen(source, timeout=10)
            
            text = r.recognize_google(audio)
            print(f"✅ Google heard: '{text}'")
            return True
            
    except sr.UnknownValueError:
        print("❌ Google could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Google error: {e}")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
    
    return False

if __name__ == "__main__":
    print("🔧 Guido Assistant Troubleshooting")
    print("1. First, let's test your microphone with Google...")
    
    # Test with Google first (more reliable for testing)
    if simple_voice_test():
        print("\n✅ Microphone works! Now testing Vosk...")
        
        assistant = GuidoFixedAssistant()
        if assistant.model:
            assistant.run_interactive_test()
        else:
            print("❌ Vosk not available")
    else:
        print("\n❌ Microphone issue detected! Please check:")
        print("   • Is microphone connected?")
        print("   • Is microphone enabled in Windows?")
        print("   • Are you allowing microphone access?")
        print("   • Try using a headset microphone for better quality")
    
    input("\nPress Enter to exit...")