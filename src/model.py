def get_user_preferences():
    """
    Collects 4-5 user inputs related to food preferences, allergies, and dietary needs.
    """
    print("Please provide your food preferences and restrictions:")
    
    # Input 1: Dietary type
    dietary_type = input("Are you vegetarian, vegan, or neither? (Enter: vegetarian/vegan/neither): ").strip().lower()
    
    # Input 2: Allergies
    allergies = input("List any food allergies (e.g., nuts, dairy, gluten) separated by commas: ").strip().lower()
    allergies_list = [allergy.strip() for allergy in allergies.split(',')] if allergies else []
    
    # Input 3: Favorite cuisines
    cuisines = input("What are your favorite cuisines? (e.g., Italian, Indian, Mexican) separated by commas: ").strip().lower()
    cuisines_list = [cuisine.strip() for cuisine in cuisines.split(',')] if cuisines else []
    
    # Input 4: Calorie goal or needs
    calorie_goal = input("What is your daily calorie goal? (Enter a number or 'none'): ").strip()
    calorie_goal = int(calorie_goal) if calorie_goal.isdigit() else None
    
    # Input 5: Additional needs (e.g., health conditions)
    additional_needs = input("Any additional needs or restrictions? (e.g., low-sodium, diabetic-friendly): ").strip().lower()
    
    return {
        "dietary_type": dietary_type,
        "allergies": allergies_list,
        "cuisines": cuisines_list,
        "calorie_goal": calorie_goal,
        "additional_needs": additional_needs
    }

# Example usage
if __name__ == "__main__":
    preferences = get_user_preferences()
    print("Collected preferences:", preferences)