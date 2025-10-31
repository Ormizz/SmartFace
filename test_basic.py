from smartface.stt import SpeechToText
from smartface.tts import TextToSpeech
import time

def test_tts():
    """Test Text-to-Speech"""
    print("\n" + "="*50)
    print("Testing Text-to-Speech")
    print("="*50)
    
    tts = TextToSpeech()
    tts.speak("Hello! I am SmartFace. Testing text to speech.")
    

def test_stt():
    """Test Speech-to-Text"""
    print("\n" + "="*50)
    print("Testing Speech-to-Text")
    print("="*50)
    
    stt = SpeechToText()
    
    try:
        text = stt.listen()
        print(f"Final result: \"{text}\"")
    finally:
        stt.close()


def test_both():
    """Test STT + TTS together - ONE interaction"""
    print("\n" + "="*50)
    print("Testing STT + TTS Together (Single Exchange)")
    print("="*50)
    
    stt = SpeechToText()
    tts = TextToSpeech()
    
    try:
        tts.speak("Hello! Say something and I will repeat it.")
        time.sleep(1)  # Wait for TTS to finish
        
        text = stt.listen()
        
        if text:
            response = f"You said: {text}"
            print(f"\n🤖 {response}")
            time.sleep(0.5)
            tts.speak(response)
            time.sleep(1)  # Wait for TTS to finish before closing
        else:
            tts.speak("I didn't hear anything. Please try again.")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        time.sleep(1)  # Give time for audio to finish
        stt.close()
        print("\n✅ Test completed!")


def test_conversation():
    """Test multiple exchanges - CONTINUOUS"""
    print("\n" + "="*50)
    print("Testing Conversation Loop (Continuous)")
    print("="*50)
    print("\n💡 Say 'exit', 'quit', or 'goodbye' to stop\n")
    
    stt = SpeechToText()
    tts = TextToSpeech()
    
    try:
        # Welcome message
        welcome = "Hello! I'm SmartFace. I'm ready for conversation. Say exit to quit."
        print(f"🤖 {welcome}")
        tts.speak(welcome)
        time.sleep(1)
        
        exchange_count = 0
        
        # Conversation loop
        while True:
            exchange_count += 1
            print(f"\n--- Exchange {exchange_count} ---")
            
            # Listen
            text = stt.listen()
            
            # Handle empty input
            if not text:
                response = "I didn't catch that. Please try again."
                print(f"🤖 {response}")
                tts.speak(response)
                time.sleep(0.5)
                continue
            
            # Check for exit commands
            if text.lower() in ['exit', 'quit', 'stop', 'goodbye', 'bye']:
                farewell = "Goodbye! Have a great day!"
                print(f"🤖 {farewell}")
                tts.speak(farewell)
                time.sleep(1)
                break
            
            # Echo back what user said
            response = f"You said: {text}"
            print(f"🤖 {response}")
            tts.speak(response)
            
            # Small pause between exchanges
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
        tts.speak("Goodbye!")
        time.sleep(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        stt.close()
        print("\n✅ Conversation ended!")


if __name__ == "__main__":
    # Choose test
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "tts":
            test_tts()
        elif test_name == "stt":
            test_stt()
        elif test_name == "both":
            test_both()
        elif test_name == "conversation":
            test_conversation()
        else:
            print("Usage: python test_basic.py [tts|stt|both|conversation]")
    else:
        # Default: run conversation mode
        print("💡 Running conversation mode by default")
        print("   Use 'python test_basic.py both' for single exchange")
        print()
        test_conversation()