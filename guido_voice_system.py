import speech_recognition as sr
import pyttsx3
import time
import threading
from datetime import datetime

class GuidoVoiceSystem:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # System state
        self.is_activated = False
        self.last_activity_time = time.time()
        self.activation_timeout = 15 * 60  # 15 minutes
        self.check_interval = 10 * 60     # 10 minutes for object checking
        
        # Activation phrases
        self.activation_phrases = [
            "guido wake up",
            "guido activate", 
            "hey guido",
            "wake up guido",
            "hello guido"
        ]
        
        # Tool classes
        self.tool_classes = {
            'bolt': 0, 'hammer': 1, 'measuring tape': 2,
            'plier': 3, 'screwdriver': 4, 'wrench': 5
        }
        
        print("Guido Voice System Initialized!")
    
    def setup_tts(self):
        """Configure text-to-speech engine"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[1].id)  # Female voice
        self.tts_engine.setProperty('rate', 150)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Guido: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete!")
    
    def listen(self, timeout=7, phrase_time_limit=6):
        """Listen for voice input"""
        try:
            with self.microphone as source:
                print("\n🎤 Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            text = self.recognizer.recognize_google(audio).lower()
            print(f"👤 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition: {e}")
            return None
    
    def is_activation_command(self, text):
        """Check if the text contains activation phrases"""
        if not text:
            return False
        
        for phrase in self.activation_phrases:
            if phrase in text:
                return True
        return False
    
    def process_command(self, command):
        """Process voice commands"""
        self.last_activity_time = time.time()
        
        if any(tool in command for tool in ['bolt', 'hammer', 'measuring tape', 'plier', 'screwdriver', 'wrench']):
            self.handle_tool_request(command)
        elif any(word in command for word in ['guide', 'help', 'manual']):
            self.provide_guidance(command)
        elif any(word in command for word in ['deactivate', 'sleep', 'stop']):
            self.deactivate()
        elif 'time' in command:
            self.tell_time()
        else:
            self.speak("I didn't understand that command. Please try again.")
    
    def handle_tool_request(self, command):
        """Handle tool delivery request"""
        # Extract tool name from command
        tool = None
        for tool_name in self.tool_classes.keys():
            if tool_name in command:
                tool = tool_name
                break
        
        if tool:
            self.speak(f"I will bring you the {tool}. Please show me your hand.")
            # Here you would integrate with MediaPipe hand detection
            print(f"🤖 [ACTION] Delivering {tool} to user's hand")
        else:
            self.speak("I didn't catch which tool you need. Please say it again.")
    
    def provide_guidance(self, command):
        """Provide repair guidance"""
        if 'tire' in command or 'tyre' in command or 'puncture' in command:
            self.speak("Here's the procedure for repairing a punctured tire:")
            procedure = [
                "1. Secure the vehicle on a flat surface and apply parking brake",
                "2. Loosen the lug nuts before jacking up the vehicle",
                "3. Jack up the vehicle and remove the tire",
                "4. Locate the puncture and mark it",
                "5. Use a tire repair kit to fix the puncture",
                "6. Reinstall the tire and tighten lug nuts in a star pattern",
                "7. Lower the vehicle and double-check lug nuts"
            ]
            for step in procedure:
                print(f"   {step}")
                self.speak(step)
        else:
            self.speak("I can help with tire repair procedures. What specific guidance do you need?")
    
    def tell_time(self):
        """Tell current time"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {current_time}")
    
    def check_inactivity(self):
        """Check if robot should deactivate due to inactivity"""
        if self.is_activated and (time.time() - self.last_activity_time) > self.activation_timeout:
            self.speak("I'm deactivating due to inactivity. Say 'Guido wake up' when you need me.")
            self.is_activated = False
    
    def auto_organize_tools(self):
        """Simulate automatic tool organization"""
        if self.is_activated:
            print("🛠️ [AUTO-ORGANIZE] Checking and organizing tools by class...")
            self.speak("I'm organizing the tools according to their classes.")
            # This would integrate with your vision system
    
    def deactivate(self):
        """Deactivate the robot"""
        self.is_activated = False
        self.speak("Deactivating now. Goodbye!")
    
    def run(self):
        """Main system loop"""
        self.calibrate_microphone()
        self.speak("Voice system ready. Say 'Guido wake up' to activate me.")
        
        # Start background threads
        inactivity_thread = threading.Thread(target=self.monitor_inactivity, daemon=True)
        organization_thread = threading.Thread(target=self.monitor_organization, daemon=True)
        inactivity_thread.start()
        organization_thread.start()
        
        while True:
            try:
                if not self.is_activated:
                    # Listen for activation
                    text = self.listen(timeout=10, phrase_time_limit=3)
                    if text and self.is_activation_command(text):
                        self.is_activated = True
                        self.last_activity_time = time.time()
                        self.speak("I am activated sir! How can I assist you today?")
                
                else:
                    # Listen for commands
                    text = self.listen(timeout=8, phrase_time_limit=5)
                    if text:
                        self.process_command(text)
                    else:
                        print("⏰ No command detected, continuing to listen...")
                        
            except KeyboardInterrupt:
                self.speak("Shutting down Guido system. Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
    
    def monitor_inactivity(self):
        """Background thread to monitor inactivity"""
        while True:
            time.sleep(30)  # Check every 30 seconds
            self.check_inactivity()
    
    def monitor_organization(self):
        """Background thread for automatic organization"""
        while True:
            time.sleep(600)  # Check every 10 minutes
            if self.is_activated:
                self.auto_organize_tools()

# Test the system
if __name__ == "__main__":
    guido = GuidoVoiceSystem()
    guido.run()