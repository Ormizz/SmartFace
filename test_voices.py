from smartface.tts import TextToSpeech

def test_all_voices():
    """Test all available voices"""
    tts = TextToSpeech()
    
    # List all voices
    voices = tts.list_voices()
    
    # Test each voice
    test_phrase = "Hello, this is a test of the voice assistant."
    
    for i, voice in enumerate(voices):
        print(f"\n{'='*60}")
        print(f"Testing voice {i}: {voice.name}")
        print('='*60)
        
        tts.set_voice(i)
        tts.speak(test_phrase)
        
        response = input("\nDo you like this voice? (y/n/q to quit): ").lower()
        if response == 'q':
            break
        elif response == 'y':
            print(f"\n✅ Selected voice: {voice.name}")
            print(f"   Voice ID: {voice.id}")
            print("\nTo use this voice, initialize TTS with:")
            print(f"   tts = TextToSpeech()")
            print(f"   tts.set_voice({i})")
            break

def test_specific_voices():
    """Test specific recommended voices"""
    tts = TextToSpeech()
    
    recommended = ['Samantha', 'Alex', 'Zoe', 'Daniel']
    test_phrase = "Hello! I am SmartFace, your voice assistant."
    
    print("\n🎤 Testing recommended voices:\n")
    
    for name in recommended:
        if tts.set_voice_by_name(name):
            tts.speak(test_phrase)
            response = input(f"Keep {name}? (y/n): ").lower()
            if response == 'y':
                print(f"✅ Using {name}")
                return
        print()

if __name__ == "__main__":
    # Test specific voices first (faster)
    test_specific_voices()
    
    # Or test all voices
    # test_all_voices()