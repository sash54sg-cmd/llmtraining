"""
Conversational AI for nutrition and wellness guidance.
This module can be used to fine-tune an LLM for personalized health coaching.
"""
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import logging
from typing import Dict, List, Optional
from pathlib import Path
from src.config.config import BASE_DIR, LLM_MODEL_NAME

logger = logging.getLogger(__name__)


class ConversationalAI:
    """Conversational AI for wellness guidance."""
    
    def __init__(self, model_name: str = LLM_MODEL_NAME, use_finetuned: bool = True):
        """
        Initialize conversational AI.
        
        Args:
            model_name: HuggingFace model name for conversation
            use_finetuned: Whether to try using fine-tuned LoRA model
        """
        self.model_name = model_name
        self.use_finetuned = use_finetuned
        self.finetuned_path = BASE_DIR / "data" / "models" / "conversational_ai_finetuned"
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self):
        """Load the conversational model, with fine-tuned LoRA if available."""
        try:
            logger.info(f"Loading conversational model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Try to load fine-tuned LoRA adapters
            if self.use_finetuned and self.finetuned_path.exists():
                try:
                    from peft import PeftModel
                    logger.info(f"Loading fine-tuned LoRA adapters from {self.finetuned_path}")
                    self.model = PeftModel.from_pretrained(
                        self.model,
                        str(self.finetuned_path / "adapter_model")
                    )
                    logger.info("Fine-tuned model loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load fine-tuned model: {e}. Using base model.")
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Conversational model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading conversational model: {e}")
            raise
    
    def generate_response(self, user_message: str, context: Dict = None, image_analysis: Optional[Dict] = None, transcription: Optional[str] = None) -> str:
        """
        Generate AI response to user message.
        
        Args:
            user_message: User's message
            context: Additional context (user profile, recent logs, etc.)
            
        Returns:
            AI-generated response
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Build context-aware prompt (include multimodal summaries)
            prompt = self._build_prompt(user_message, context, image_analysis, transcription)
            
            # Generate response
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.6,
                    top_p=0.85,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new response (remove prompt)
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(user_message)
    
    def _build_prompt(self, user_message: str, context: Dict = None, image_analysis: Optional[Dict] = None, transcription: Optional[str] = None) -> str:
        """Build context-aware prompt."""
        prompt_parts = [
            "System: You are a helpful nutrition and wellness AI assistant. Provide empathetic, evidence-based advice.",
        ]
        
        if context:
            if context.get('user_goal'):
                prompt_parts.append(f"User goal: {context['user_goal']}")
            if context.get('dietary_type'):
                prompt_parts.append(f"Dietary preference: {context['dietary_type']}")

        # Include image analysis summary if available
        if image_analysis:
            try:
                preds = image_analysis.get('predictions', [])
                if preds:
                    top = preds[0]
                    confidence = top.get('confidence_percent', 0)
                    if confidence > 10:
                        prompt_parts.append(f"Image detected: {top.get('food_name')} ({confidence:.1f}% confidence)")
                portion = image_analysis.get('portion_estimate')
                if portion:
                    prompt_parts.append(f"Portion estimate: {portion.get('portion_size')}")
            except Exception:
                pass

        # Include transcription if present
        if transcription:
            prompt_parts.append(f"Transcribed audio: {transcription}")
        
        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("Assistant: ")
        
        return "\n".join(prompt_parts)
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Get rule-based fallback response."""
        message_lower = user_message.lower()
        
        # Nutrition questions
        if any(word in message_lower for word in ['calorie', 'calories', 'eat', 'food', 'meal']):
            return ("I can help you track your nutrition! Try logging your meals with photos or manual entry, "
                   "and I'll provide personalized recommendations based on your goals.")
        
        # Cravings
        if any(word in message_lower for word in ['craving', 'hungry', 'want to eat']):
            return ("Cravings are normal! Try drinking water first, as sometimes thirst feels like hunger. "
                   "If you're still hungry, choose a protein-rich snack to keep you satisfied longer.")
        
        # Mood/wellness
        if any(word in message_lower for word in ['stress', 'anxious', 'tired', 'mood', 'feel']):
            return ("Your mental wellness is important! I recommend trying some breathing exercises, "
                   "a short walk, or meditation. Would you like specific activity suggestions?")
        
        # Exercise
        if any(word in message_lower for word in ['exercise', 'workout', 'activity', 'fitness']):
            return ("Regular physical activity is great for both physical and mental health! "
                   "I can suggest workouts based on your fitness level and goals. What type of exercise interests you?")
        
        # Default
        return ("I'm here to help with your nutrition and wellness journey! "
               "You can ask me about meal planning, exercise, managing stress, or tracking your progress.")


# Global AI instance
_conversational_ai = None

def get_conversational_ai() -> ConversationalAI:
    """Get or create the global conversational AI instance."""
    global _conversational_ai
    if _conversational_ai is None:
        _conversational_ai = ConversationalAI()
    return _conversational_ai


# Training function for fine-tuning (optional - for future use)
def train_wellness_model(dataset_path: str, output_dir: str):
    """
    Fine-tune LLM on wellness conversation dataset.
    This is for future enhancement when you have training data.
    
    Args:
        dataset_path: Path to training dataset (JSONL format)
        output_dir: Directory to save fine-tuned model
    """
    from datasets import load_dataset
    from transformers import TrainingArguments
    from peft import LoraConfig
    from trl import SFTTrainer
    
    MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    # Load model + tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_4bit=True,
        device_map="auto"
    )
    
    # Load dataset
    dataset = load_dataset("json", data_files=dataset_path)
    
    # LoRA config
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Training setup
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        tokenizer=tokenizer,
        args=TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            num_train_epochs=3,
            logging_steps=10,
            save_strategy="epoch",
            fp16=True,
            optim="paged_adamw_8bit"
        ),
        peft_config=lora_config
    )
    
    trainer.train()
    logger.info(f"Model training complete. Saved to {output_dir}")
