from smartface.nlp import NLPProcessor
from smartface.response_handler import ResponseHandler


def test_intent_classification():
    """Test intent classification with various inputs"""
    print("\n" + "="*60)
    print("Testing Intent Classification")
    print("="*60)
    
    nlp = NLPProcessor()
    response_handler = ResponseHandler()
    
    # Test phrases
    test_phrases = [
        "hello there",
        "what time is it",
        "tell me a joke",
        "turn on the living room light",
        "what's the weather like",
        "remind me to buy milk",
        "search for python tutorials",
        "goodbye",
        "how are you",
        "thank you",
        "some random gibberish text"
    ]
    
    print("\nTesting various phrases:\n")
    
    for phrase in test_phrases:
        intent, confidence = nlp.classify_intent(phrase)
        entities = nlp.extract_entities(phrase, intent)
        response = response_handler.generate_response(intent, entities, confidence)
        
        print(f"Input: \"{phrase}\"")
        print(f"  → Intent: {intent} (confidence: {confidence:.2f})")
        if entities:
            print(f"  → Entities: {entities}")
        print(f"  → Response: {response}")
        print()


if __name__ == "__main__":
    test_intent_classification()