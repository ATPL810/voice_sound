from guido_voice_system import GuidoVoiceSystem

def quick_test():
    """Quick test of the voice system"""
    guido = GuidoVoiceSystem()
    
    # Test text-to-speech
    print("Testing text-to-speech...")
    guido.speak("Hello! I am Guido. This is a test of my voice system.")
    
    # Test microphone calibration
    print("Testing microphone...")
    guido.calibrate_microphone()
    
    # Test listening
    print("Speak something after the beep...")
    text = guido.listen()
    if text:
        print(f"You said: {text}")
    
    print("Test completed!")

if __name__ == "__main__":
    quick_test()