# Quick Start: Multimodal Health & Wellness API

This guide gets you started with the multimodal AI-powered health & wellness tracking system.

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Training Data (Optional)
If you want to use the fine-tuned model:
```bash
python src/training/create_training_data.py
python src/training/fine_tune_model.py
```
This takes ~8-10 minutes and improves wellness response quality.

### 3. Start the Server
```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit: http://127.0.0.1:8000/api/docs (Swagger UI)

---

## 💬 Multimodal Chat Examples

The API accepts **text, image, or audio** in a single unified endpoint.

### Text-Only Chat
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -H "X-User-Email: user@example.com" \
  -F "message=What's a healthy breakfast with 30g protein?"
```

Response:
```json
{
  "response": "A high-protein breakfast could include...",
  "context": {...},
  "image_analysis": null,
  "transcription": null
}
```

### Upload a Food Photo
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -H "X-User-Email: user@example.com" \
  -F "message=How many calories does this look like?" \
  -F "file=@pizza.jpg;type=image/jpeg"
```

Response includes food predictions:
```json
{
  "response": "This pizza portion looks like...",
  "image_analysis": {
    "predictions": [
      {
        "food_name": "Pizza",
        "confidence": 0.92,
        "confidence_percent": 92.0
      }
    ],
    "portion_estimate": {
      "portion_size": "medium",
      "portion_multiplier": 1.0
    }
  }
}
```

### Upload an Audio Recording
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -H "X-User-Email: user@example.com" \
  -F "file=@voice_note.wav;type=audio/wav"
```

The audio is transcribed and processed:
```json
{
  "response": "Based on your question about...",
  "transcription": "What should I eat after my workout?"
}
```

---

## 📊 API Endpoints

### Chat & AI
- `POST /api/chat/multimodal` — Unified multimodal input (text/image/audio)
- `POST /api/chat/message` — Text-only chat (legacy)
- `GET /api/chat/recommendations` — Personalized wellness recommendations

### User Profile
- `GET /api/users/profile` — Get user health profile
- `PUT /api/users/profile` — Update profile
- `GET /api/users/health-metrics` — Get BMR, TDEE, macro targets

### Food & Nutrition
- `POST /api/food/analyze` — Analyze food image
- `GET /api/food/search` — Search nutrition database
- `GET /api/food/history` — Get meal logs

### Activity & Wellness
- `POST /api/activity/workout` — Log exercise
- `POST /api/activity/mood` — Log mood/stress
- `GET /api/activity/dashboard` — Daily summary

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./data/user_data/nutrition_wellness.db
API_HOST=127.0.0.1
API_PORT=8000
LLM_MODEL_NAME=microsoft/DialoGPT-medium
LOG_LEVEL=INFO
```

### Using Authentication
Pass your email in the request header:
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -H "X-User-Email: john@example.com" \
  -F "message=How should I meal prep for the week?"
```

---

## 🧠 Model Fine-Tuning

The system includes a **fine-tuned conversational AI** that improves response quality for wellness topics.

### Check Fine-Tuned Model Status
```bash
ls data/models/conversational_ai_finetuned/
```

Should show:
- `adapter_model/` — LoRA weight adapters
- `tokenizer/` — Vocabulary files
- `adapter_config.json` — Configuration

### Retrain on New Data

1. Add more examples to `data/train.jsonl`:
```jsonl
{"text": "User: How do I stay motivated to workout?\nAssistant: ..."}
```

2. Run training:
```bash
python src/training/fine_tune_model.py
```

The fine-tuned model is automatically used on next server restart.

---

## 🧪 Testing

### Run Test Suite
```bash
pytest tests/test_multimodal.py -v
```

Expected output:
```
test_multimodal_text_only PASSED
test_multimodal_image_and_audio PASSED
```

---

## 📋 Request/Response Format

### Multimodal Request
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -F "message=Optional text prompt" \
  -F "file=@image_or_audio_file"
```

**Parameters:**
- `message` (optional): Text message or question
- `file` (optional): Image (jpg/png) or Audio (wav/mp3) file

### Multimodal Response
```json
{
  "response": "string - AI generated response",
  "context": {
    "user_goal": "weight_loss|muscle_gain|maintain",
    "dietary_type": "omnivore|vegetarian|vegan",
    "target_calories": 2000
  },
  "image_analysis": {
    "predictions": [
      {
        "food_name": "Pizza",
        "confidence": 0.92,
        "confidence_percent": 92.0
      }
    ],
    "nutrition": {},
    "portion_estimate": {
      "portion_size": "small|medium|large",
      "portion_multiplier": 0.75
    }
  },
  "transcription": "transcribed audio text (if audio provided)"
}
```

---

## ⚡ Performance Tips

### Optimize Image Upload
- Resize to max 1920x1920 px
- Use JPEG compression (quality 85+)
- Max file size: 10MB

### Optimize Audio Upload
- Use WAV or MP3 format
- 16kHz sample rate recommended
- Mono or stereo OK

### Faster Responses
- Use GPU if available (CUDA)
- Base model is faster than fine-tuned (if fine-tuning slows inference)
- Cache frequent responses

---

## 🐛 Troubleshooting

### Audio Transcription Not Working
**Issue:** "whisper package not available"
**Solution:**
```bash
pip install openai-whisper
# Also need ffmpeg: brew install ffmpeg (Mac) or choco install ffmpeg (Windows)
```

### Image Recognition Low Confidence
**Issue:** Food predictions < 10% confidence
**Solution:** 
- Take a clearer, well-lit photo
- Center the food in frame
- Avoid blurry or small images

### Model Slow to Start
**Issue:** First request takes 30+ seconds
**Solution:**
- Pre-warm by making a dummy request on startup
- Use GPU for faster inference
- Cache model in memory

---

## 📚 Documentation

- **API Docs:** http://localhost:8000/api/docs (Swagger)
- **Detailed Guide:** See `docs/MODEL_FINETUNING.md`
- **Full Summary:** See `PROJECT_COMPLETION_SUMMARY.md`

---

## 🎯 Next Steps

1. **Set up your user profile** with health goals
2. **Start logging meals** with food photos
3. **Chat with the AI** about nutrition & wellness
4. **Track mood & activities** for comprehensive insights
5. **Fine-tune the model** for better responses (optional)

---

## 💡 Example Workflow

```bash
# 1. Start server
uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# 2. Ask about breakfast
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -F "message=What should I eat for breakfast tomorrow?"

# 3. Upload a food photo
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -F "message=Is this healthy?" \
  -F "file=@lunch.jpg;type=image/jpeg"

# 4. Voice note
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
  -F "file=@question.wav;type=audio/wav"

# 5. Get recommendations
curl "http://127.0.0.1:8000/api/chat/recommendations"
```

---

**Ready to go! 🚀**
