# Model Fine-Tuning Guide

This document describes the setup, training, and evaluation of the fine-tuned conversational AI model for wellness guidance.

## Overview

The project now includes a fine-tuning pipeline that improves the conversational AI model's responses to wellness and nutrition queries using domain-specific training data.

### What Was Done

1. **Created Training Data Generator** (`src/training/create_training_data.py`)
   - Generates synthetic wellness conversation examples (20+ QA pairs)
   - Creates JSONL format training data
   - Covers topics: nutrition, fitness, meal prep, cravings, weight loss, stress, mood, etc.

2. **Implemented Fine-Tuning Pipeline** (`src/training/fine_tune_model.py`)
   - Uses LoRA (Low-Rank Adaptation) for efficient fine-tuning
   - Fine-tunes on `microsoft/DialoGPT-medium` model
   - Requires only 1.7M trainable parameters vs. 356M total (0.5% trainable)
   - Runs on CPU but optimized for GPU if available
   - Saves adapted weights to `data/models/conversational_ai_finetuned/`

3. **Updated ConversationalAI** (`src/ai/conversational_ai.py`)
   - Auto-loads fine-tuned LoRA adapters if available
   - Falls back to base model gracefully
   - Improved prompt engineering with better structure and context inclusion
   - Better response generation parameters (lower temperature, better repetition penalty)

4. **Added Evaluation Script** (`src/training/evaluate_model.py`)
   - Tests model on representative wellness queries
   - Compares responses with user context (goals, dietary preferences, etc.)

## Running Fine-Tuning

### Generate Training Data
```bash
python src/training/create_training_data.py
```

Creates `data/train.jsonl` with 20 wellness conversation examples.

### Fine-Tune the Model
```bash
python src/training/fine_tune_model.py
```

**Process:**
- Loads `microsoft/DialoGPT-medium` model
- Applies LoRA adapters (1.7M trainable params)
- Tokenizes training data to max 512 tokens
- Trains for 3 epochs with batch size 4
- Learning rate: 2e-4 with warmup
- Saves to `data/models/conversational_ai_finetuned/`

**Time:** ~8-10 minutes on CPU, ~2-3 minutes on GPU

### Evaluate Model
```bash
python src/training/evaluate_model.py
```

Tests the fine-tuned model on 5 representative wellness queries.

## Architecture

### LoRA Fine-Tuning Benefits
- **Memory Efficient:** Only train 0.5% of model parameters
- **Fast:** ~10x faster than full fine-tuning
- **Space Efficient:** Adapter weights are ~100MB (vs 1GB+ for full model)
- **Portable:** Adapters can be easily shared and loaded

### Model Load Priority
When `ConversationalAI` is initialized:
1. Loads base model (`microsoft/DialoGPT-medium`)
2. Looks for LoRA adapters in `data/models/conversational_ai_finetuned/adapter_model`
3. If found, merges adapters into model
4. If not found or error, uses base model as fallback

## Integration with API

The fine-tuned model is automatically used in the `/api/chat/multimodal` endpoint when:
- `use_finetuned=True` (default)
- Adapter weights exist in `data/models/conversational_ai_finetuned/`

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -F "message=What's a good high-protein breakfast?"
```

Response will use the fine-tuned model for improved wellness-domain responses.

## Extending Training Data

To improve model further, add more examples to `data/train.jsonl`:

```jsonl
{"text": "User: How do I stay consistent with my fitness goals?\nAssistant: Consistency comes from building habits. Start small with realistic goals—maybe 15 minutes of activity daily. Track your progress, celebrate wins, and adjust as needed. Having an accountability partner helps too."}
```

Then re-run:
```bash
python src/training/fine_tune_model.py
```

## Performance Metrics

- **Training Time:** ~8 minutes (CPU), ~2 minutes (GPU)
- **Model Size:** Base model 356M params, trainable adapters 1.7M (0.5%)
- **Training Data:** 20 examples (can extend to hundreds)
- **Domain:** Wellness, nutrition, fitness, mental health

## Troubleshooting

### Model Not Loading LoRA Adapters
- Check that `data/models/conversational_ai_finetuned/adapter_model` directory exists
- Verify fine-tuning completed successfully (check `logs/fine_tune.log`)
- Model falls back to base model automatically

### CUDA/GPU Not Available
- Fine-tuning works on CPU (slower but functional)
- For GPU acceleration, ensure `torch` is installed with CUDA support
- Set `CUDA_VISIBLE_DEVICES` if multiple GPUs available

### Out of Memory
- Reduce `batch_size` in `fine_tune_model.py` (default: 4)
- Reduce `max_length` during tokenization (default: 512)
- Use gradient accumulation for larger effective batch sizes

## Future Improvements

1. **More Training Data:** Collect real conversation logs to expand training set
2. **Domain-Specific Models:** Fine-tune on food recognition models too
3. **Evaluation Metrics:** Add BLEU/ROUGE scoring for response quality
4. **A/B Testing:** Compare base vs. fine-tuned responses in production
5. **Continuous Learning:** Update model with successful conversational logs

## References

- LoRA Paper: https://arxiv.org/abs/2106.09685
- HuggingFace PEFT: https://github.com/huggingface/peft
- DialoGPT: https://arxiv.org/abs/1911.00536
