# 🚀 Chatbot Quick Reference

## 5-Minute Setup

```bash
# 1. Get API key
# Visit: https://platform.openai.com/signup
# Get free $5 trial credits

# 2. Create .env file
cp .env.example .env
# Edit and add: OPENAI_API_KEY=sk-xxxxx

# 3. Install packages (if needed)
pip install -r requirements.txt

# 4. Run app
python app.py
# Visit: http://127.0.0.1:5000
# Click 💬 button to chat!
```

## Files at a Glance

| File | Purpose | Size |
|------|---------|------|
| `static/chatbot.js` | Chat widget logic | 6.2 KB |
| `static/chatbot.css` | Chat styling | 5.5 KB |
| `app.py` | Backend routes | +100 lines |
| `.env.example` | Config template | 313 B |
| `requirements.txt` | Dependencies | +2 packages |

## Chat Widget

**Location**: Bottom-right corner of every page
**Button**: 💬 (purple gradient)
**Features**:
- ✅ Drag-friendly UI
- ✅ Conversation history
- ✅ Reset button (↻)
- ✅ Close button (×)
- ✅ Mobile responsive

## API Endpoints

### POST /api/chat
Send message and get response

**Request:**
```json
{"message": "What is MFA?"}
```

**Response:**
```json
{"response": "MFA is Multi-Factor Authentication..."}
```

### POST /api/chat/reset
Clear chat history

**Response:**
```json
{"status": "Chat history cleared"}
```

## Sample Questions

```
✅ What is phishing?
✅ How do I spot a scam?
✅ Why is MFA important?
✅ What makes a strong password?
✅ Explain that question to me
✅ What's the safest network?
✅ How do I verify a URL?
✅ What is least privilege?
```

## Configuration

### In app.py:

```python
# Change bot personality
CHATBOT_SYSTEM_PROMPT = """Your prompt..."""

# Use better model (costs more)
model="gpt-4"

# Adjust response length
max_tokens=800

# Keep more history
if len(chat_history) > 30:
```

### In .env:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
FLASK_ENV=development
FLASK_DEBUG=1
```

## Customization in 3 Steps

### 1. Change Bot Behavior
Edit `CHATBOT_SYSTEM_PROMPT` in `app.py`:
```python
CHATBOT_SYSTEM_PROMPT = """You are a funny cybersecurity tutor..."""
```

### 2. Adjust Visual Style
Edit `static/chatbot.css`:
```css
/* Change gradient colors */
background: linear-gradient(135deg, #FF6B6B 0%, #FFA500 100%);

/* Change widget size */
width: 400px;
height: 600px;
```

### 3. Modify Behavior
Edit `static/chatbot.js`:
```javascript
// Auto-expand chat
openChatbot();

// Disable reset button
document.getElementById('chatbot-reset').style.display = 'none';
```

## Troubleshooting

### Chat not showing?
```
1. Refresh page (Ctrl+R)
2. Clear cache (Ctrl+Shift+Del)
3. Check console (F12)
4. Verify chatbot.js is loaded
```

### No response from bot?
```
1. Verify .env has API key
2. Check OpenAI account status
3. Test API key: https://platform.openai.com/account/api-keys
4. Look at Flask console for errors
```

### High costs?
```
1. Reduce history limit (currently 20)
2. Limit response length (max_tokens)
3. Implement caching for common questions
4. Set spending limit in OpenAI dashboard
```

## Cost Calculator

| Messages/Day | Est. Cost/Day | Est. Cost/Month |
|---|---|---|
| 10 | $0.03 | $1 |
| 50 | $0.15 | $5 |
| 100 | $0.30 | $10 |
| 500 | $1.50 | $45 |
| 1000 | $3 | $90 |

*Based on avg. 200-300 tokens per message at ~$0.0005/1K tokens*

## Performance Tips

✅ **Do:**
- Limit chat history (currently 20 msgs)
- Use gpt-3.5-turbo (not gpt-4)
- Cache common questions
- Monitor API usage

❌ **Don't:**
- Store full conversations in database
- Use gpt-4 for every query
- Set max_tokens too high
- Leave debug mode on in production

## Production Checklist

- [ ] Replace SECRET_KEY with random string
- [ ] Set OPENAI_API_KEY in production environment
- [ ] Enable HTTPS
- [ ] Set FLASK_ENV=production
- [ ] Implement rate limiting
- [ ] Monitor API costs
- [ ] Setup error logging
- [ ] Backup conversation logs (optional)

## Emergency Stop

If API costs are too high, disable chatbot:

**Option 1: Remove from HTML**
```html
<!-- Comment out in base.html -->
<!-- <script src="{{ url_for('static', filename='chatbot.js') }}"></script> -->
```

**Option 2: Disable endpoint**
```python
# In app.py
@app.route("/api/chat", methods=["POST"])
def chat():
    return jsonify({"error": "Chatbot disabled"}), 403
```

**Option 3: Remove API key**
```bash
# Delete from .env
# OPENAI_API_KEY=
```

## Useful Links

| Resource | URL |
|----------|-----|
| OpenAI Signup | https://platform.openai.com/signup |
| API Keys | https://platform.openai.com/account/api-keys |
| Documentation | https://platform.openai.com/docs |
| Pricing | https://openai.com/pricing |
| Status | https://status.openai.com |

## Version Info

```
Flask: 3.0.0
OpenAI: 1.3.0+
Python: 3.8+
JS: ES6+
Browser Support: All modern browsers
```

---

**Questions?** See `CHATBOT_SETUP.md` or `CHATBOT_API.md` for detailed guides.

**Need help?** Check console errors (F12) → See Flask terminal output → Review documentation files.

**Ready to test?** Run `python app.py` and click the 💬 button!
