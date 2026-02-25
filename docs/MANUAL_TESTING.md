# Manual Image Testing Guide

This guide explains how to use the manual testing script to test food recognition and nutrition tracking with real images.

## Quick Start

### 1. Start the API Server

```bash
python run_server.py
```

The server will start on `http://127.0.0.1:8000`

### 2. Run the Manual Testing Script

```bash
python manual_test_images.py
```

### 3. Follow the Interactive Menu

The script provides an interactive menu for:
- Testing single images
- Batch testing all available images
- Viewing user profile
- Viewing recent food logs

## Features

### Single Image Testing

1. Select "Test single image" from the menu
2. Choose an image from available options
3. View AI predictions with confidence scores
4. See estimated portion size
5. Review calculated nutrition info
6. Option to save to database

### Batch Testing

1. Select "Batch test all images"
2. Script automatically tests all images in `data/test_images/`
3. View summary of results
4. Export results to JSON file

### Results Display

Each test shows:
```
Food Recognition Results:
  1. Pizza                                 (95.2%)
  2. Pasta                                 (3.5%)
  3. Bread                                 ( 1.2%)

Portion Estimate:
  Estimated portion size: medium
  Portion multiplier: 1.0x

Estimated Nutrition (per serving):
  Calories:  285 kcal
  Protein:   12.5g
  Carbs:     38.2g
  Fat:       8.3g
  Fiber:     2.1g
```

## Test Image Setup

### Add Test Images

Place food images in: `data/test_images/`

Supported formats:
- JPG / JPEG
- PNG

### Recommended Test Images

For best results, use clear photos of:
- Single dish in focus
- Good lighting
- Reasonable frame (food takes 40-70% of image)
- Common foods

### Sample Test Foods

Try testing these common foods for best recognition:
- Pizza
- Burger
- Salad
- Pasta
- Rice
- Soup
- Sandwich
- Cake
- Fruit
- Vegetables

## Understanding Results

### Confidence Scores

- **90%+**: Very confident prediction
- **70-90%**: Good prediction, likely correct
- **50-70%**: Moderate confidence, may need verification
- **<50%**: Low confidence, manual entry recommended

### Portion Estimates

The portion multiplier affects nutrition calculation:
- `0.5x`: Half the standard serving
- `1.0x`: Standard serving size
- `2.0x`: Double the standard serving

### Nutrition Values

Displayed values are **per serving** (based on portion estimate):
- Calories: Total energy in kcal
- Protein: Grams of protein
- Carbs: Grams of carbohydrates
- Fat: Grams of total fat
- Fiber: Grams of dietary fiber

## Database Logging

When you choose to log a food:

1. **Meal Type**: breakfast, lunch, dinner, or snack
2. **Notes**: Optional observations about the meal
3. Entry is saved with:
   - Timestamp
   - User ID
   - Nutrition values
   - Image reference

View logged meals with: "View recent food logs" option

## Batch Testing & Export

After batch testing, results can be exported to `test_results.json`:

```json
{
  "timestamp": "2026-02-25 10:30:45",
  "total_images_tested": 5,
  "results": [
    {
      "image": "pizza.jpg",
      "success": true,
      "predictions": [
        {"food_name": "Pizza", "confidence": 0.952}
      ],
      "nutrition": {
        "calories": 285,
        "protein_g": 12.5
      }
    }
  ]
}
```

## Troubleshooting

### "Cannot connect to API"

- Make sure server is running: `python run_server.py`
- Check if port 8000 is available
- Verify no firewall blocking

### "No test images found"

- Add images to `data/test_images/` directory
- Or provide custom path when prompted
- Accepted formats: JPG, PNG

### "Analysis failed"

Possible causes:
- Image file corrupted
- Unsupported format
- API timeout (try with smaller image)
- GPU/CUDA issues (will fallback to CPU)

### "File size exceeds maximum"

- Compress the image
- Resize to smaller dimensions
- Max size: Usually 10-20 MB

## Advanced Testing

### Test Specific Image Formats

```bash
# Test with custom image
python manual_test_images.py
# Choose "Enter custom path" option
# Enter: /path/to/your/image.jpg
```

### Analyze API Response

Results are formatted as JSON internally, useful for:
- Integration testing
- Debugging predictions
- Analyzing model confidence
- Tracking inference times

### Performance Metrics

The script tracks:
- Request times
- Model inference latency
- API response times
- Success/failure rates

## API Endpoints Used

The manual testing script exercises these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/food/analyze` | POST | Analyze image |
| `/api/food/manual` | POST | Log food entry |
| `/api/users/profile` | GET | View profile |
| `/api/food/logs` | GET | List food logs |

## Next Steps

1. Test with your own food images
2. Verify nutrition calculations
3. Check database entries
4. Batch test for overall accuracy
5. Review and export results
6. Adjust API parameters if needed

## Questions?

Refer to main documentation:
- [API Documentation](API_DOCUMENTATION.md)
- [Quick Start Guide](QUICK_START.md)
- [Multimodal Quickstart](MULTIMODAL_QUICKSTART.md)
