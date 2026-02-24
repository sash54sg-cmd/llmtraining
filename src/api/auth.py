"""
Authentication and security utilities.
MODIFIED: Authentication bypassed for single-user mode.
"""
from fastapi import Header, Depends
from sqlalchemy.orm import Session, joinedload
from src.config.database import get_db
from src.models.user_models import User, UserProfile
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (kept for compatibility)."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta=None) -> str:
    """Dummy function for compatibility."""
    return "dummy-token"

async def get_current_user(
    x_user_email: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current user based on mobile app headers.
    
    Args:
        x_user_email: Email provided by the mobile app (trusted header)
        db: Database session
        
    Returns:
        The verified user object
    """
    email_to_use = x_user_email if x_user_email else "guest@example.com"
    username_to_use = email_to_use.split('@')[0]
    
    try:
        # Try to find user by email
        user = db.query(User).options(joinedload(User.profile)).filter(User.email == email_to_use).first()
        
        if not user:
            print(f"Creating new user for {email_to_use}...")
            # Create new user
            user = User(
                email=email_to_use,
                username=username_to_use,
                hashed_password=get_password_hash("mobile-app-user"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"Created user {user.id}")
            
            # Create default profile data
            initial_profile = {
                "user_id": user.id,
                "age": 30,
                "gender": "male",
                "height_cm": 170,
                "weight_kg": 70,
                "goal_type": "maintenance",
                "activity_level": "moderate",
                "dietary_type": "omnivore"
            }
            
            # Calculate health metrics
            from src.services.health_calculator import HealthCalculator
            calc = HealthCalculator()
            
            # Calculate metrics
            bmr = calc.calculate_bmr(70, 170, 30, "male")
            tdee = calc.calculate_tdee(bmr, "moderate")
            target = calc.calculate_target_calories(tdee, "maintenance")
            macros = calc.calculate_macro_targets(target, "maintenance")
            bmi = calc.calculate_bmi(70, 170)
            
            profile = UserProfile(
                **initial_profile,
                bmr=bmr,
                tdee=tdee,
                target_calories=target,
                target_protein_g=macros['protein_g'],
                target_carbs_g=macros['carbs_g'],
                target_fat_g=macros['fat_g'],
                allergies=[],
                food_preferences={},
                cuisines=[]
            )
            db.add(profile)
            db.commit()
            print("Created default profile")
            
            return user
            
        return user
    except Exception as e:
        print(f"Auth Error: {e}")
        raise e

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the default user."""
    return current_user
