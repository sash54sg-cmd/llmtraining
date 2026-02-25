"""
Manual testing script for food image recognition and nutrition tracking.
Interactive tool to test uploaded images against the API.
"""
import requests
import json
import os
from pathlib import Path
from typing import Optional
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGES_DIR = Path("data/test_images")
UPLOAD_DIR = Path("data/user_data/uploads/1")

# Test user email (no-auth mode)
TEST_USER_EMAIL = "test@example.com"

# Headers for no-auth mode
DEFAULT_HEADERS = {
    "X-User-Email": TEST_USER_EMAIL
}


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_section(title: str):
    """Print formatted subsection."""
    print(f"\n{title}")
    print("-" * len(title))


def test_api_health():
    """Test if API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ API is healthy and running")
            return True
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API at", BASE_URL)
        print("  Make sure the server is running: python run_server.py")
        return False
    except Exception as e:
        print(f"✗ Error checking API health: {e}")
        return False


def list_available_images() -> list:
    """List available test images."""
    images = []
    
    # Check test_images directory
    if TEST_IMAGES_DIR.exists():
        test_images = list(TEST_IMAGES_DIR.glob("*.[jJ][pP][gG]")) + \
                      list(TEST_IMAGES_DIR.glob("*.[pP][nN][gG]"))
        images.extend(test_images)
    
    # Check upload directory (previously uploaded images)
    if UPLOAD_DIR.exists():
        uploaded = list(UPLOAD_DIR.glob("*.[jJ][pP][gG]")) + \
                   list(UPLOAD_DIR.glob("*.[pP][nN][gG]"))
        images.extend(uploaded)
    
    return list(set(images))  # Remove duplicates


def select_image() -> Optional[Path]:
    """Let user select an image file."""
    images = list_available_images()
    
    if not images:
        print("✗ No test images found!")
        print(f"  Please add images to: {TEST_IMAGES_DIR.absolute()}")
        return None
    
    print_section("Available Images")
    for i, img in enumerate(images, 1):
        size_kb = img.stat().st_size / 1024
        print(f"{i:2}. {img.name:40} ({size_kb:.1f} KB)")
    
    print(f"\n{len(images) + 1}. Enter custom path")
    choice = input("\nSelect image (or 'q' to cancel): ").strip()
    
    if choice.lower() == 'q':
        return None
    
    try:
        choice_idx = int(choice) - 1
        if choice_idx == len(images):
            # Custom path
            custom_path = input("Enter image path: ").strip()
            path = Path(custom_path)
            if path.exists():
                return path
            else:
                print(f"✗ File not found: {custom_path}")
                return None
        elif 0 <= choice_idx < len(images):
            return images[choice_idx]
        else:
            print("✗ Invalid selection")
            return None
    except ValueError:
        print("✗ Invalid input")
        return None


def analyze_image(image_path: Path) -> Optional[dict]:
    """Send image to API for analysis."""
    if not image_path.exists():
        print(f"✗ Image file not found: {image_path}")
        return None
    
    print(f"\nAnalyzing: {image_path.name}")
    print(f"Size: {image_path.stat().st_size / 1024:.1f} KB")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            
            print("  Sending to /food/analyze...")
            response = requests.post(
                f"{BASE_URL}/api/food/analyze",
                files=files,
                headers=DEFAULT_HEADERS,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis successful")
            return result
        else:
            print(f"✗ API error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Request timeout (inference took too long)")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def display_analysis_results(result: dict):
    """Display detailed analysis results."""
    print_section("Food Recognition Results")
    
    if 'predictions' in result:
        predictions = result['predictions']
        print(f"Top {len(predictions)} Predictions:")
        for i, pred in enumerate(predictions, 1):
            confidence = pred.get('confidence', 0) * 100
            print(f"  {i}. {pred['food_name']:30} ({confidence:5.1f}%)")
    
    if 'portion_estimate' in result:
        portion = result['portion_estimate']
        print_section("Portion Estimate")
        print(f"  Estimated portion size: {portion.get('portion_size', 'unknown')}")
        print(f"  Portion multiplier: {portion.get('portion_multiplier', 1):.1f}x")
    
    if 'nutrition' in result:
        nutrition = result['nutrition']
        print_section("Estimated Nutrition (per serving)")
        print(f"  Calories:  {nutrition.get('calories', 0):.0f} kcal")
        print(f"  Protein:   {nutrition.get('protein_g', 0):.1f}g")
        print(f"  Carbs:     {nutrition.get('carbs_g', 0):.1f}g")
        print(f"  Fat:       {nutrition.get('fat_g', 0):.1f}g")
        print(f"  Fiber:     {nutrition.get('fiber_g', 0):.1f}g")


def log_food_to_database(result: dict, image_path: Path) -> bool:
    """Save the analyzed food to database."""
    if 'predictions' not in result or 'nutrition' not in result:
        print("✗ Cannot log: Missing predictions or nutrition data")
        return False
    
    top_prediction = result['predictions'][0]
    nutrition = result['nutrition']
    
    meal_type = input("\nMeal type (breakfast/lunch/dinner/snack): ").strip().lower()
    if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal_type = 'snack'
    
    notes = input("Notes (optional): ").strip()
    
    payload = {
        "food_name": top_prediction['food_name'],
        "meal_type": meal_type,
        "portion_size": result.get('portion_estimate', {}).get('portion_size', 'medium'),
        "calories": nutrition.get('calories', 0),
        "protein_g": nutrition.get('protein_g', 0),
        "carbs_g": nutrition.get('carbs_g', 0),
        "fat_g": nutrition.get('fat_g', 0),
        "fiber_g": nutrition.get('fiber_g', 0),
        "notes": notes,
        "image_path": str(image_path)
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/food/manual",
            json=payload,
            headers=DEFAULT_HEADERS,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Food logged successfully (ID: {result.get('id', 'unknown')})")
            return True
        else:
            print(f"✗ Failed to log food: {response.status_code}")
            print(f"  {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error logging food: {e}")
        return False


def export_test_report(results: list):
    """Export test results to JSON file."""
    if not results:
        print("No results to export")
        return
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_images_tested": len(results),
        "results": results
    }
    
    report_path = Path("test_results.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Test report exported to: {report_path}")


def test_batch_images():
    """Test multiple images in a batch."""
    images = list_available_images()
    
    if not images:
        print("✗ No images found")
        return
    
    print_section("Batch Image Testing")
    print(f"Found {len(images)} images")
    
    results = []
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Testing: {image_path.name}")
        
        result = analyze_image(image_path)
        if result:
            results.append({
                "image": image_path.name,
                "success": True,
                "predictions": result.get('predictions', []),
                "nutrition": result.get('nutrition', {})
            })
        else:
            results.append({
                "image": image_path.name,
                "success": False,
                "error": "Analysis failed"
            })
        
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print_section("Batch Test Summary")
    print(f"Successful: {successful}/{len(results)}")
    
    if input("\nExport results to JSON? (y/n): ").lower() == 'y':
        export_test_report(results)


def interactive_menu():
    """Main interactive menu."""
    while True:
        print_header("Food Recognition Manual Testing")
        print("1. Test single image")
        print("2. Batch test all images")
        print("3. View user profile")
        print("4. View recent food logs")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            image_path = select_image()
            if image_path:
                result = analyze_image(image_path)
                if result:
                    display_analysis_results(result)
                    if input("\nLog to database? (y/n): ").lower() == 'y':
                        log_food_to_database(result, image_path)
        
        elif choice == '2':
            test_batch_images()
        
        elif choice == '3':
            try:
                response = requests.get(
                    f"{BASE_URL}/api/users/profile",
                    headers=DEFAULT_HEADERS,
                    timeout=5
                )
                if response.status_code == 200:
                    profile = response.json()
                    print_section("User Profile")
                    print(json.dumps(profile, indent=2))
                else:
                    print(f"✗ Failed to fetch profile: {response.status_code}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == '4':
            try:
                response = requests.get(
                    f"{BASE_URL}/api/food/logs",
                    headers=DEFAULT_HEADERS,
                    timeout=5
                )
                if response.status_code == 200:
                    logs = response.json()
                    print_section("Recent Food Logs")
                    if logs:
                        for log in logs[:10]:
                            print(f"  {log.get('food_name', 'Unknown'):30} "
                                  f"{log.get('calories', 0):6.0f} kcal "
                                  f"{log.get('meal_type', ''):10}")
                    else:
                        print("  No food logs yet")
                else:
                    print(f"✗ Failed to fetch logs: {response.status_code}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("✗ Invalid option")


def main():
    """Main entry point."""
    print_header("Food Recognition & Nutrition Tracking - Manual Testing")
    
    if not test_api_health():
        return
    
    print("\n✓ API connection successful")
    print(f"✓ Test user: {TEST_USER_EMAIL}")
    
    # Create test directories if needed
    TEST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"✓ Test images directory: {TEST_IMAGES_DIR.absolute()}")
    print(f"✓ Upload directory: {UPLOAD_DIR.absolute()}")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")


if __name__ == "__main__":
    main()
