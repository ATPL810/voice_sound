import pyaudio
import wave
import os
import time
import numpy as np
from scipy import signal
import noisereduce as nr

class VoiceDataCollector:
    def __init__(self, data_dir="voice_dataset"):
        self.data_dir = data_dir
        self.create_folder_structure()
        
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 3
        
        self.audio = pyaudio.PyAudio()
        
        # Noise reduction settings
        self.noise_profile = None
        self.is_noise_profile_captured = False
    
    def create_folder_structure(self):
        """Create organized folder structure with enhanced guide commands"""
        
        # 1. ACTIVATION PHRASES
        activation_phrases = [
            "guido_wake_up",
            "guido_activate", 
            "hey_guido",
            "wake_up_guido",
            "hello_guido"
        ]
        
        # 2. TOOL DELIVERY COMMANDS
        tool_commands = [
            "give_me_bolt", "give_me_hammer", "give_me_measuring_tape",
            "give_me_plier", "give_me_screwdriver", "give_me_wrench"
        ]
        
        # 3. ENHANCED MANUAL READING COMMANDS
        manual_commands = [
            "read_manual",
            "guide_me",
            "help_me",
            "show_procedure",
            "how_to_change_tire",
            "how_to_replace_tire",
            "tire_change_guide",
            "change_car_tire",
            "how_to_change_engine_oil",
            "engine_oil_change",
            "oil_change_guide",
            "change_oil",
            "car_maintenance",
            "repair_instructions"
        ]
        
        # 4. REARRANGEMENT COMMANDS
        rearrangement_commands = [
            "arrange_tools",
            "organize_tools", 
            "clean_up",
            "put_in_order"
        ]
        
        # 5. SYSTEM COMMANDS
        system_commands = [
            "deactivate",
            "go_to_sleep", 
            "stop",
            "what_time_is_it"
        ]
        
        # Create all folders
        categories = {
            "activation": activation_phrases,
            "tool_delivery": tool_commands,
            "manual_reading": manual_commands,
            "rearrangement": rearrangement_commands,
            "system": system_commands
        }
        
        for category, phrases in categories.items():
            for phrase in phrases:
                os.makedirs(f"{self.data_dir}/{category}/{phrase}", exist_ok=True)
        
        print("✅ Complete folder structure created!")
        print("📁 Categories: Activation, Tool Delivery, Manual Reading, Rearrangement, System")
    
    def record_high_quality_sample(self, category, subfolder, phrase, sample_number):
        """Record with noise reduction and audio enhancement"""
        filename = f"{self.data_dir}/{category}/{subfolder}/{phrase}_{sample_number:03d}.wav"
        
        # WAIT FOR ENTER BEFORE STARTING RECORDING
        input(f"    Press Enter to start recording sample {sample_number}...")
        
        print("    🎤 Recording NOW... Speak clearly!")
        print(f"    Say: '{self.get_spoken_phrase(phrase)}'")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        print("    [", end="")
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            print("█", end="", flush=True)  # Progress indicator
        
        print("]")
        print("    ✅ Recording complete!")
        
        stream.stop_stream()
        stream.close()
        
        # Process audio
        raw_audio = b''.join(frames)
        audio_array = np.frombuffer(raw_audio, dtype=np.int16)
        
        # Apply noise reduction and enhancement
        print("    🔊 Processing audio (noise reduction)...")
        clean_audio = self.apply_noise_reduction(audio_array)
        enhanced_audio = self.apply_audio_enhancement(clean_audio)
        
        # Save processed recording
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(enhanced_audio.tobytes())
        wf.close()
        
        print(f"    💾 Saved: {filename}")
        return filename
    
    def get_spoken_phrase(self, phrase):
        """Convert folder names to spoken phrases"""
        phrase_map = {
            # Activation
            "guido_wake_up": "Guido wake up",
            "guido_activate": "Guido activate",
            "hey_guido": "Hey Guido",
            "wake_up_guido": "Wake up Guido",
            "hello_guido": "Hello Guido",
            
            # Tool Delivery
            "give_me_bolt": "Give me the bolt",
            "give_me_hammer": "Give me the hammer",
            "give_me_measuring_tape": "Give me the measuring tape",
            "give_me_plier": "Give me the plier",
            "give_me_screwdriver": "Give me the screwdriver",
            "give_me_wrench": "Give me the wrench",
            
            # Enhanced Manual Reading
            "read_manual": "Read the manual",
            "guide_me": "Guide me",
            "help_me": "Help me",
            "show_procedure": "Show the procedure",
            "how_to_change_tire": "How to change a tire",
            "how_to_replace_tire": "How to replace a tire",
            "tire_change_guide": "Tire change guide",
            "change_car_tire": "Change car tire",
            "how_to_change_engine_oil": "How to change engine oil",
            "engine_oil_change": "Engine oil change",
            "oil_change_guide": "Oil change guide",
            "change_oil": "Change oil",
            "car_maintenance": "Car maintenance",
            "repair_instructions": "Repair instructions",
            
            # Rearrangement
            "arrange_tools": "Arrange the tools",
            "organize_tools": "Organize the tools",
            "clean_up": "Clean up",
            "put_in_order": "Put tools in order",
            
            # System
            "deactivate": "Deactivate",
            "go_to_sleep": "Go to sleep",
            "stop": "Stop",
            "what_time_is_it": "What time is it"
        }
        
        return phrase_map.get(phrase, phrase.replace('_', ' '))
    
    def capture_noise_profile(self, duration=2):
        """Capture ambient noise profile for noise reduction"""
        print("\n🔊 Capturing ambient noise profile...")
        print("Please stay silent for 2 seconds...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        noise_frames = []
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            noise_frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Convert to numpy array for noise reduction
        noise_audio = b''.join(noise_frames)
        noise_array = np.frombuffer(noise_audio, dtype=np.int16)
        self.noise_profile = noise_array.astype(np.float32)
        self.is_noise_profile_captured = True
        
        print("✅ Noise profile captured!")
        return self.noise_profile
    
    def apply_noise_reduction(self, audio_data):
        """Apply noise reduction to recorded audio"""
        if not self.is_noise_profile_captured:
            return audio_data
        
        try:
            # Convert to float32 for processing
            audio_float = audio_data.astype(np.float32)
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio_float,
                sr=self.rate,
                y_noise=self.noise_profile,
                prop_decrease=0.8,  # Reduce 80% of noise
                stationary=True
            )
            
            # Convert back to int16
            return reduced_noise.astype(np.int16)
            
        except Exception as e:
            print(f"⚠️  Noise reduction failed: {e}")
            return audio_data
    
    def apply_audio_enhancement(self, audio_data):
        """Apply basic audio enhancement"""
        try:
            # Normalize audio
            audio_float = audio_data.astype(np.float32)
            max_val = np.max(np.abs(audio_float))
            if max_val > 0:
                audio_float = audio_float / max_val * 0.9  # Normalize to 90% of max
            
            # Apply high-pass filter to remove low-frequency noise
            sos = signal.butter(4, 100, 'hp', fs=self.rate, output='sos')
            filtered_audio = signal.sosfilt(sos, audio_float)
            
            # Convert back to int16
            enhanced_audio = (filtered_audio * 32767).astype(np.int16)
            return enhanced_audio
            
        except Exception as e:
            print(f"⚠️  Audio enhancement failed: {e}")
            return audio_data
    
    def setup_recording_environment(self):
        """Setup optimal recording environment"""
        print("\n🎧 SETTING UP OPTIMAL RECORDING ENVIRONMENT")
        print("=" * 50)
        print("📝 RECORDING TIPS:")
        print("• Find a quiet room with minimal background noise")
        print("• Close windows and doors to reduce external noise")
        print("• Use a good quality microphone if possible")
        print("• Speak clearly and at consistent volume")
        print("• Keep consistent distance from microphone")
        print("• Avoid breathing directly into microphone")
        print("=" * 50)
        
        # Capture noise profile
        self.capture_noise_profile()
    
    def collect_manual_reading_commands(self, samples_per_command=4):
        """Collect enhanced manual reading command samples"""
        commands = {
            "read_manual": "Read the manual",
            "guide_me": "Guide me",
            "help_me": "Help me",
            "how_to_change_tire": "How to change a tire",
            "tire_change_guide": "Tire change guide",
            "how_to_change_engine_oil": "How to change engine oil",
            "oil_change_guide": "Oil change guide",
            "change_oil": "Change oil"
        }
        
        print("=== COLLECTING MANUAL READING COMMANDS ===")
        print("Includes tire change and engine oil change procedures!")
        print("You need to press Enter before EVERY recording\n")
        
        for folder_name, spoken_command in commands.items():
            print(f"\n📁 Now recording: '{spoken_command}'")
            print(f"Folder: manual_reading/{folder_name}/")
            print(f"Need to record {samples_per_command} samples")
            
            input("Press Enter to start recording this command category...")
            
            for i in range(samples_per_command):
                print(f"\n🎤 Sample {i+1}/{samples_per_command}")
                self.record_high_quality_sample('manual_reading', folder_name, folder_name, i+1)
                
                if i < samples_per_command - 1:
                    print("    ⏸️  Ready for next sample...")
            
            print(f"✅ Completed {samples_per_command} samples for '{spoken_command}'\n")
            print("-" * 50)

    # [Keep other collection methods similar but use record_high_quality_sample]
    def collect_activation_phrases(self, samples_per_phrase=8):
        phrases = {
            "guido_wake_up": "Guido wake up",
            "guido_activate": "Guido activate", 
            "hey_guido": "Hey Guido",
            "wake_up_guido": "Wake up Guido",
            "hello_guido": "Hello Guido"
        }
        
        print("=== COLLECTING ACTIVATION PHRASES ===")
        for folder_name, spoken_phrase in phrases.items():
            print(f"\n📁 Now recording: '{spoken_phrase}'")
            input("Press Enter to start recording this phrase category...")
            
            for i in range(samples_per_phrase):
                print(f"\n🎤 Sample {i+1}/{samples_per_phrase}")
                self.record_high_quality_sample('activation', folder_name, folder_name, i+1)
                
                if i < samples_per_phrase - 1:
                    print("    ⏸️  Ready for next sample...")
            
            print(f"✅ Completed {samples_per_phrase} samples for '{spoken_phrase}'\n")

    def collect_tool_delivery_commands(self, samples_per_command=5):
        commands = {
            "give_me_bolt": "Give me the bolt",
            "give_me_hammer": "Give me the hammer",
            "give_me_measuring_tape": "Give me the measuring tape",
            "give_me_plier": "Give me the plier",
            "give_me_screwdriver": "Give me the screwdriver",
            "give_me_wrench": "Give me the wrench"
        }
        
        print("=== COLLECTING TOOL DELIVERY COMMANDS ===")
        for folder_name, spoken_command in commands.items():
            print(f"\n📁 Now recording: '{spoken_command}'")
            input("Press Enter to start recording this command category...")
            
            for i in range(samples_per_command):
                print(f"\n🎤 Sample {i+1}/{samples_per_command}")
                self.record_high_quality_sample('tool_delivery', folder_name, folder_name, i+1)
                
                if i < samples_per_command - 1:
                    print("    ⏸️  Ready for next sample...")
            
            print(f"✅ Completed {samples_per_command} samples for '{spoken_command}'\n")

    # [Add other collection methods...]

    def show_dataset_stats(self):
        """Show statistics about collected dataset"""
        print("\n=== DATASET STATISTICS ===")
        total_samples = 0
        
        for root, dirs, files in os.walk(self.data_dir):
            if files:
                path_parts = root.split('/')
                if len(path_parts) >= 2:
                    category = path_parts[-2]
                    phrase = path_parts[-1]
                    print(f"📁 {category}/{phrase}: {len(files)} samples")
                    total_samples += len(files)
        
        print(f"\n📊 TOTAL SAMPLES: {total_samples}")
    
    def close(self):
        """Clean up audio resources"""
        self.audio.terminate()


# ENHANCED MAIN VOICE SYSTEM WITH PROCEDURES
class GuidoVoiceSystem:
    def __init__(self):
        # [Previous initialization code...]
        self.manual_procedures = self.create_procedure_library()
    
    def create_procedure_library(self):
        """Create the procedure library for car maintenance"""
        procedures = {
            "tire_change": {
                "title": "How to Change a Car Tire",
                "steps": [
                    "Step 1: Find a safe, flat location and turn on hazard lights",
                    "Step 2: Apply parking brake and place wheel wedges",
                    "Step 3: Remove hubcap and loosen lug nuts",
                    "Step 4: Jack up the vehicle about 6 inches",
                    "Step 5: Remove lug nuts and take off flat tire",
                    "Step 6: Mount spare tire and hand-tighten lug nuts",
                    "Step 7: Lower vehicle and tighten lug nuts in star pattern",
                    "Step 8: Replace hubcap and check tire pressure",
                    "Step 9: Stow all equipment and have spare tire repaired"
                ],
                "tools_needed": ["jack", "lug wrench", "wheel wedges", "spare tire"]
            },
            "oil_change": {
                "title": "How to Change Engine Oil",
                "steps": [
                    "Step 1: Run engine for 5 minutes to warm oil, then turn off",
                    "Step 2: Locate oil drain plug and oil filter",
                    "Step 3: Place drain pan under drain plug",
                    "Step 4: Remove drain plug and drain old oil completely",
                    "Step 5: Replace drain plug and washer",
                    "Step 6: Remove old oil filter and lubricate new filter gasket",
                    "Step 7: Install new oil filter hand-tight",
                    "Step 8: Add new engine oil through fill hole",
                    "Step 9: Check oil level with dipstick",
                    "Step 10: Run engine and check for leaks",
                    "Step 11: Properly dispose of old oil and filter"
                ],
                "tools_needed": ["oil drain pan", "wrench set", "new oil filter", "funnel", "new engine oil"]
            }
        }
        return procedures
    
    def provide_guidance(self, command):
        """Provide specific maintenance procedure guidance"""
        self.last_activity_time = time.time()
        
        # Tire change procedures
        if any(word in command for word in ['tire', 'tyre', 'wheel', 'flat']):
            self.speak("I'll guide you through changing a car tire.")
            procedure = self.manual_procedures["tire_change"]
            self.speak(f"Procedure: {procedure['title']}")
            self.speak(f"You will need: {', '.join(procedure['tools_needed'])}")
            
            for step in procedure['steps']:
                print(f"   {step}")
                self.speak(step)
                time.sleep(1)  # Pause between steps
        
        # Engine oil change procedures
        elif any(word in command for word in ['oil', 'engine oil', 'lubricant']):
            self.speak("I'll guide you through changing engine oil.")
            procedure = self.manual_procedures["oil_change"]
            self.speak(f"Procedure: {procedure['title']}")
            self.speak(f"You will need: {', '.join(procedure['tools_needed'])}")
            
            for step in procedure['steps']:
                print(f"   {step}")
                self.speak(step)
                time.sleep(1)  # Pause between steps
        
        # General help
        elif any(word in command for word in ['guide', 'help', 'manual']):
            self.speak("I can help you with two main procedures:")
            self.speak("1. Changing a car tire")
            self.speak("2. Changing engine oil")
            self.speak("Which procedure would you like me to explain?")
        
        else:
            self.speak("I can help with tire changes or engine oil changes. Please specify which procedure you need.")


# Enhanced main execution
if __name__ == "__main__":
    # Install required package first
    print("🔧 Installing required packages for noise reduction...")
    try:
        import noisereduce
    except ImportError:
        print("Please install noisereduce first:")
        print("pip install noisereduce")
        exit(1)
    
    collector = VoiceDataCollector()
    
    print("🎯 GUIDO ENHANCED VOICE DATASET COLLECTOR")
    print("✨ Now with CAR MAINTENANCE PROCEDURES! ✨")
    print("=" * 60)
    print("Available Procedures:")
    print("• Tire Change Guide")
    print("• Engine Oil Change Guide")
    print("=" * 60)
    
    # Setup optimal recording environment
    collector.setup_recording_environment()
    
    print("\nChoose what to record:")
    print("1. Activation Phrases (Wake up commands)")
    print("2. Tool Delivery Commands (Give me tools)") 
    print("3. Manual Reading Commands (Tire/Oil change guides)")
    print("4. Rearrangement Commands (Organize tools)")
    print("5. System Commands (Deactivate, time, etc.)")
    print("6. COLLECT ALL (Recommended)")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        collector.collect_activation_phrases(8)
    elif choice == '2':
        collector.collect_tool_delivery_commands(5)
    elif choice == '3':
        collector.collect_manual_reading_commands(4)
    elif choice == '4':
        # Add rearrangement method
        pass
    elif choice == '5':
        # Add system method
        pass
    elif choice == '6':
        print("\n=== COLLECTING COMPLETE DATASET ===")
        collector.collect_activation_phrases(8)
        collector.collect_tool_delivery_commands(5)
        collector.collect_manual_reading_commands(4)
        # Add other methods
    else:
        collector.collect_activation_phrases(5)
    
    collector.show_dataset_stats()
    collector.close()
    
    print("\n🎉 DATASET COLLECTION COMPLETE!")
    print("Your robot can now guide through tire changes and oil changes!")