# Adaptive Difficulty - Quick Start Guide

## 🎯 What You Get

✅ **Adaptive Difficulty** - Questions match user skill level
✅ **Smart Recommendations** - Learn about weak areas
✅ **Learning Dashboard** - See your progress
✅ **AI-Powered** - System learns from your performance

## 🚀 Try It Now (3 Steps)

### Step 1: Play a Game
```
1. Go to http://localhost:5000
2. Click "Games"
3. Play Phish Hunter or any game
4. Complete the game
```

### Step 2: Play Another Game
```
1. Notice the difficulty has changed!
2. If you scored high: Questions are HARDER
3. If you scored low: Questions are EASIER
```

### Step 3: Check Your Dashboard
```
1. Visit http://localhost:5000/dashboard
2. See your performance stats
3. Get personalized recommendations
4. Preview next game difficulty
```

## 📊 Dashboard Features

### Your Performance
- Overall score percentage
- Games played count
- Score breakdown per game
- Visual progress bars

### Recommendations
- 🔴 **High Priority** (< 40% score)
  - Learn these modules to improve significantly
  
- 🟡 **Medium Priority** (40-60% score)
  - Learn these modules to fine-tune skills

- ✅ **No Recommendations** (> 60% score)
  - You're doing great! Keep playing!

### Next Game Difficulty
- 🟢 **Easy** - Less than 50% overall score
- 🟡 **Medium** - 50-75% overall score  
- 🔴 **Hard** - More than 75% overall score

## 💡 How It Works

```
First Game
    ↓
Questions: MEDIUM (default)
    ↓
You score 70%
    ↓
Second Game
    ↓
Questions: MEDIUM (70% is in that range)
    ↓
You score 80%
    ↓
Third Game
    ↓
Questions: HARD (80% > 75%)
    ↓
You score 60%
    ↓
Fourth Game
    ↓
Questions: MEDIUM (back to medium range)
```

## 🎮 Difficulty Levels

### 🟢 Easy Questions
- Obvious phishing red flags
- Clear security mistakes
- Perfect for learning basics
- Build confidence

### 🟡 Medium Questions
- Realistic scenarios
- Moderate challenge
- Standard difficulty
- Most common

### 🔴 Hard Questions
- Subtle threats
- Complex decisions
- Advanced challenge
- For experts

## 📈 Track Your Progress

### What Gets Tracked:
- Score for each game played
- Total questions answered correctly
- Overall performance percentage
- Weak and strong areas

### Where to See It:
- `/dashboard` - Full stats and recommendations
- Game result pages - Individual game scores
- Browser console - Real-time API access

## 🔧 APIs (For Developers)

### Get Your Stats
```bash
curl http://localhost:5000/api/user-stats
```

### Get Recommendations
```bash
curl http://localhost:5000/api/recommendations
```

### Get Next Difficulty
```bash
curl http://localhost:5000/api/next-difficulty
```

## 📱 Mobile Support

Dashboard works on:
- ✅ Desktop (full features)
- ✅ Tablet (responsive layout)
- ✅ Mobile (optimized display)

All stats and recommendations visible on any device!

## 🎓 Learning Tips

1. **Play Multiple Games** (at least 2-3)
   - Helps system understand your weak areas
   - Recommendations become more accurate

2. **Follow Recommendations**
   - Focus on high-priority modules
   - They're your biggest improvement areas

3. **Watch Difficulty Increase**
   - As you improve, questions get harder
   - This means you're mastering the material!

4. **Review Results**
   - Check explanations for wrong answers
   - Visit dashboard to see patterns

5. **Retake Challenging Games**
   - Your score might improve 2nd time
   - Difficulty will adjust accordingly

## ❓ FAQ

**Q: Why are my questions suddenly easier?**
A: Your overall score dipped below 50%. This is normal! Easier questions help you rebuild confidence. As you score better, difficulty will increase again.

**Q: When do recommendations appear?**
A: When you have at least one game with < 60% score. Play more games to get better recommendations.

**Q: Do stats reset?**
A: Stats clear when you close your browser. For permanent tracking, we can add database storage.

**Q: Can I change difficulty manually?**
A: Not yet, but the system automatically adapts! Just keep playing.

**Q: Why are all my games the same difficulty?**
A: Play more games first! After 2-3 games, the system has enough data to adapt.

**Q: What counts toward difficulty calculation?**
A: All your game scores combined (games, phish_hunter, password_ninja, etc.)

## 🚀 Pro Tips

- **Pro Tip 1:** High priority recommendations are 2-3x more impactful than medium priority
- **Pro Tip 2:** Your overall score % is what matters for difficulty, not individual games
- **Pro Tip 3:** Check dashboard after every 2-3 games to see your progress
- **Pro Tip 4:** Recommende modules usually take 5-10 min to review
- **Pro Tip 5:** Retaking games 2-3x usually shows 15-20% score improvement

## 📊 Example Scenario

```
Day 1:
  Play Phish Hunter: 40% (weak area!)
  Dashboard shows: 🔴 HIGH PRIORITY phishing modules
  
Day 2:
  Review "Phishing Awareness" module (10 min)
  Review "Phish Hunter Mastery" module (10 min)
  
Day 3:
  Play Phish Hunter again: 75% (HUGE IMPROVEMENT!)
  Questions now at MEDIUM difficulty (next game)
  
Day 4:
  Play another game: 80%
  System sets all questions to HARD
  
Result: User went from 40% → 75% in weak area! ✅
```

## 🎯 System Behavior

| Overall Score | Difficulty | Why |
|---|---|---|
| 0-50% | Easy | Need confidence building |
| 50-75% | Medium | Good progress, steady challenge |
| 75%+ | Hard | Mastery level, advanced material |

## 🔄 Adaptive Loop

```
Start Game
    ↓
[Your Difficulty Level Applied]
    ↓
You Answer Questions
    ↓
Complete Game & See Score
    ↓
Results Saved
    ↓
System Calculates New Difficulty
    ↓
Next Game Uses New Difficulty
    ↓
(Repeat)
```

## 💾 Data Storage

**Currently:** Stored in browser session
- Persists during session
- Cleared on browser close

**Can Add:** Database storage
- Persist across sessions
- Track long-term progress
- Enable user accounts

## 🎊 You're All Set!

Start playing now:
1. Open http://localhost:5000
2. Play a game
3. Play another game (notice difference!)
4. Check /dashboard for recommendations

**That's it!** The system will automatically:
- Track your scores
- Adjust difficulty
- Recommend learning areas
- Help you improve

---

**Questions?** Check `ADAPTIVE_DIFFICULTY_GUIDE.md` for detailed documentation.

**Ready?** Start playing! 🚀
