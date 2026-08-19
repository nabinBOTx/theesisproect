# CyberSecure Quest Chatbot Integration - Summary

## What Was Added

### 1. Backend Changes (app.py)
- Added OpenAI client initialization using `python-dotenv` for environment variable management
- Added two new API routes:
  - `POST /api/chat` - Handles chatbot messages and conversation history
  - `POST /api/chat/reset` - Clears chat history
- Added `CHATBOT_SYSTEM_PROMPT` to define chatbot behavior and capabilities
- Conversation history is limited to last 20 messages for efficient API usage

### 2. Frontend Components
Created three new files in `static/`:

#### chatbot.js
- `ChatbotWidget` class that handles:
  - Creating and managing chatbot UI
  - Sending messages to backend API
  - Maintaining conversation state
  - Handling loading states and errors
  - Resetting conversation history

#### chatbot.css
- Modern, cybersecurity-themed styling
- Floating chat widget in bottom-right corner
- Animated message bubbles
- Responsive design for mobile devices
- Purple gradient matching the platform theme

#### Updated base.html
- Added links to `chatbot.css` and `chatbot.js`
- Chatbot is automatically loaded on all pages

### 3. Configuration Files
- Updated `requirements.txt` with:
  - `openai==1.3.0` - OpenAI Python client
  - `python-dotenv==1.0.0` - Environment variable management
- Created `.env.example` - Template for users to configure API key

### 4. Documentation
- Updated `README.md` with:
  - Chatbot feature description
  - Setup instructions for OpenAI API
  - Chatbot capabilities and customization options
  - Configuration details

## Features

### Chatbot Capabilities
- **Context-Aware Help**: Explains cybersecurity concepts and game scenarios
- **Conversation Memory**: Maintains last 20 message exchanges for context
- **Real-Time Responses**: Uses GPT-3.5-turbo for quick, accurate answers
- **Error Handling**: Gracefully handles API errors and missing credentials
- **Session Management**: Stores conversation history per user session

### UI/UX Features
- **Floating Widget**: Always accessible chat button in bottom-right
- **Smooth Animations**: Slide-in effects and loading indicators
- **Theme Integration**: Matches platform's purple gradient cybersecurity theme
- **Mobile Responsive**: Works on all screen sizes
- **Accessibility**: Clear messaging and proper focus management

## Usage

### For Users
1. Click the 💬 button in bottom-right corner to open chat
2. Type questions about cybersecurity, games, or security practices
3. Click "Reset" (↻) to clear conversation history
4. Click × to close the chat widget

### For Developers
1. Get OpenAI API key from https://platform.openai.com/account/api-keys
2. Create `.env` file from `.env.example`
3. Add API key: `OPENAI_API_KEY=sk-...`
4. Restart Flask app
5. Chat widget automatically works on all pages

## How It Works

1. User types message and clicks Send
2. Frontend sends message to `/api/chat` via AJAX
3. Backend maintains conversation history in session
4. Message + history sent to OpenAI API with system prompt
5. Response returned to frontend and displayed in chat
6. Conversation history updated for next message

## Customization Options

### Change Chatbot Behavior
Edit `CHATBOT_SYSTEM_PROMPT` in `app.py`:
```python
CHATBOT_SYSTEM_PROMPT = """Your custom prompt here..."""
```

### Change Model
Update model name in chat route:
```python
model="gpt-4"  # or other models
```

### Adjust Token Limits
Modify message history length in chat route:
```python
if len(chat_history) > 30:  # Keep last 30 messages instead of 20
```

## Error Handling

- If `OPENAI_API_KEY` not set: Shows user-friendly message
- If API request fails: Shows error and allows retry
- If network error: Gracefully handles and informs user

## Security Notes

- API key should be stored in `.env` (never in code)
- Conversation history stored in Flask session (user-specific)
- Consider implementing rate limiting for production
- Monitor API usage to manage costs
