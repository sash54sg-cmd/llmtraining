# AI-Powered Nutrition & Wellness Tracking System

A comprehensive health and wellness platform that combines computer vision, AI-powered recommendations, and personalized health tracking to help users manage their nutrition, fitness, and mental well-being.

## 🌟 Features

### 🍽️ Food Recognition & Nutrition Tracking
- **AI-Powered Food Detection**: Upload food photos and get instant identification using pre-trained Food-101 model
- **Automatic Nutrition Calculation**: Get calories, macros, and micronutrients for detected foods
- **Manual Food Entry**: Fallback option with comprehensive nutrition database
- **Portion Size Estimation**: Smart estimation of serving sizes from images
- **Meal History Tracking**: Complete log of all meals with timestamps

### 👤 User Health Profiles
- **Personalized Profiles**: Age, weight, height, activity level, and health goals
- **Dietary Preferences**: Support for vegetarian, vegan, keto, and other diets
- **Allergy Tracking**: Manage food allergies and restrictions
- **Health Metrics**: Automatic BMR, TDEE, and BMI calculations
- **Macro Targets**: Personalized protein, carbs, and fat goals

### 🏃 Activity & Wellness Tracking
- **Workout Logging**: Track cardio, strength, yoga, and other activities
- **Calorie Burn Calculation**: Accurate estimates based on activity type and intensity
- **Mood Tracking**: Log emotional states, energy levels, and stress
- **Daily Summaries**: Comprehensive dashboards with progress visualization
- **Historical Trends**: Track progress over days, weeks, and months

### 🤖 AI-Powered Recommendations
- **Conversational AI**: Chat with an AI wellness assistant
- **Personalized Meal Suggestions**: Based on goals, preferences, and remaining calories
- **Workout Recommendations**: Tailored to fitness level and activity history
- **Mood-Regulating Activities**: Suggestions for yoga, meditation, breathing exercises
- **Behavioral Insights**: Pattern analysis and progress tracking

### 📱 Mobile Integration
- **Trusted Authentication**: Accepts `X-User-Email` header from the "Beliving" mobile app to automatically provision and identify users.
- **Dynamic AI**: Configurable LLM model selection via environment variables.

### 🔒 Security & Privacy
- **Mobile App Trust**: Relies on upstream authentication from the mobile app (trusted network/header).
- **Data Privacy**: Secure storage of sensitive health information (local database).
- **User Isolation**: Data stored under unique profiles based on email identity.


## 🏗️ Architecture

```
llm-training-project/
├── src/
│   ├── api/                    # FastAPI REST API
│   │   ├── routes/            # API endpoints
│   │   ├── main.py            # FastAPI app
│   │   ├── auth.py            # Authentication
│   │   └── schemas.py         # Pydantic models
│   ├── models/                # Database models
│   │   ├── user_models.py     # User, profile, logs
│   │   └── tracking_models.py # Activity plans, summaries
│   ├── services/              # Business logic
│   │   ├── nutrition_calculator.py
│   │   ├── health_calculator.py
│   │   └── image_handler.py
│   ├── ai/                    # AI/ML components
│   │   ├── food_recognition.py
│   │   ├── conversational_ai.py
│   │   └── recommendation_engine.py
│   ├── config/                # Configuration
│   │   ├── config.py
│   │   └── database.py
│   └── utils/                 # Utilities
├── data/
│   ├── nutrition_db/          # Nutrition databases
│   ├── user_data/             # User uploads & database
│   └── models/                # ML model cache
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster AI inference

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-training-project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**:
   The database will be automatically created when you first run the API.

5. **Run the API server**:
   ```bash
   python src/api/main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Access the API documentation**:
   - Swagger UI: http://127.0.0.1:8000/api/docs
   - ReDoc: http://127.0.0.1:8000/api/redoc

## ⚙️ Configuration

Create a `.env` file in the root directory (see `.env.example`):

```env
# Database
DATABASE_URL=sqlite:///./data/user_data/nutrition_wellness.db

# AI Configuration
LLM_MODEL_NAME=microsoft/DialoGPT-medium  # Change to any HuggingFace model

# API
API_HOST=127.0.0.1
API_PORT=8000
```

## 📚 API Endpoints

### Authentication (Legacy/Mock)
- `POST /api/auth/register` - Mock registration (returns dummy token)
- `POST /api/auth/login` - Mock login (returns dummy token)
- **Note**: Use `X-User-Email` header for real user identity in mobile app integration.


### User Profile
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/health-metrics` - Get calculated health metrics

### Food & Nutrition
- `POST /api/food/analyze` - Analyze food image
- `POST /api/food/log-from-image` - Analyze and log food
- `POST /api/food/manual` - Manually log food
- `GET /api/food/search` - Search food database
- `GET /api/food/history` - Get food log history
- `DELETE /api/food/{log_id}` - Delete food log

### Activity & Wellness
- `POST /api/activity/workout` - Log workout
- `POST /api/activity/mood` - Log mood
- `GET /api/activity/dashboard` - Get dashboard data
- `GET /api/activity/insights` - Get AI insights
- `GET /api/activity/mood-activities` - Get mood-based activities
- `GET /api/activity/history/activities` - Get activity history
- `GET /api/activity/history/mood` - Get mood history

### AI Chat
- `POST /api/chat/message` - Send message to AI
- `GET /api/chat/recommendations` - Get personalized recommendations
- `GET /api/chat/activities` - Get activity suggestions

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=sqlite:///./data/user_data/nutrition_wellness.db

# API
API_HOST=127.0.0.1
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here

# USDA API (Optional)
USDA_API_KEY=your-api-key
```

### USDA FoodData Central API (Optional)
For enhanced nutrition data, get a free API key:
1. Visit https://fdc.nal.usda.gov/api-key-signup.html
2. Sign up for a free API key
3. Add it to your `.env` file

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test specific modules:
```bash
pytest tests/test_food_recognition.py -v
pytest tests/test_api.py -v
```

## 📖 Usage Examples

### Register and Login
```python
import requests

# Register
response = requests.post("http://localhost:8000/api/auth/register", json={
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword"
})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### Upload and Analyze Food Image
```python
# Upload food image
with open("food_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/food/analyze",
        files=files,
        headers=headers
    )
    
print(response.json())
# Output: {
#   "predictions": [...],
#   "nutrition": {...},
#   "portion_estimate": {...}
# }
```

### Get Dashboard Data
```python
response = requests.get(
    "http://localhost:8000/api/activity/dashboard",
    headers=headers
)
dashboard = response.json()
print(f"Calories today: {dashboard['nutrition']['calories']}")
```

### Multimodal Chat (Text, Image, Audio)

You can interact with the AI assistant using text, or upload an image or audio file to include in the prompt.

- Text-only example:
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
   -F "message=What should I eat for dinner?"
```

- Image upload example (multipart form):
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
   -F "message=Does this look healthy?" \
   -F "file=@/path/to/food.jpg;type=image/jpeg"
```

- Audio upload example (requires `ffmpeg` and `openai-whisper` if using transcription):
```bash
curl -X POST "http://127.0.0.1:8000/api/chat/multimodal" \
   -F "file=@/path/to/voice_note.wav;type=audio/wav"
```

Notes:
- If using Whisper-based transcription, ensure `ffmpeg` is installed on your system.
- The endpoint returns a JSON object with `response`, optional `image_analysis`, and `transcription` fields.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Food-101 Dataset**: Pre-trained food recognition model
- **USDA FoodData Central**: Comprehensive nutrition database
- **FastAPI**: Modern web framework for building APIs
- **Transformers**: State-of-the-art NLP models

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for health and wellness**