"""
Evaluate the fine-tuned conversational AI model on test queries.
Compare responses before and after fine-tuning.
"""
import logging
from src.ai.conversational_ai import ConversationalAI

logging.basicConfig(level=logging.WARNING)

test_queries = [
    ("What should I eat for breakfast?", {"user_goal": "weight_loss", "dietary_type": "omnivore", "target_calories": 2000}),
    ("I'm feeling tired after my workout.", {"user_goal": "muscle_gain", "dietary_type": "omnivore", "target_calories": 3000}),
    ("How do I stay motivated to exercise?", {"user_goal": "maintain", "dietary_type": "vegetarian", "target_calories": 2500}),
    ("What are good protein sources?", {"user_goal": "muscle_gain", "dietary_type": "omnivore", "target_calories": 3000}),
    ("Can I eat pizza on a diet?", {"user_goal": "weight_loss", "dietary_type": "omnivore", "target_calories": 1800}),
]

def evaluate_model():
    """Evaluate the fine-tuned model on test queries."""
    print("=" * 80)
    print("EVALUATING FINE-TUNED CONVERSATIONAL AI MODEL")
    print("=" * 80)
    
    # Test with fine-tuned model
    ai = ConversationalAI(use_finetuned=True)
    print("\n[Using fine-tuned LoRA model]")
    
    for i, (query, context) in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print(f"   Context: {context.get('user_goal')} | {context.get('dietary_type')}")
        
        response = ai.generate_response(query, context)
        print(f"   Response: {response[:150]}..." if len(response) > 150 else f"   Response: {response}")
        print("-" * 80)

if __name__ == "__main__":
    evaluate_model()
