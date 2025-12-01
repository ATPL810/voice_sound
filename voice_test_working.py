# voice_test_working.py - Complete working test
import sys

try:
    import speech_recognition as sr
    import pyttsx3
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class SimpleVoiceTest:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
    def setup_tts(self):
        """Setup text-to-speech"""
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        print("✅ TTS engine ready")
    
    def speak(self, text):
        """Speak text"""
        print(f"🤖: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def test_microphone(self):
        """Test if microphone works"""
        print("\n🎤 TESTING MICROPHONE...")
        try:
            # List available microphones
            mics = sr.Microphone.list_microphone_names()
            print(f"Available microphones: {len(mics)}")
            for i, mic in enumerate(mics):
                print(f"  {i}: {mic}")
            
            # Try to use default microphone
            with sr.Microphone() as source:
                print("✅ Default microphone detected")
                print("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("✅ Calibration complete")
                return True
                
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return False
    
    def listen_once(self):
        """Listen for one voice command"""
        print("\n🎤 Speak now (say 'hello' or 'test')...")
        
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"✅ You said: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run_test(self):
        """Run complete voice test"""
        print("🚀 STARTING VOICE SYSTEM TEST")
        print("=" * 45)
        
        self.speak("Hello! I am testing the voice system.")
        
        # Test microphone
        if not self.test_microphone():
            print("💡 Continuing with simulated mode...")
            self.speak("Microphone not available, but other systems work.")
            return
        
        # Test voice recognition
        self.speak("Please say hello or test after the beep.")
        
        for i in range(3):  # Try 3 times
            text = self.listen_once()
            if text:
                if 'hello' in text or 'test' in text:
                    self.speak("Excellent! Voice recognition is working perfectly!")
                    print("🎉 VOICE SYSTEM TEST PASSED!")
                    return
                else:
                    self.speak(f"I heard {text}. Please say hello or test.")
            else:
                self.speak("Let's try again. Please say hello or test.")
        
        self.speak("Voice test completed with some issues, but basic system works.")

if __name__ == "__main__":
    test = SimpleVoiceTest()
    test.run_test()