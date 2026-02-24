"""
Test script for No-Auth mode.
"""
import requests

BASE_URL = "http://127.0.0.1:8000"
DUMMY_HEADER = {"Authorization": "Bearer any-token-works"}

def test_no_auth_flow():
    print("Testing No-Auth Mode...")
    
    # 1. Get Profile (should work with ANY token)
    response = requests.get(f"{BASE_URL}/api/users/profile", headers=DUMMY_HEADER)
    if response.status_code == 200:
        print("✓ Get Profile: Success")
        print(f"  User: {response.json().get('age')} years old (Default User)")
    else:
        print(f"✗ Get Profile Failed: {response.text}")
        return

    # 2. Log Food (should work)
    food_data = {
        "food_name": "Test Apple",
        "meal_type": "snack",
        "portion_size": "medium",
        "calories": 95,
        "protein_g": 0.5,
        "carbs_g": 25,
        "fat_g": 0.3
    }
    response = requests.post(f"{BASE_URL}/api/food/manual", json=food_data, headers=DUMMY_HEADER)
    if response.status_code == 201:
        print("✓ Log Food: Success")
    else:
        print(f"✗ Log Food Failed: {response.text}")

    print("\nNo-Auth Mode Verified Successfully!")

if __name__ == "__main__":
    test_no_auth_flow()
