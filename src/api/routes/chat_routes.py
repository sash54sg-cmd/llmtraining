"""
AI chat and conversational routes.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user_models import User, Conversation
from src.api.schemas import ChatMessage, ChatResponse, MultiModalResponse
from src.api.auth import get_current_active_user
from src.ai.conversational_ai import get_conversational_ai
from src.ai.recommendation_engine import get_recommendation_engine
from src.services.image_handler import get_image_handler
from src.ai.food_recognition import get_food_model
from src.services.audio_handler import get_audio_handler

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send message to AI assistant and get response."""
    # Build context from user profile
    context = {}
    if current_user.profile:
        context = {
            "user_goal": current_user.profile.goal_type,
            "dietary_type": current_user.profile.dietary_type,
            "target_calories": current_user.profile.target_calories
        }
    
    # Get AI response
    ai = get_conversational_ai()
    response = ai.generate_response(message.message, context)
    
    # Save conversation
    conversation = Conversation(
        user_id=current_user.id,
        user_message=message.message,
        ai_response=response,
        context=context
    )
    db.add(conversation)
    db.commit()
    
    return {
        "response": response,
        "context": context
    }


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations."""
    rec_engine = get_recommendation_engine(db)
    
    meal_recs = rec_engine.generate_meal_recommendations(current_user.id)
    activity_recs = rec_engine.generate_activity_recommendations(current_user.id)
    insights = rec_engine.generate_insights(current_user.id)
    
    return {
        "meal_recommendations": meal_recs,
        "activity_recommendations": activity_recs,
        "insights": insights
    }


@router.get("/activities")
async def get_activity_suggestions(
    mood: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mood-based activity suggestions."""
    rec_engine = get_recommendation_engine(db)
    activities = rec_engine.generate_mood_activities(current_user.id, mood)
    
    return {"activities": activities}



@router.post("/multimodal", response_model=MultiModalResponse)
async def multimodal_input(
    message: str = Form(None),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Accept text, image or audio input and return an AI response.

    - If image is provided: run food recognition and include analysis.
    - If audio is provided: transcribe audio to text and include transcription.
    - If only text: behave like regular message.
    """
    # Build user context
    context = {}
    if current_user.profile:
        context = {
            "user_goal": current_user.profile.goal_type,
            "dietary_type": current_user.profile.dietary_type,
            "target_calories": current_user.profile.target_calories
        }

    ai = get_conversational_ai()
    extra = {}

    # Prepare message text based on inputs
    message_text = message or ""

    if file is not None:
        content_type = (file.content_type or "").lower()
        # Image handling
        if content_type.startswith("image/"):
            data = await file.read()
            img_handler = get_image_handler()
            img_path = img_handler.save_uploaded_image(data, file.filename, current_user.id)
            # Run food recognition
            food_model = get_food_model()
            predictions = food_model.predict(img_path)
            portion = food_model.estimate_portion_size(img_path)

            detected = predictions[0]['food_name'] if predictions else 'food item'
            conf = predictions[0].get('confidence_percent', 0) if predictions else 0
            message_text = (message_text + " \n" if message_text else "") + f"I uploaded an image that looks like {detected} ({conf}%)."
            extra['image_analysis'] = {
                'predictions': predictions,
                'nutrition': {},
                'portion_estimate': portion,
                'image_path': img_path
            }

        # Audio handling
        elif content_type.startswith("audio/"):
            data = await file.read()
            audio_handler = get_audio_handler()
            audio_path = audio_handler.save_audio(data, file.filename, current_user.id)
            transcription = audio_handler.transcribe(audio_path)
            message_text = (message_text + " \n" if message_text else "") + f"(Transcribed audio) {transcription}"
            extra['transcription'] = transcription

        else:
            # Unknown file type: include a short note
            message_text = (message_text + " \n" if message_text else "") + f"I attached a file of type {content_type}, which was ignored." 

    # Generate AI response (include multimodal extras)
    response = ai.generate_response(
        message_text,
        context,
        image_analysis=extra.get('image_analysis'),
        transcription=extra.get('transcription')
    )

    # Save conversation
    conversation = Conversation(
        user_id=current_user.id,
        user_message=message_text,
        ai_response=response,
        context=context
    )
    db.add(conversation)
    db.commit()

    result = {
        'response': response,
        'context': context
    }
    result.update(extra)

    return result
