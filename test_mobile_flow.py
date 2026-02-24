"""
Test script for Mobile App Auth Flow.
Simulating "Beliving" app requests.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_mobile_auth():
    print("Testing Mobile Auth Integration...")
    
    # 1. Default Guest (No Header)
    print("\n1. Testing Default Guest (No Header)...")
    r = requests.get(f"{BASE_URL}/api/users/profile")
    if r.status_code == 200:
        print("✓ Guest Access Success")
        # Verify it is guest
        # We can't see the email effectively in the profile response unless we query DB or check logs
        # But we know ID 1 is guest.
        print(f"  User ID: {r.json().get('user_id')}")
    else:
        print(f"✗ Guest Access Failed: {r.text}")

    # 2. Mobile User 1 (Bob)
    print("\n2. Testing Mobile User Bob (X-User-Email: bob@beliving.app)...")
    headers = {"X-User-Email": "bob@beliving.app"}
    r = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
    if r.status_code == 200:
        print("✓ Bob Access Success")
        bob_id = r.json().get('user_id')
        print(f"  User ID: {bob_id}")
    else:
        print(f"✗ Bob Access Failed: {r.text}")

    # 3. Mobile User 2 (Alice)
    print("\n3. Testing Mobile User Alice (X-User-Email: alice@beliving.app)...")
    headers = {"X-User-Email": "alice@beliving.app"}
    r = requests.get(f"{BASE_URL}/api/users/profile", headers=headers)
    if r.status_code == 200:
        print("✓ Alice Access Success")
        alice_id = r.json().get('user_id')
        print(f"  User ID: {alice_id}")
        
        if alice_id != bob_id:
            print("✓ Validated: Alice and Bob are different users")
        else:
            print("✗ Error: Alice and Bob have same ID!")
    else:
        print(f"✗ Alice Access Failed: {r.text}")

if __name__ == "__main__":
    test_mobile_auth()
