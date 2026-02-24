# Quick Start Guide

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

3. **Run the server**:
   ```bash
   python run_server.py
   ```

4. **Access the API**:
   - API Docs: http://127.0.0.1:8000/api/docs
   - Health Check: http://127.0.0.1:8000/api/health

## First Steps

### 1. Register a User
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 2. Update Your Profile
```bash
curl -X PUT "http://127.0.0.1:8000/api/users/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "goal_type": "weight_loss",
    "activity_level": "moderate",
    "dietary_type": "omnivore"
  }'
```

### 3. Log Some Food
```bash
curl -X POST "http://127.0.0.1:8000/api/food/manual" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "food_name": "Grilled Chicken",
    "meal_type": "lunch",
    "portion_size": "medium",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6
  }'
```

### 4. View Your Dashboard
```bash
curl -X GET "http://127.0.0.1:8000/api/activity/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Features to Try

- **Food Image Analysis**: Upload a food photo at `/api/food/analyze`
- **AI Chat**: Ask wellness questions at `/api/chat/message`
- **Mood Tracking**: Log your mood at `/api/activity/mood`
- **Get Recommendations**: Get personalized suggestions at `/api/chat/recommendations`

## Troubleshooting

### Port Already in Use
Change the port in `.env`:
```
API_PORT=8001
```

### Database Issues
Delete the database and restart:
```bash
rm data/user_data/nutrition_wellness.db
python run_server.py
```

### Model Download Issues
The Food-101 model will download automatically on first use. Ensure you have internet connection.

## Next Steps

- Read the full [API Documentation](docs/API_DOCUMENTATION.md)
- Check out the [README](README.md) for detailed features
- Explore the interactive API docs at http://127.0.0.1:8000/api/docs
