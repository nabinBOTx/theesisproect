# Chatbot API Reference

## Endpoints

### POST /api/chat
Sends a message to the chatbot and receives a response.

**Request:**
```json
{
    "message": "What is phishing?"
}
```

**Response (Success):**
```json
{
    "response": "Phishing is a cyberattack where attackers impersonate legitimate organizations..."
}
```

**Response (Error - API not configured):**
```json
{
    "error": true,
    "response": "Chatbot is not configured. Please set the OPENAI_API_KEY environment variable."
}
```

**Response (API Error):**
```json
{
    "error": "API Error message",
    "response": "Sorry, I encountered an error. Please try again."
}
```

---

### POST /api/chat/reset
Clears the conversation history for the current user session.

**Request:**
```
POST /api/chat/reset
```

**Response:**
```json
{
    "status": "Chat history cleared"
}
```

---

## Usage Examples

### JavaScript/Frontend

```javascript
// Send a message
async function sendChatMessage(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    });
    
    const data = await response.json();
    console.log(data.response);
}

// Reset chat history
async function resetChatHistory() {
    const response = await fetch('/api/chat/reset', {
        method: 'POST'
    });
    
    const data = await response.json();
    console.log(data.status);
}
```

### Python/Backend

```python
import requests

# Send message
response = requests.post(
    'http://127.0.0.1:5000/api/chat',
    json={'message': 'Explain MFA'}
)
print(response.json()['response'])

# Reset chat
response = requests.post('http://127.0.0.1:5000/api/chat/reset')
print(response.json()['status'])
```

### cURL

```bash
# Send message
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a strong password?"}'

# Reset chat
curl -X POST http://127.0.0.1:5000/api/chat/reset
```

---

## Features

### Conversation Context
- Each API call includes full conversation history (last 20 messages)
- Enables context-aware responses
- User-specific sessions maintain separate conversation threads

### Rate Limiting
- Consider implementing rate limiting in production
- Each message consumes OpenAI API tokens (~$0.0005-0.001 per message)

### Customization
- System prompt defines chatbot personality and expertise
- Model can be changed from `gpt-3.5-turbo` to other OpenAI models
- Temperature can be adjusted (currently 0.7) for response variability

### Error Handling
- Graceful fallback if API key not configured
- Descriptive error messages for debugging
- Frontend handles network errors and retries

---

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxx  # Your OpenAI API key
```

### Flask Session Configuration
Conversation history is stored in Flask session:
- Timeout: Default Flask session timeout
- Storage: Server-side (can be configured)
- Visibility: Only accessible to authenticated user's session

---

## Best Practices

1. **Security**
   - Never commit `.env` with real API keys
   - Use `.env.example` as template
   - Rotate keys periodically

2. **Performance**
   - Conversation history limited to 20 exchanges to manage tokens
   - Consider caching frequent questions
   - Implement rate limiting for production

3. **User Experience**
   - Show loading state while waiting for response
   - Allow message retry on error
   - Provide option to clear history
   - Display timestamps for long sessions

4. **Monitoring**
   - Log API usage and costs
   - Monitor error rates
   - Track popular questions for improvement

---

## Troubleshooting

### Chatbot not responding
1. Check if `OPENAI_API_KEY` is set in `.env`
2. Verify API key is valid at https://platform.openai.com/account/api-keys
3. Check Flask console for error messages
4. Verify internet connection

### High API costs
- Reduce conversation history length (currently 20 messages)
- Use cheaper models if available
- Implement response caching
- Rate limit user messages

### Slow responses
- OpenAI API latency depends on load
- Ensure server has good internet connection
- Consider using GPT-3.5-turbo (faster) vs GPT-4
- Show loading indicators to manage user expectations

---

## Example Conversations

### User: "What is phishing?"
**Assistant:** "Phishing is a cyberattack method where attackers impersonate legitimate organizations to trick you into revealing sensitive information like passwords, credit card numbers, or personal data. Attackers use various tactics including urgency, fear, and social engineering to manipulate victims into taking action without thinking carefully. Key indicators of phishing include: unexpected links or attachments, requests for sensitive information, suspicious sender addresses, and urgent language like 'Your account will be closed today!' Always verify sender email addresses, navigate directly to official websites instead of clicking email links, and contact organizations through official channels if you're unsure."

### User: "How do I spot a phishing email?"
**Assistant:** "Great question! Here are the key red flags to watch for:
1. **Sender Address** - Look carefully at the email address, not just the display name. Check for misspellings like "g00gle" instead of "google"
2. **Urgent Language** - Phrases like 'Act now!' or 'Your account is locked!' are pressure tactics
3. **Suspicious Links** - Hover over links (don't click!) to see the actual URL. Is it what you expected?
4. **Requests for Sensitive Data** - Legitimate companies never ask for passwords or credit card numbers via email
5. **Unexpected Attachments** - Be wary of files from unknown senders
6. **Grammar/Formatting** - Legitimate companies usually have good grammar and professional formatting
7. **Domain Mismatch** - If they claim to be from Amazon but the domain ends in '@not-really-amazon.com', it's phishing

When in doubt, don't click! Contact the organization directly through their official website."

### User: "Why is MFA important?"
**Assistant:** "MFA (Multi-Factor Authentication) is critical for security because:

**The Problem:** Passwords alone are vulnerable to:
- Phishing attacks
- Brute force attacks
- Data breaches
- Credential stuffing

**How MFA Helps:** MFA requires at least 2 of 3 factors:
1. Something you know (password)
2. Something you have (phone, security key)
3. Something you are (biometric)

**Real Security Impact:** Even if an attacker steals your password, they can't access your account without the second factor.

**Best MFA Methods:**
1. **Authenticator App** (Google Authenticator, Authy) - Most secure
2. **Hardware Security Key** (YubiKey) - Maximum security
3. **SMS Codes** - Better than nothing, but can be intercepted
4. **Email Codes** - Least secure of MFA options

**Recommendation:** Enable MFA on all important accounts: email, banking, social media, work accounts. Use authenticator apps when available."
