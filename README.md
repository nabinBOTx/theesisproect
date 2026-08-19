# CyberSecure Quest (Flask)

A lightweight web game that teaches cybersecurity awareness through short, scenario-based questions with instant explanations. Includes an AI-powered chatbot assistant to help users learn.

## Quickstart (Windows / PowerShell)

1. Create and activate a virtual environment:

```powershell
cd C:\Code
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure OpenAI API (optional, for chatbot):

Copy `.env.example` to `.env` and add your OpenAI API key:

```powershell
Copy-Item .env.example .env
# Edit .env and add your OpenAI API key from https://platform.openai.com/account/api-keys
```

4. Run the app:

```powershell
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Features

- **8 Interactive Games**: Phish Hunter, Spot the Scam, Device Defender, Safe to Click, Choose 2FA, Password Ninja, Inbox Investigation, and more
- **AI Chatbot Assistant**: Get help explaining concepts, learning security tips, and understanding game scenarios
- **Learning Modules**: Comprehensive cybersecurity education resources
- **Real-Time Feedback**: Instant explanations for correct and incorrect answers
- **Cyber-Themed UI**: Modern, engaging interface with dark theme

## Project Structure

- `app.py`: Flask app, routes, game logic, and question banks
- `templates/`: HTML templates for all pages and games
- `static/`: CSS, JavaScript, and chatbot files
- `requirements.txt`: Python dependencies
- `.env.example`: Environment configuration template

## Chatbot Features

The AI chatbot can:
- Answer questions about cybersecurity concepts
- Explain game scenarios and correct answers
- Provide real-world security examples
- Offer guidance on identifying threats
- Be accessed via the chat button (💬) in the bottom-right corner

### Setting Up the Chatbot

1. Get a free OpenAI API key: https://platform.openai.com/signup
2. Copy `.env.example` to `.env`
3. Add your `OPENAI_API_KEY` to `.env`
4. Restart the Flask app

The chatbot maintains conversation history and adapts its responses based on context.

## Customization

- **Add questions**: Edit `QUESTION_BANK`, `PHISH_HUNTER_CHALLENGES`, etc. in `app.py`
- **Modify chatbot behavior**: Edit `CHATBOT_SYSTEM_PROMPT` in `app.py`
- **Change styling**: Update `cyber-theme.css` and `chatbot.css`
- **Adjust game difficulty**: Modify `num_questions` parameter in game state functions

## Configuration

- The default `SECRET_KEY` in `app.py` is for local development only. Replace it in production.
- Chatbot works best with `gpt-3.5-turbo` model (you can change in `app.py`)
- Conversation history is limited to last 20 messages to manage API token usage

## Notes

- OpenAI API is optional—the game works without it, but the chatbot won't be available
- Free OpenAI credits are available for new accounts
- For production deployment, use environment variables for sensitive data (API keys, secrets)
