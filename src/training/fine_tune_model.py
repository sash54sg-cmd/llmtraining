"""
Fine-tune the conversational AI model on wellness/nutrition domain data.
Uses LoRA for efficient fine-tuning and saves the adapted model.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType

logger = logging.getLogger(__name__)

class ConversationalAITrainer:
    """Trainer for fine-tuning the conversational AI model on wellness data."""
    
    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-medium",
        output_dir: str = "data/models/conversational_ai_finetuned",
        lora_rank: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
    ):
        """Initialize the trainer."""
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Using device: {self.device}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def load_training_data(self, data_file: str) -> Dataset:
        """Load JSONL training data and convert to HF Dataset."""
        data = []
        with open(data_file, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        
        # Create Dataset
        dataset = Dataset.from_dict({
            "text": [item["text"] for item in data]
        })
        
        logger.info(f"Loaded {len(dataset)} training examples")
        return dataset
    
    def load_models(self):
        """Load tokenizer and model."""
        logger.info(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Ensure pad token is set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        logger.info("Models loaded successfully")
    
    def apply_lora(self):
        """Apply LoRA adapters to the model."""
        lora_config = LoraConfig(
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            target_modules=["c_attn", "mlp.c_proj"],
            lora_dropout=self.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        logger.info("LoRA adapters applied")
    
    def preprocess_function(self, examples):
        """Tokenize training examples."""
        return self.tokenizer(
            examples["text"],
            max_length=512,
            truncation=True,
            padding="max_length",
        )
    
    def train(
        self,
        data_file: str = "data/train.jsonl",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        save_steps: int = 50,
    ):
        """Fine-tune the model."""
        # Load data
        dataset = self.load_training_data(data_file)
        
        # Load models
        self.load_models()
        
        # Apply LoRA
        self.apply_lora()
        
        # Tokenize data
        tokenized_dataset = dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=["text"],
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=save_steps,
            save_total_limit=2,
            logging_steps=10,
            learning_rate=learning_rate,
            weight_decay=0.01,
            warmup_steps=50,
            fp16=torch.cuda.is_available(),
            seed=42,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting fine-tuning...")
        trainer.train()
        
        # Save
        self.model.save_pretrained(str(self.output_dir / "adapter_model"))
        self.tokenizer.save_pretrained(str(self.output_dir / "tokenizer"))
        
        logger.info(f"Fine-tuning complete. Model saved to {self.output_dir}")
        
        return trainer

def main():
    """Run fine-tuning."""
    logging.basicConfig(level=logging.INFO)
    
    trainer = ConversationalAITrainer()
    trainer.train(
        data_file="data/train.jsonl",
        num_epochs=3,
        batch_size=4,
        learning_rate=2e-4,
    )

if __name__ == "__main__":
    main()
