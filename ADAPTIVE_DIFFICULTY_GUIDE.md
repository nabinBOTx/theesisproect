# Adaptive Difficulty & Personalized Recommendations

## Overview

Your CyberSecure Quest platform now has intelligent AI/ML features that:

1. **Adaptive Difficulty** - Automatically adjusts game difficulty based on user performance
2. **Personalized Recommendations** - Suggests learning modules for weak areas

## Features

### 🎯 Adaptive Difficulty

**How It Works:**
- Each question has a difficulty level: easy, medium, or hard
- System tracks user performance across all games
- Next game automatically adjusts difficulty based on overall score:
  - **< 50% score** → Easy questions (build confidence)
  - **50-75% score** → Medium questions (steady progress)
  - **> 75% score** → Hard questions (advanced challenge)

**User Benefits:**
✅ Personalized learning pace
✅ No frustration from too-hard content
✅ Proper progression path
✅ Maintains engagement

### 📊 Personalized Recommendations

**How It Works:**
- Analyzes which game types user struggles with (< 60% score)
- Recommends specific learning modules for weak areas
- Prioritizes high-impact improvements (< 40% = high priority)
- Suggests contextually relevant materials

**Example:**
```
User scored 40% on Phish Hunter
↓
System identifies phishing as weak area
↓
Recommends:
  - 🔴 HIGH PRIORITY: "Phishing Awareness" module
  - 🔴 HIGH PRIORITY: "Phish Hunter Mastery" module
```

## Implementation Details

### Database/Tracking

**User Stats Tracked:**
```python
{
    "total_games_played": 5,
    "game_scores": {
        "phish_hunter": {"score": 6, "total": 8, "percentage": 75},
        "password_ninja": {"score": 4, "total": 8, "percentage": 50},
        ...
    },
    "overall_score": 50,
    "overall_total": 80,
    "weak_categories": ["phishing", "passwords"],
    "strong_categories": ["mfa", "device_security"]
}
```

### Question Difficulty Levels

All questions now have difficulty ratings:

```python
Question(
    prompt="...",
    choices=[...],
    correct_index=0,
    explanation="...",
    category="Phishing",
    difficulty="easy"  # easy | medium | hard
)
```

**Distribution:**
- Easy: Basic concept questions, obvious threats
- Medium: Standard scenarios, moderate decision-making
- Hard: Subtle phishing, complex scenarios, advanced concepts

### API Endpoints

#### GET /api/user-stats
Returns user performance statistics

**Response:**
```json
{
    "total_games_played": 3,
    "game_scores": {
        "phish_hunter": {
            "score": 6,
            "total": 8,
            "percentage": 75
        }
    },
    "overall_score": 18,
    "overall_total": 24,
    "weak_categories": [],
    "strong_categories": ["phishing"]
}
```

#### GET /api/recommendations
Returns personalized learning recommendations

**Response:**
```json
{
    "recommendations": [
        {
            "game": "password_ninja",
            "score": 45,
            "message": "You scored 45% on password_ninja. Try these learning modules to improve!",
            "modules": [
                "Password Security",
                "Password Ninja Skills"
            ],
            "priority": "high"
        }
    ]
}
```

#### GET /api/next-difficulty
Returns recommended difficulty for next game

**Response:**
```json
{
    "difficulty": "medium",
    "overall_score": 18,
    "overall_total": 24,
    "percentage": 75
}
```

### New Routes

#### GET /dashboard
Displays user learning dashboard with:
- Performance statistics
- Game scores with progress bars
- Personalized recommendations
- Difficulty indicator
- Quick action buttons

## Frontend Components

### JavaScript: adaptive.js

**UserStats Class:**
```javascript
const userStats = new UserStats();
await userStats.loadStats();
userStats.displayStats();
await userStats.loadRecommendations();
userStats.displayRecommendations();
userStats.displayDifficultyIndicator();
```

**Features:**
- Loads stats from API
- Renders stats visualization
- Displays recommendations
- Shows difficulty indicator

### CSS: adaptive.css

**Styles:**
- Stats panel with gradient background
- Game score bars with color coding
- Recommendation cards with priority indicators
- Responsive design for mobile
- Dark/light mode support

## Game Flow with Adaptive Difficulty

```
User plays game
    ↓
User completes game
    ↓
Results saved to session
    ↓
Next time user starts game:
    ↓
Stats calculated from session
    ↓
Difficulty determined
    ↓
Questions filtered by difficulty
    ↓
Mixed with other levels if needed
    ↓
Game starts with appropriate difficulty
```

## User Experience

### First Time Playing
- User plays their first game
- Questions are **medium** difficulty (default)
- After completing:
  - System calculates score
  - Displays results

### After Playing Multiple Games
1. User visits Dashboard (/dashboard)
   - See stats visualization
   - See personalized recommendations
   - See next game difficulty preview

2. User starts next game
   - Game adjusts difficulty based on performance
   - Questions are more challenging if they did well
   - Questions are easier if they need help

3. User follows recommendations
   - Clicks suggested learning modules
   - Studies relevant content
   - Comes back to play again
   - Performance improves

## Configuration & Customization

### Adjust Difficulty Thresholds

In `app.py`, modify `_get_difficulty_level()`:

```python
def _get_difficulty_level(user_score_percentage: float) -> str:
    if user_score_percentage < 50:       # < 50% = easy
        return "easy"
    elif user_score_percentage < 75:     # < 75% = medium
        return "medium"
    else:                                  # > 75% = hard
        return "hard"
```

### Adjust Recommendation Threshold

In `app.py`, modify `_get_recommendations()`:

```python
weak_threshold = 60  # Change this value (default 60%)
```

### Add Difficulty to New Questions

```python
Question(
    prompt="Your question here",
    choices=[...],
    correct_index=0,
    explanation="...",
    category="...",
    difficulty="medium"  # Always include this!
)
```

## Data Persistence

**Note:** Stats are stored in Flask session
- Persists for current user session
- Clears when browser session ends
- For production, consider:
  - Database storage
  - User authentication
  - Long-term tracking

## Analytics & Insights

**Track Over Time:**
- User progression (easy → medium → hard)
- Most challenging game types
- Learning module effectiveness
- Recommended vs. actual performance

**Example Query:**
```python
# Calculate average score improvement
initial_scores = session_history[0]
final_scores = session_history[-1]
improvement = final_scores.overall - initial_scores.overall
```

## Best Practices

✅ **Do:**
- Ensure all questions have difficulty levels
- Regularly review recommendation accuracy
- Monitor user progression
- Keep difficulty progression smooth

❌ **Don't:**
- Skip difficulty levels (e.g., easy → hard directly)
- Make hard questions impossibly hard
- Give bad recommendations
- Force recommendations on users

## Testing

### Manual Testing

1. **Test Adaptive Difficulty:**
   ```
   - Play first game (should be medium)
   - Score 90% (should get hard next)
   - Score 20% (should get easy next)
   ```

2. **Test Recommendations:**
   ```
   - Play Phish Hunter and score 30%
   - Check /dashboard
   - Should recommend Phishing modules
   ```

3. **Test Stats API:**
   ```
   - GET /api/user-stats
   - Should return current game scores
   - Verify calculations are correct
   ```

## API Examples

### Python
```python
import requests

# Get user stats
response = requests.get('http://localhost:5000/api/user-stats')
stats = response.json()
print(f"Overall Score: {stats['overall_score']}/{stats['overall_total']}")

# Get recommendations
response = requests.get('http://localhost:5000/api/recommendations')
recs = response.json()
for rec in recs['recommendations']:
    print(f"{rec['game']}: {rec['message']}")
```

### JavaScript
```javascript
// In browser console
const userStats = new UserStats();
await userStats.loadStats();
console.log(userStats.stats);

await userStats.loadRecommendations();
console.log(userStats.recommendations);

userStats.displayDifficultyIndicator();
```

### cURL
```bash
# Get stats
curl http://localhost:5000/api/user-stats

# Get recommendations
curl http://localhost:5000/api/recommendations

# Get next difficulty
curl http://localhost:5000/api/next-difficulty
```

## Future Enhancements

🚀 **Possible Improvements:**
1. **Predictive Analytics** - ML model to predict user mastery
2. **Database Storage** - Persist stats across sessions
3. **Learning Paths** - Structured courses with prerequisites
4. **Spaced Repetition** - Remind users of weak areas after time
5. **Adaptive Hints** - Give hints based on difficulty level
6. **Performance Timeline** - Chart progress over time
7. **Peer Comparison** - Benchmark against average users
8. **Smart Scheduling** - Suggest best time to practice weak areas

## Troubleshooting

**Issue:** Stats not updating after game
- **Solution:** Make sure game saves results to session

**Issue:** Recommendations not appearing
- **Solution:** Play games until you have < 60% score in an area

**Issue:** Always getting same difficulty
- **Solution:** Try playing multiple games to change score percentage

**Issue:** Dashboard page not loading
- **Solution:** Check browser console (F12) for errors

---

## Files Reference

| File | Purpose |
|------|---------|
| `static/adaptive.js` | UI logic for stats/recommendations |
| `static/adaptive.css` | Styling for stats display |
| `templates/recommendations.html` | Dashboard template |
| `app.py` (functions) | `_get_user_stats()`, `_get_recommendations()`, `_new_adaptive_game_state()` |
| `app.py` (routes) | `/dashboard`, `/api/user-stats`, `/api/recommendations`, `/api/next-difficulty` |

---

**Status:** ✅ Fully Implemented
**Tested:** ✅ Syntax verified, APIs functional
**Ready to Use:** ✅ Start playing games and check your dashboard!
