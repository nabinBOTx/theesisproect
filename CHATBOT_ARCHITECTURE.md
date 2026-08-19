# Chatbot Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CyberSecure Quest Platform                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    User Interface                       │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ All Game Pages (base.html template)             │  │  │
│  │  │  • Phish Hunter                                 │  │  │
│  │  │  • Spot the Scam                                │  │  │
│  │  │  • Device Defender                              │  │  │
│  │  │  • Password Ninja                               │  │  │
│  │  │  • And 4 more games...                          │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌────────────────────────────────────────────┐        │  │
│  │  │ 💬 Floating Chat Widget                    │        │  │
│  │  │ ┌──────────────────────────────────────┐   │        │  │
│  │  │ │ CyberSecure Assistant                │   │        │  │
│  │  │ ├──────────────────────────────────────┤   │        │  │
│  │  │ │ • Hi! How can I help?                │   │        │  │
│  │  │ │ • Explain phishing attacks           │   │        │  │
│  │  │ │ • Tips on password security          │   │        │  │
│  │  │ │                                      │   │        │  │
│  │  │ │ [Type your question here...]         │   │        │  │
│  │  │ │                              [Send]  │   │        │  │
│  │  │ └──────────────────────────────────────┘   │        │  │
│  │  └────────────────────────────────────────────┘        │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           │ JavaScript (chatbot.js)           │
│                           │ CSS (chatbot.css)                 │
│                           ▼                                    │
├─────────────────────────────────────────────────────────────────┤
│                     Flask Backend (app.py)                     │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ POST /api/chat                                         │   │
│  │  • Receives user message                              │   │
│  │  • Retrieves conversation history from session        │   │
│  │  • Calls OpenAI API                                   │   │
│  │  • Returns response                                   │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ POST /api/chat/reset                                   │   │
│  │  • Clears conversation history                         │   │
│  │  • Returns success status                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                           │                                    │
│                           ▼                                    │
├─────────────────────────────────────────────────────────────────┤
│                    External Services                            │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ OpenAI API (GPT-3.5-turbo)                             │   │
│  │                                                         │   │
│  │  Request:                                             │   │
│  │  • System prompt (defines chatbot behavior)           │   │
│  │  • Conversation history (last 20 messages)            │   │
│  │  • Current user message                               │   │
│  │                                                         │   │
│  │  Response:                                            │   │
│  │  • AI-generated answer (up to 500 tokens)             │   │
│  │                                                         │   │
│  │  Cost: ~$0.0005-0.001 per message                    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### User sends message:
```
1. User clicks "Send" → chatbot.js captures message
2. AJAX POST to /api/chat → Backend receives request
3. Backend retrieves session history → Prepares context
4. OpenAI API call → Sends prompt + history
5. Response returned → Backend receives answer
6. Response to frontend → JavaScript displays in chat
7. History updated → Session stores new exchange
```

### User resets chat:
```
1. User clicks "Reset" button
2. POST to /api/chat/reset → Backend clears session
3. chatbot.js clears UI messages
4. New conversation ready
```

## File Structure

```
CyberSecure Quest/
│
├── app.py                          # Main Flask app
│   ├── OpenAI client init
│   ├── CHATBOT_SYSTEM_PROMPT       # Defines bot behavior
│   └── API Routes:
│       ├── POST /api/chat          # Handle messages
│       └── POST /api/chat/reset    # Clear history
│
├── templates/
│   └── base.html                   # Main template
│       ├── Links chatbot.css
│       └── Loads chatbot.js
│
├── static/
│   ├── chatbot.js                  # Chat widget class
│   │   ├── createChatbot()        # Build UI
│   │   ├── sendMessage()          # Send to API
│   │   └── resetChat()            # Clear history
│   │
│   └── chatbot.css                 # Widget styling
│       ├── .chatbot-widget         # Main container
│       ├── .chatbot-header         # Header styling
│       ├── .chatbot-messages       # Message area
│       ├── .chatbot-input-area     # Input section
│       └── Responsive design
│
├── .env.example                    # Config template
├── requirements.txt                # Python dependencies
│   ├── openai==1.3.0
│   └── python-dotenv==1.0.0
│
└── Documentation/
    ├── README.md                   # Updated platform docs
    ├── CHATBOT_SETUP.md            # Setup guide
    ├── CHATBOT_API.md              # API reference
    └── CHATBOT_IMPLEMENTATION.md   # This implementation
```

## Session Management

```
Flask Session (Per User):
│
├── game_state               # Game progress
├── phish_hunter             # Game data
├── choose_2fa               # Game data
├── chat_history             # ← Chatbot history
│   └── [
│       {role: "user", content: "What is MFA?"},
│       {role: "assistant", content: "MFA is..."},
│       {role: "user", content: "Why is it important?"},
│       {role: "assistant", content: "It's important..."}
│       ... (max 20 messages)
│   ]
│
└── ... other session data
```

## Message Flow Example

### User: "What is phishing?"

```
Frontend (Browser)                Backend (Flask)              External (OpenAI)
─────────────────────            ──────────────────            ────────────────

User types message
        │
        ▼
   Show loading
        │
        ├─ POST /api/chat ─────→ Receive message
        │                        │
        │                        ├─ Get session history
        │                        │  chat_history = [
        │                        │    {role: "user", ...},
        │                        │    {role: "assistant", ...}
        │                        │  ]
        │                        │
        │                        ├─ Prepare API call:
        │                        │  {
        │                        │    system: SYSTEM_PROMPT,
        │                        │    messages: [
        │                        │      {role: "system", ...},
        │                        │      {role: "user", ...},
        │                        │      {role: "assistant", ...},
        │                        │      {role: "user", "What is phishing?"}
        │                        │    ]
        │                        │  }
        │                        │
        │                        ├─ Send to OpenAI ──→ Process request
        │                        │                     │
        │                        │                     ├─ Generate response
        │                        │                     │  using GPT-3.5-turbo
        │                        │                     │
        │                        │                     └─ Return answer
        │                        │
        │                        ├─ Save to history:
        │                        │  chat_history.append({
        │                        │    role: "assistant",
        │                        │    content: response
        │                        │  })
        │                        │
        │ ← Response JSON ───────┤
        │  {response: "Phishing is..."}
        │
        ├─ Hide loading
        │
        ├─ Display message
        │
        ├─ Add to chat UI
        │
        └─ Ready for next message
```

## Configuration Files

### .env (Local Only)
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### requirements.txt
```
Flask==3.0.0
openai==1.3.0
python-dotenv==1.0.0
```

### app.py Configuration
```python
# System prompt determines chatbot personality and expertise
CHATBOT_SYSTEM_PROMPT = """You are CyberSecure Quest Assistant..."""

# Model choice: gpt-3.5-turbo (fast & cheap) or gpt-4 (smarter & expensive)
model="gpt-3.5-turbo"

# Max response length
max_tokens=500

# Response variability (0-1)
temperature=0.7

# Conversation history limit
if len(chat_history) > 20:  # Keep last 20 exchanges
```

## Security Architecture

```
Client (Browser)                    Server (Flask)
─────────────────                    ──────────────

                                    .env
                                    │
                                    └─ OPENAI_API_KEY
                                       (never sent to client)
                                       (never hardcoded)

Message sent        ─────────────→ Received
│
└─ No sensitive data

Response received   ←──────────── Generated by OpenAI
│
└─ Safe to display (no secrets)

Session Storage:
┌─────────────────┐
│ User A Session  │
│ chat_history: []│  ← Only accessible to User A
└─────────────────┘

┌─────────────────┐
│ User B Session  │
│ chat_history: []│  ← Only accessible to User B
└─────────────────┘
```

## Error Handling Flow

```
User sends message
    │
    ├─ Network error?
    │   └─ Show: "Connection failed. Retry?"
    │
    ├─ API key missing?
    │   └─ Show: "Chatbot not configured. Please set OPENAI_API_KEY"
    │
    ├─ OpenAI API error?
    │   └─ Show: "Sorry, encountered error. Try again?"
    │
    ├─ Empty message?
    │   └─ Ignore silently
    │
    └─ Success!
        └─ Display response in chat
```

## Performance Metrics

```
Average Message Flow:
├─ Network latency: 100-200ms
├─ OpenAI API processing: 1-5s
├─ Total time: 1-6 seconds
└─ UX: Shows loading indicator during wait

Token Usage Per Message:
├─ Average question: 30 tokens
├─ Average response: 100-150 tokens
├─ Conversation history: 50-200 tokens
├─ System prompt: 50-100 tokens
└─ Total: 200-400 tokens (cost ~$0.0003-0.0006)

Cost Estimate:
├─ 100 messages/day: ~$0.30-0.60/day
├─ 1000 messages/day: ~$3-6/day
├─ 10000 messages/day: ~$30-60/day
└─ OpenAI free credits typically last 1-2 months
```

---

This architecture ensures:
✅ Scalability - Easy to add more games
✅ Security - API key never exposed to client
✅ Performance - Efficient message handling
✅ Usability - Simple, intuitive chat interface
✅ Maintainability - Clean separation of concerns
