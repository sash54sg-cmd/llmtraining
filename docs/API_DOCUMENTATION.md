"""
API Documentation for AI-Powered Nutrition & Wellness Tracking System
"""

# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require authentication using JWT Bearer tokens.

### Headers
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login
**POST** `/api/auth/login`

Login with username and password.

**Request Body:** (Form Data)
```
username: johndoe
password: securepassword123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## User Profile Endpoints

### Get Profile
**GET** `/api/users/profile`

Get current user's profile.

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "age": 30,
  "gender": "male",
  "height_cm": 175,
  "weight_kg": 75,
  "goal_type": "weight_loss",
  "activity_level": "moderate",
  "dietary_type": "omnivore",
  "allergies": ["peanuts"],
  "bmr": 1650.5,
  "tdee": 2557.5,
  "target_calories": 2057,
  "target_protein_g": 180,
  "target_carbs_g": 180,
  "target_fat_g": 68
}
```

### Update Profile
**PUT** `/api/users/profile`

Update user profile and recalculate health metrics.

**Request Body:**
```json
{
  "age": 30,
  "gender": "male",
  "height_cm": 175,
  "weight_kg": 75,
  "goal_type": "weight_loss",
  "activity_level": "moderate",
  "dietary_type": "omnivore",
  "allergies": ["peanuts"],
  "food_preferences": {},
  "cuisines": ["italian", "indian"]
}
```

**Response:** `200 OK` (Same as Get Profile)

### Get Health Metrics
**GET** `/api/users/health-metrics`

Get calculated health metrics.

**Response:** `200 OK`
```json
{
  "bmr": 1650.5,
  "tdee": 2557.5,
  "bmi": 24.5,
  "bmi_category": "normal",
  "target_calories": 2057,
  "target_macros": {
    "protein_g": 180,
    "carbs_g": 180,
    "fat_g": 68
  }
}
```

---

## Food & Nutrition Endpoints

### Analyze Food Image
**POST** `/api/food/analyze`

Upload and analyze a food image.

**Request:** Multipart Form Data
```
file: <image_file>
```

**Response:** `200 OK`
```json
{
  "predictions": [
    {
      "food_name": "Pizza",
      "confidence": 0.95,
      "confidence_percent": 95.0
    }
  ],
  "nutrition": {
    "calories": 399,
    "protein": 16.5,
    "carbs": 49.5,
    "fat": 15,
    "source": "local_database"
  },
  "portion_estimate": {
    "portion_size": "medium",
    "portion_multiplier": 1.0,
    "confidence": 0.6
  }
}
```

### Log Food from Image
**POST** `/api/food/log-from-image`

Analyze image and automatically log food.

**Request:** Multipart Form Data
```
file: <image_file>
meal_type: dinner
notes: Homemade pizza
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "food_name": "Pizza",
  "meal_type": "dinner",
  "portion_size": "medium",
  "calories": 399,
  "protein_g": 16.5,
  "carbs_g": 49.5,
  "fat_g": 15,
  "image_path": "/path/to/image.jpg",
  "detection_confidence": 0.95,
  "is_manual_entry": false,
  "logged_at": "2026-01-21T10:30:00",
  "notes": "Homemade pizza"
}
```

### Manual Food Entry
**POST** `/api/food/manual`

Manually log food entry.

**Request Body:**
```json
{
  "food_name": "Grilled Chicken",
  "meal_type": "lunch",
  "portion_size": "medium",
  "calories": 165,
  "protein_g": 31,
  "carbs_g": 0,
  "fat_g": 3.6,
  "notes": "Grilled chicken breast"
}
```

**Response:** `201 Created` (Same structure as Log from Image)

### Search Food
**GET** `/api/food/search?query=chicken`

Search for food in nutrition database.

**Response:** `200 OK`
```json
{
  "food_name": "chicken",
  "nutrition": {
    "calories": 165,
    "protein": 31,
    "carbs": 0,
    "fat": 3.6,
    "source": "local_database"
  }
}
```

### Get Food History
**GET** `/api/food/history?days=7`

Get food log history.

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 7)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "food_name": "Pizza",
    "meal_type": "dinner",
    "calories": 399,
    "logged_at": "2026-01-21T10:30:00"
  }
]
```

---

## Activity & Wellness Endpoints

### Log Workout
**POST** `/api/activity/workout`

Log a workout or exercise activity.

**Request Body:**
```json
{
  "activity_type": "cardio",
  "activity_name": "Running",
  "duration_minutes": 30,
  "intensity": "moderate",
  "notes": "Morning run"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "activity_type": "cardio",
  "activity_name": "Running",
  "duration_minutes": 30,
  "intensity": "moderate",
  "calories_burned": 315.0,
  "logged_at": "2026-01-21T07:00:00",
  "notes": "Morning run"
}
```

### Log Mood
**POST** `/api/activity/mood`

Log mood and emotional state.

**Request Body:**
```json
{
  "mood_state": "happy",
  "mood_score": 8,
  "energy_level": 7,
  "stress_level": 3,
  "triggers": ["good_sleep", "exercise"],
  "activities_done": ["meditation"],
  "notes": "Feeling great today"
}
```

**Response:** `201 Created`

### Get Dashboard
**GET** `/api/activity/dashboard`

Get comprehensive dashboard data.

**Response:** `200 OK`
```json
{
  "date": "2026-01-21T10:30:00",
  "nutrition": {
    "calories": 1500,
    "protein_g": 120,
    "carbs_g": 150,
    "fat_g": 50,
    "target_calories": 2057,
    "remaining_calories": 557
  },
  "activity": {
    "exercise_minutes": 30,
    "calories_burned": 315,
    "activities_count": 1
  },
  "wellness": {
    "avg_mood": 8.0,
    "avg_energy": 7.0,
    "avg_stress": 3.0,
    "mood_logs_count": 1
  },
  "goals_met": {
    "calorie_goal_met": true,
    "protein_goal_met": true,
    "exercise_goal_met": true
  }
}
```

### Get AI Insights
**GET** `/api/activity/insights`

Get AI-generated insights and recommendations.

**Response:** `200 OK`
```json
{
  "insights": {
    "nutrition": {
      "avg_daily_calories": 1850,
      "target_calories": 2057,
      "status": "on_track",
      "message": "Perfect! You're hitting your calorie target consistently."
    },
    "activity": {
      "total_minutes": 180,
      "weekly_goal": 150,
      "status": "excellent",
      "message": "Excellent! You've completed 180 minutes of exercise this week."
    },
    "wellness": {
      "avg_mood_score": 7.5,
      "status": "good",
      "message": "Your mood has been great! Keep up the good habits."
    }
  },
  "meal_recommendations": [...],
  "activity_recommendations": [...]
}
```

---

## AI Chat Endpoints

### Send Message
**POST** `/api/chat/message`

Send message to AI assistant.

**Request Body:**
```json
{
  "message": "I'm feeling stressed, what should I do?"
}
```

**Response:** `200 OK`
```json
{
  "response": "Your mental wellness is important! I recommend trying some breathing exercises, a short walk, or meditation. Would you like specific activity suggestions?",
  "context": {
    "user_goal": "weight_loss",
    "dietary_type": "omnivore"
  }
}
```

### Get Recommendations
**GET** `/api/chat/recommendations`

Get personalized recommendations.

**Response:** `200 OK`
```json
{
  "meal_recommendations": [...],
  "activity_recommendations": [...],
  "insights": {...}
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
