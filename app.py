from __future__ import annotations

import random
import os
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for, request, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from openai import OpenAI # type: ignore
from dotenv import load_dotenv

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cyberguard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


# --- Database Models ---
class User(db.Model):
    """User model for storing user account information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.String(20), default="Bronze")  # Bronze, Silver, Gold, Platinum
    xp = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(500), default="")  # JSON string of badges
    games_played = db.Column(db.Integer, default=0)
    privilege = db.Column(db.String(20), default="user")  # user, moderator, banned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password: str) -> None:
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "rank": self.rank,
            "xp": self.xp,
            "badges": self.badges.split(",") if self.badges else [],
            "games_played": self.games_played,
            "privilege": self.privilege,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


@dataclass
class Question:
    prompt: str
    choices: List[str]
    correct_index: int
    explanation: str
    category: str
    difficulty: str = "medium"  # "easy", "medium", "hard"


QUESTION_BANK: List[Question] = [
    Question(
        prompt="You receive an email from 'IT Support' asking you to reset your password using a link. The sender's address is support-it@secure-pass-reset.com. What should you do?",
        choices=[
            "Click the link and reset immediately to avoid account lockout.",
            "Reply asking if this is legitimate.",
            "Report the email as phishing and verify via the official IT portal.",
            "Forward it to colleagues to warn them."
        ],
        correct_index=2,
        explanation=(
            "Unexpected password-reset emails with third-party domains are common phishing."
            " Report it and navigate directly to the official portal instead of clicking links."
        ),
        category="Phishing",
        difficulty="easy",
    ),
    Question(
        prompt="Which password is the strongest?",
        choices=[
            "P@ssw0rd!",
            "CorrectHorseBatteryStaple#92",
            "Qwerty123!",
            "John1990!"
        ],
        correct_index=1,
        explanation=(
            "Length + randomness beats clever substitutions. A long passphrase with entropy is strongest."
        ),
        category="Passwords",
        difficulty="medium",
    ),
    Question(
        prompt="A USB stick labeled 'Salary_2025' is found in the parking lot. What is the safest action?",
        choices=[
            "Plug it into a spare computer to check contents.",
            "Give it to IT/Security for safe handling.",
            "Open on your workstation with antivirus enabled.",
            "Ignore it; leave it where it was."
        ],
        correct_index=1,
        explanation=(
            "Unknown removable media can contain malware. Turn it over to IT/Security; never plug it in."
        ),
        category="Physical",
        difficulty="easy",
    ),
    Question(
        prompt="MFA (Multi-Factor Authentication) primarily helps defend against which risk?",
        choices=[
            "DDoS attacks",
            "Stolen or guessed passwords",
            "Ransomware",
            "SQL injection"
        ],
        correct_index=1,
        explanation=(
            "MFA reduces the impact of compromised passwords by requiring a second factor."
        ),
        category="MFA",
        difficulty="medium",
    ),
    Question(
        prompt="You're sent a file 'invoice.pdf.exe' from an unknown contact. What's the best response?",
        choices=[
            "Open it in a sandbox to be safe.",
            "Rename it to .pdf and open.",
            "Delete or quarantine it and report the message.",
            "Forward to a coworker to confirm if they expected it."
        ],
        correct_index=2,
        explanation=(
            "Double extensions often hide executables. Do not open; report and quarantine/delete it."
        ),
        category="Malware",
        difficulty="hard",
    ),
    Question(
        prompt="Which is the safest network to access sensitive company data while traveling?",
        choices=[
            "Hotel Wi‑Fi without VPN",
            "Public cafe Wi‑Fi with HTTPS only",
            "Personal mobile hotspot with VPN",
            "Any public Wi‑Fi with 'Incognito mode'"
        ],
        correct_index=2,
        explanation=(
            "Use a trusted network (personal hotspot) and a VPN when handling sensitive data."
        ),
        category="Network",
        difficulty="medium",
    ),
    Question(
        prompt="A website shows a certificate warning. What should you do?",
        choices=[
            "Proceed if you recognize the site.",
            "Ignore if using Incognito mode.",
            "Stop and verify the URL/certificate or contact the site owner.",
            "Try reloading until it disappears."
        ],
        correct_index=2,
        explanation=(
            "Certificate warnings may indicate man-in-the-middle or misconfiguration. Verify before proceeding."
        ),
        category="Web",
        difficulty="hard",
    ),
    Question(
        prompt="Least privilege means...",
        choices=[
            "Giving users the broadest access to move quickly.",
            "Granting temporary admin rights to everyone.",
            "Providing only the minimal access required to perform a task.",
            "Letting users request access from peers."
        ],
        correct_index=2,
        explanation=(
            "Least privilege reduces blast radius by limiting permissions to only what's necessary."
        ),
        category="Principles",
        difficulty="hard",
    ),
    Question(
        prompt="Which is a sign of a phishing URL?",
        choices=[
            "Subdomain that looks like a company (login.company.com)",
            "Misspelled brand or extra words (company-login.secure-verify.example)",
            "Use of HTTPS",
            "A short URL"
        ],
        correct_index=1,
        explanation=(
            "Attackers often use misspellings/extra words and odd domains to appear legitimate."
        ),
        category="Phishing",
        difficulty="medium",
    ),
    Question(
        prompt="Software updates are important because they...",
        choices=[
            "Add new wallpapers",
            "Usually slow down your device",
            "Fix security vulnerabilities and bugs",
            "Aren't needed if you have antivirus"
        ],
        correct_index=2,
        explanation=(
            "Patches fix exploitable vulnerabilities. Keep OS and apps updated promptly."
        ),
        category="Patching",
        difficulty="easy",
    ),
]


def _new_game_state(num_questions: int = 8) -> Dict[str, Any]:
    questions = random.sample(QUESTION_BANK, k=min(num_questions, len(QUESTION_BANK)))
    return {
        "q_indices": [QUESTION_BANK.index(q) for q in questions],
        "current": 0,
        "score": 0,
        "answers": [],  # list of dicts: {idx, selected, correct}
    }


def _get_user_stats(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate user performance statistics from session data"""
    stats = {
        "total_games_played": 0,
        "game_scores": {},
        "overall_score": 0,
        "overall_total": 0,
        "weak_categories": [],
        "strong_categories": [],
    }
    
    # Aggregate scores from all game types
    game_types = ["game", "phish_hunter", "spot_the_scam", "device_defender", 
                  "safe_to_click", "choose_2fa", "password_ninja", "phish", "inbox"]
    
    for game_type in game_types:
        if game_type in session_data and isinstance(session_data[game_type], dict):
            game_data = session_data[game_type]
            if "score" in game_data:
                score = game_data.get("score", 0)
                total = len(game_data.get("q_indices", game_data.get("indices", [])))
                if total > 0:
                    stats["game_scores"][game_type] = {
                        "score": score,
                        "total": total,
                        "percentage": round((score / total) * 100, 1)
                    }
                    stats["total_games_played"] += 1
                    stats["overall_score"] += score
                    stats["overall_total"] += total
    
    return stats


def _get_difficulty_level(user_score_percentage: float) -> str:
    """Determine appropriate difficulty based on performance"""
    if user_score_percentage < 50:
        return "easy"
    elif user_score_percentage < 75:
        return "medium"
    else:
        return "hard"


def _new_adaptive_game_state(session_data: Dict[str, Any], num_questions: int = 8) -> Dict[str, Any]:
    """Create adaptive game state based on user performance"""
    stats = _get_user_stats(session_data)
    
    # Determine difficulty for this game
    if stats["overall_total"] == 0:
        difficulty = "medium"  # First game is medium
    else:
        overall_percentage = round((stats["overall_score"] / stats["overall_total"]) * 100, 1)
        difficulty = _get_difficulty_level(overall_percentage)
    
    # Filter questions by difficulty
    questions_by_difficulty = [q for q in QUESTION_BANK if q.difficulty == difficulty]
    
    # If not enough questions at this difficulty, mix in other difficulties
    if len(questions_by_difficulty) < num_questions:
        questions_by_difficulty = [q for q in QUESTION_BANK 
                                   if q.difficulty in ["easy", "medium", "hard"]]
    
    questions = random.sample(questions_by_difficulty, k=min(num_questions, len(questions_by_difficulty)))
    
    return {
        "q_indices": [QUESTION_BANK.index(q) for q in questions],
        "current": 0,
        "score": 0,
        "answers": [],
        "difficulty": difficulty,
    }


def _get_recommendations(session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate personalized learning recommendations"""
    stats = _get_user_stats(session_data)
    recommendations = []
    
    # Recommend learning modules for weak areas
    weak_threshold = 60  # Score below 60% indicates weakness
    
    for game_type, scores in stats["game_scores"].items():
        if scores["percentage"] < weak_threshold:
            # Map game type to learning modules
            module_map = {
                "phish_hunter": ["Phishing Awareness", "Phish Hunter Mastery"],
                "spot_the_scam": ["Spot the Scam Techniques"],
                "device_defender": ["Device Defender Security"],
                "safe_to_click": ["Safe to Click Guidelines"],
                "choose_2fa": ["Multi-Factor Authentication (MFA)", "2FA Method Selection"],
                "password_ninja": ["Password Security", "Password Ninja Skills"],
                "phish": ["Phishing Awareness"],
                "inbox": ["Email Security", "Phishing Awareness"],
                "game": ["Phishing Awareness", "Password Security", "Multi-Factor Authentication (MFA)"],
            }
            
            modules = module_map.get(game_type, [])
            recommendations.append({
                "game": game_type,
                "score": scores["percentage"],
                "message": f"You scored {scores['percentage']}% on {game_type}. Try these learning modules to improve!",
                "modules": modules,
                "priority": "high" if scores["percentage"] < 40 else "medium",
            })
    
    # Sort by priority and score
    recommendations.sort(key=lambda x: (x["priority"] != "high", x["score"]))
    
    return recommendations


# --- Spot the Phish mode data ---
@dataclass
class PhishItem:
    text: str  # could be URL or email subject/preview
    is_phish: bool
    explanation: str


PHISH_ITEMS: List[PhishItem] = [
    PhishItem(
        text="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        is_phish=False,
        explanation="Legitimate Microsoft OAuth endpoint; domain and path are correct.",
    ),
    PhishItem(
        text="https://microsoftonline.com.login.secure-reset-verify[.]com",
        is_phish=True,
        explanation="Extra words and deceptive structure on a non-Microsoft domain indicate phishing.",
    ),
    PhishItem(
        text="Invoice attached - due today!",
        is_phish=True,
        explanation="Urgency with unknown sender and attachment is a common phishing tactic.",
    ),
    PhishItem(
        text="https://accounts.google.com/ServiceLogin",
        is_phish=False,
        explanation="Google Accounts login on a legitimate google.com domain.",
    ),
    PhishItem(
        text="Password expiry notice: https://it.example-co.com/reset",
        is_phish=True,
        explanation="Looks corporate but domain mismatch from official company domain suggests phishing.",
    ),
]

def _new_phish_state(num_items: int = 6) -> Dict[str, Any]:
    # sample with replacement allowed if requesting more than available
    population = PHISH_ITEMS.copy()
    random.shuffle(population)
    items = population[: min(num_items, len(population))]
    return {
        "indices": [PHISH_ITEMS.index(x) for x in items],
        "answers": {},  # idx -> bool user says phish?
    }


@app.route("/")
def index():
    return render_template("cyber_landing.html")


# --- User Authentication Routes ---
@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation
        if not username or not email or not password:
            return render_template("register.html", error="All fields are required"), 400
        
        if len(username) < 3:
            return render_template("register.html", error="Username must be at least 3 characters"), 400
        
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters"), 400
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match"), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists"), 400
        
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email already registered"), 400
        
        # Create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Log user in
            session["user_id"] = user.id
            session["username"] = user.username
            
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            return render_template("register.html", error=f"Registration failed: {str(e)}"), 500
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            return render_template("login.html", error="Username and password are required"), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid username or password"), 401
        
        if user.privilege == "banned":
            return render_template("login.html", error="This account has been banned"), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log user in
        session["user_id"] = user.id
        session["username"] = user.username
        
        return redirect(url_for("dashboard"))
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout"""
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/learn")
def learn():
    return render_template("learn.html", modules=LEARNING_MODULES)


@app.route("/api/learning-modules/<game_type>")
def get_game_modules(game_type):
    """Get learning modules related to a specific game"""
    game_module_map = {
        "phish_hunter": ["Phishing Awareness", "Phish Hunter Mastery", "Phish Hunter Advanced Techniques", "Email Security", "Social Engineering Defense"],
        "password_ninja": ["Password Security", "Password Ninja Skills", "Password Cracking Defense", "Multi-Factor Authentication (MFA)"],
        "spot_the_scam": ["Spot the Scam Techniques", "Scam Prevention and Detection", "Social Engineering Defense"],
        "device_defender": ["Device Defender Security", "Device Hardening Techniques", "Software Updates and Patching", "Mobile Security Essentials"],
        "safe_to_click": ["Safe to Click Guidelines", "Secure Link Identification", "Web Security", "Malware Protection"],
        "choose_2fa": ["Multi-Factor Authentication (MFA)", "2FA Method Selection", "Two-Factor Authentication Best Practices"],
        "inbox": ["Email Security", "Inbox Investigation", "Phishing Awareness", "Email Security", "Social Engineering Defense", "Incident Response and Reporting"],
        "phish": ["Phishing Awareness", "Phish Hunter Mastery", "Phish Hunter Advanced Techniques", "Email Security"],
    }
    
    module_titles = game_module_map.get(game_type, [])
    modules = [m for m in LEARNING_MODULES if m.title in module_titles]
    
    return {
        "game": game_type,
        "modules": [{
            "title": m.title,
            "category": m.category,
            "content": m.content,
            "key_points": m.key_points,
            "examples": m.examples,
        } for m in modules]
    }
def learn():
    return render_template("learn.html", modules=LEARNING_MODULES)


@app.route("/games")
def games():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("games.html")


@app.route("/phish-hunter", methods=["GET", "POST"])
def phish_hunter():
    if request.method == "POST":
        # Start new game
        challenges = random.sample(PHISH_HUNTER_CHALLENGES, k=min(8, len(PHISH_HUNTER_CHALLENGES)))
        session["phish_hunter"] = {
            "indices": [PHISH_HUNTER_CHALLENGES.index(c) for c in challenges],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("phish_hunter_play"))
    return render_template("phish_hunter_index.html")


@app.route("/phish-hunter/play")
def phish_hunter_play():
    state = session.get("phish_hunter")
    if not state:
        return redirect(url_for("phish_hunter"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("phish_hunter_result"))
    
    idx = state["indices"][state["current"]]
    challenge = PHISH_HUNTER_CHALLENGES[idx]
    return render_template(
        "phish_hunter_play.html",
        challenge=challenge,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/phish-hunter/guess", methods=["POST"])
def phish_hunter_guess():
    state = session.get("phish_hunter")
    if not state:
        return redirect(url_for("phish_hunter"))
    
    guess = request.form.get("guess")  # 'phish' or 'legitimate'
    idx = state["indices"][state["current"]]
    challenge = PHISH_HUNTER_CHALLENGES[idx]
    
    # Check if guess matches
    user_says_phish = (guess == "phish")
    correct = (user_says_phish == challenge.is_phish)
    
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "guess": guess,
        "correct": correct,
    })
    state["current"] += 1
    session["phish_hunter"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("phish_hunter_result"))
    return redirect(url_for("phish_hunter_play"))


@app.route("/phish-hunter/result")
def phish_hunter_result():
    state = session.get("phish_hunter")
    if not state:
        return redirect(url_for("phish_hunter"))
    
    details = []
    for entry in state["answers"]:
        c = PHISH_HUNTER_CHALLENGES[entry["idx"]]
        details.append({
            "text": c.text,
            "is_phish": c.is_phish,
            "user_guess": entry["guess"],
            "correct": entry["correct"],
            "explanation": c.explanation,
        })
    return render_template(
        "phish_hunter_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/spot-the-scam", methods=["GET", "POST"])
def spot_the_scam():
    if request.method == "POST":
        # Start new game
        challenges = random.sample(SCAM_CHALLENGES, k=min(8, len(SCAM_CHALLENGES)))
        session["spot_the_scam"] = {
            "indices": [SCAM_CHALLENGES.index(c) for c in challenges],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("spot_the_scam_play"))
    return render_template("spot_the_scam_index.html")


@app.route("/spot-the-scam/play")
def spot_the_scam_play():
    state = session.get("spot_the_scam")
    if not state:
        return redirect(url_for("spot_the_scam"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("spot_the_scam_result"))
    
    idx = state["indices"][state["current"]]
    challenge = SCAM_CHALLENGES[idx]
    return render_template(
        "spot_the_scam_play.html",
        challenge=challenge,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/spot-the-scam/guess", methods=["POST"])
def spot_the_scam_guess():
    state = session.get("spot_the_scam")
    if not state:
        return redirect(url_for("spot_the_scam"))
    
    guess = request.form.get("guess")  # 'scam' or 'legitimate'
    idx = state["indices"][state["current"]]
    challenge = SCAM_CHALLENGES[idx]
    
    # Check if guess matches
    user_says_scam = (guess == "scam")
    correct = (user_says_scam == challenge.is_scam)
    
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "guess": guess,
        "correct": correct,
    })
    state["current"] += 1
    session["spot_the_scam"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("spot_the_scam_result"))
    return redirect(url_for("spot_the_scam_play"))


@app.route("/spot-the-scam/result")
def spot_the_scam_result():
    state = session.get("spot_the_scam")
    if not state:
        return redirect(url_for("spot_the_scam"))
    
    details = []
    for entry in state["answers"]:
        c = SCAM_CHALLENGES[entry["idx"]]
        details.append({
            "text": c.text,
            "is_scam": c.is_scam,
            "user_guess": entry["guess"],
            "correct": entry["correct"],
            "explanation": c.explanation,
        })
    return render_template(
        "spot_the_scam_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/device-defender", methods=["GET", "POST"])
def device_defender():
    if request.method == "POST":
        settings = random.sample(DEVICE_SETTINGS, k=min(6, len(DEVICE_SETTINGS)))
        session["device_defender"] = {
            "indices": [DEVICE_SETTINGS.index(s) for s in settings],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("device_defender_play"))
    return render_template("device_defender_index.html")


@app.route("/device-defender/play")
def device_defender_play():
    state = session.get("device_defender")
    if not state:
        return redirect(url_for("device_defender"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("device_defender_result"))
    
    idx = state["indices"][state["current"]]
    setting = DEVICE_SETTINGS[idx]
    return render_template(
        "device_defender_play.html",
        setting=setting,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/device-defender/answer", methods=["POST"])
def device_defender_answer():
    state = session.get("device_defender")
    if not state:
        return redirect(url_for("device_defender"))
    
    selected = int(request.form.get("choice"))
    idx = state["indices"][state["current"]]
    setting = DEVICE_SETTINGS[idx]
    
    correct = selected == setting.correct_index
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "selected": selected,
        "correct": correct,
    })
    state["current"] += 1
    session["device_defender"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("device_defender_result"))
    return redirect(url_for("device_defender_play"))


@app.route("/device-defender/result")
def device_defender_result():
    state = session.get("device_defender")
    if not state:
        return redirect(url_for("device_defender"))
    
    details = []
    for entry in state["answers"]:
        s = DEVICE_SETTINGS[entry["idx"]]
        details.append({
            "setting": s.setting,
            "options": s.options,
            "selected": entry["selected"],
            "correct_index": s.correct_index,
            "correct": entry["correct"],
            "explanation": s.explanation,
        })
    return render_template(
        "device_defender_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/safe-to-click", methods=["GET", "POST"])
def safe_to_click():
    if request.method == "POST":
        items = random.sample(SAFE_CLICK_ITEMS, k=min(6, len(SAFE_CLICK_ITEMS)))
        session["safe_to_click"] = {
            "indices": [SAFE_CLICK_ITEMS.index(i) for i in items],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("safe_to_click_play"))
    return render_template("safe_to_click_index.html")


@app.route("/safe-to-click/play")
def safe_to_click_play():
    state = session.get("safe_to_click")
    if not state:
        return redirect(url_for("safe_to_click"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("safe_to_click_result"))
    
    idx = state["indices"][state["current"]]
    item = SAFE_CLICK_ITEMS[idx]
    return render_template(
        "safe_to_click_play.html",
        item=item,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/safe-to-click/guess", methods=["POST"])
def safe_to_click_guess():
    state = session.get("safe_to_click")
    if not state:
        return redirect(url_for("safe_to_click"))
    
    guess = request.form.get("guess")
    idx = state["indices"][state["current"]]
    item = SAFE_CLICK_ITEMS[idx]
    
    user_says_safe = (guess == "safe")
    correct = (user_says_safe == item.is_safe)
    
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "guess": guess,
        "correct": correct,
    })
    state["current"] += 1
    session["safe_to_click"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("safe_to_click_result"))
    return redirect(url_for("safe_to_click_play"))


@app.route("/safe-to-click/result")
def safe_to_click_result():
    state = session.get("safe_to_click")
    if not state:
        return redirect(url_for("safe_to_click"))
    
    details = []
    for entry in state["answers"]:
        i = SAFE_CLICK_ITEMS[entry["idx"]]
        details.append({
            "text": i.text,
            "is_safe": i.is_safe,
            "user_guess": entry["guess"],
            "correct": entry["correct"],
            "explanation": i.explanation,
        })
    return render_template(
        "safe_to_click_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/choose-2fa", methods=["GET", "POST"])
def choose_2fa():
    if request.method == "POST":
        scenarios = random.sample(TWO_FACTOR_SCENARIOS, k=min(4, len(TWO_FACTOR_SCENARIOS)))
        session["choose_2fa"] = {
            "indices": [TWO_FACTOR_SCENARIOS.index(s) for s in scenarios],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("choose_2fa_play"))
    return render_template("choose_2fa_index.html")


@app.route("/choose-2fa/play")
def choose_2fa_play():
    state = session.get("choose_2fa")
    if not state:
        return redirect(url_for("choose_2fa"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("choose_2fa_result"))
    
    idx = state["indices"][state["current"]]
    scenario = TWO_FACTOR_SCENARIOS[idx]
    return render_template(
        "choose_2fa_play.html",
        scenario=scenario,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/choose-2fa/answer", methods=["POST"])
def choose_2fa_answer():
    state = session.get("choose_2fa")
    if not state:
        return redirect(url_for("choose_2fa"))
    
    selected = int(request.form.get("choice"))
    idx = state["indices"][state["current"]]
    scenario = TWO_FACTOR_SCENARIOS[idx]
    
    correct = selected == scenario.correct_index
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "selected": selected,
        "correct": correct,
    })
    state["current"] += 1
    session["choose_2fa"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("choose_2fa_result"))
    return redirect(url_for("choose_2fa_play"))


@app.route("/choose-2fa/result")
def choose_2fa_result():
    state = session.get("choose_2fa")
    if not state:
        return redirect(url_for("choose_2fa"))
    
    details = []
    for entry in state["answers"]:
        s = TWO_FACTOR_SCENARIOS[entry["idx"]]
        details.append({
            "scenario": s.scenario,
            "options": s.options,
            "selected": entry["selected"],
            "correct_index": s.correct_index,
            "correct": entry["correct"],
            "explanation": s.explanation,
        })
    return render_template(
        "choose_2fa_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/password-ninja", methods=["GET", "POST"])
def password_ninja():
    if request.method == "POST":
        # Start new game
        challenges = random.sample(PASSWORD_CHALLENGES, k=min(8, len(PASSWORD_CHALLENGES)))
        session["password_ninja"] = {
            "indices": [PASSWORD_CHALLENGES.index(c) for c in challenges],
            "current": 0,
            "score": 0,
            "answers": [],
        }
        return redirect(url_for("password_ninja_play"))
    return render_template("password_ninja_index.html")


@app.route("/password-ninja/play")
def password_ninja_play():
    state = session.get("password_ninja")
    if not state:
        return redirect(url_for("password_ninja"))
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("password_ninja_result"))
    
    idx = state["indices"][state["current"]]
    challenge = PASSWORD_CHALLENGES[idx]
    return render_template(
        "password_ninja_play.html",
        challenge=challenge,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/password-ninja/guess", methods=["POST"])
def password_ninja_guess():
    state = session.get("password_ninja")
    if not state:
        return redirect(url_for("password_ninja"))
    
    guess = request.form.get("guess")  # 'strong' or 'weak'
    idx = state["indices"][state["current"]]
    challenge = PASSWORD_CHALLENGES[idx]
    
    # Check if guess matches (strong = True, weak = False)
    user_says_strong = (guess == "strong")
    correct = (user_says_strong == challenge.is_strong)
    
    if correct:
        state["score"] += 1
    
    state["answers"].append({
        "idx": idx,
        "guess": guess,
        "correct": correct,
    })
    state["current"] += 1
    session["password_ninja"] = state
    
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("password_ninja_result"))
    return redirect(url_for("password_ninja_play"))


@app.route("/password-ninja/result")
def password_ninja_result():
    state = session.get("password_ninja")
    if not state:
        return redirect(url_for("password_ninja"))
    
    details = []
    for entry in state["answers"]:
        c = PASSWORD_CHALLENGES[entry["idx"]]
        details.append({
            "password": c.password,
            "is_strong": c.is_strong,
            "user_guess": entry["guess"],
            "correct": entry["correct"],
            "explanation": c.explanation,
        })
    return render_template(
        "password_ninja_result.html",
        score=state["score"],
        total=len(state["indices"]),
        details=details,
    )


@app.route("/start", methods=["POST"]) 
def start():
    session["game"] = _new_adaptive_game_state(session)
    return redirect(url_for("game"))


@app.route("/game")
def game():
    game = session.get("game")
    if not game:
        return redirect(url_for("index"))

    if game["current"] >= len(game["q_indices"]):
        return redirect(url_for("result"))

    q_idx = game["q_indices"][game["current"]]
    q = QUESTION_BANK[q_idx]
    return render_template("game.html", question=q, number=game["current"] + 1, total=len(game["q_indices"]))


@app.route("/answer", methods=["POST"]) 
def answer():
    game = session.get("game")
    if not game:
        return redirect(url_for("index"))

    selected_raw = request.form.get("choice")
    if selected_raw is None:
        return redirect(url_for("game"))

    q_idx = game["q_indices"][game["current"]]
    q = QUESTION_BANK[q_idx]
    selected = int(selected_raw)
    correct = selected == q.correct_index
    if correct:
        game["score"] += 1
    game["answers"].append({
        "idx": q_idx,
        "selected": selected,
        "correct": correct,
    })
    game["current"] += 1
    session["game"] = game
    if game["current"] >= len(game["q_indices"]):
        return redirect(url_for("result"))
    return redirect(url_for("game"))


@app.route("/result")
def result():
    game = session.get("game")
    if not game:
        return redirect(url_for("index"))

    details = []
    for entry in game["answers"]:
        q = QUESTION_BANK[entry["idx"]]
        details.append({
            "prompt": q.prompt,
            "choices": q.choices,
            "selected": entry["selected"],
            "correct_index": q.correct_index,
            "explanation": q.explanation,
            "category": q.category,
            "is_correct": entry["correct"],
        })
    return render_template(
        "result.html",
        score=game["score"],
        total=len(game["q_indices"]),
        details=details,
    )


# --- Spot the Phish mode ---
@app.route("/phish", methods=["GET", "POST"]) 
def phish():
    if request.method == "POST":
        # Start new session for phish mode
        session["phish"] = _new_phish_state()
        return redirect(url_for("phish_play"))
    return render_template("phish_index.html")


@app.route("/phish/play")
def phish_play():
    state = session.get("phish")
    if not state:
        return redirect(url_for("phish"))
    items = [(i, PHISH_ITEMS[i]) for i in state["indices"]]
    return render_template("phish_play.html", items=items, saved=state.get("answers", {}))


@app.route("/phish/submit", methods=["POST"]) 
def phish_submit():
    state = session.get("phish")
    if not state:
        return redirect(url_for("phish"))
    answers: Dict[int, bool] = {}
    for idx in state["indices"]:
        val = request.form.get(f"item_{idx}")
        answers[idx] = (val == "phish")
    state["answers"] = answers
    session["phish"] = state

    # compute results
    details = []
    score = 0
    for idx in state["indices"]:
        item = PHISH_ITEMS[idx]
        user_says_phish = answers.get(idx, False)
        correct = (user_says_phish == item.is_phish)
        if correct:
            score += 1
        details.append({
            "text": item.text,
            "is_phish": item.is_phish,
            "user": user_says_phish,
            "correct": correct,
            "explanation": item.explanation,
        })
    return render_template("phish_result.html", score=score, total=len(state["indices"]), details=details)


# --- Device Defender Game ---
@dataclass
class DeviceSetting:
    setting: str
    options: List[str]
    correct_index: int
    explanation: str


DEVICE_SETTINGS: List[DeviceSetting] = [
    DeviceSetting(
        setting="Screen Lock",
        options=[
            "No lock (convenience)",
            "Pattern lock",
            "6-digit PIN",
            "Biometric (fingerprint/face) + PIN"
        ],
        correct_index=3,
        explanation="Biometric + PIN provides the strongest security. Biometrics are convenient but can be bypassed; PIN adds a second layer.",
    ),
    DeviceSetting(
        setting="App Permissions",
        options=[
            "Allow all permissions for convenience",
            "Review and grant only necessary permissions",
            "Deny all permissions"
        ],
        correct_index=1,
        explanation="Grant only necessary permissions. Apps don't need access to everything - review what each app actually requires.",
    ),
    DeviceSetting(
        setting="Automatic Updates",
        options=[
            "Disable updates to save data",
            "Manual updates only",
            "Enable automatic updates"
        ],
        correct_index=2,
        explanation="Automatic updates keep your device secure with the latest security patches. Enable them for best protection.",
    ),
    DeviceSetting(
        setting="Wi-Fi Connections",
        options=[
            "Auto-connect to any open Wi-Fi",
            "Connect only to known networks",
            "Disable Wi-Fi completely"
        ],
        correct_index=1,
        explanation="Only connect to trusted networks. Open/public Wi-Fi can be insecure and used by attackers.",
    ),
    DeviceSetting(
        setting="Location Services",
        options=[
            "Always on for all apps",
            "On only when using apps that need it",
            "Always off"
        ],
        correct_index=1,
        explanation="Enable location only when needed. Constant location tracking poses privacy risks and drains battery.",
    ),
    DeviceSetting(
        setting="Find My Device",
        options=[
            "Disabled",
            "Enabled (for lost device tracking)"
        ],
        correct_index=1,
        explanation="Enable Find My Device! This helps locate, lock, or erase your phone if lost or stolen.",
    ),
]


# --- Daily Mission: Is this safe to click? ---
@dataclass
class SafeClickItem:
    text: str  # URL or link text
    is_safe: bool
    explanation: str


SAFE_CLICK_ITEMS: List[SafeClickItem] = [
    SafeClickItem(
        text="https://www.bankofamerica.com/login",
        is_safe=True,
        explanation="Safe! Official Bank of America domain. Always verify the domain matches the official website.",
    ),
    SafeClickItem(
        text="https://bankofamerica.com.secure-login.verify-account.com",
        is_safe=False,
        explanation="Dangerous! Deceptive URL structure. The real domain is at the end, not the beginning. This is likely phishing.",
    ),
    SafeClickItem(
        text="Click here to verify your account: bit.ly/verify-account-now",
        is_safe=False,
        explanation="Dangerous! Shortened URLs can hide malicious destinations. Never click shortened links in unsolicited messages.",
    ),
    SafeClickItem(
        text="https://docs.google.com/document/d/abc123",
        is_safe=True,
        explanation="Safe! Official Google Docs link. Google Drive links from trusted sources are generally safe.",
    ),
    SafeClickItem(
        text="You've won! Claim prize: http://free-prize-winner.com/claim",
        is_safe=False,
        explanation="Dangerous! HTTP (not HTTPS) and suspicious domain. Legitimate sites use HTTPS and official domains.",
    ),
    SafeClickItem(
        text="https://github.com/username/repository",
        is_safe=True,
        explanation="Safe! Official GitHub domain. Code repositories on GitHub are generally safe to view.",
    ),
]


# --- Daily Mission: Choose the best 2FA method ---
@dataclass
class TwoFactorOption:
    scenario: str
    options: List[str]
    correct_index: int
    explanation: str


TWO_FACTOR_SCENARIOS: List[TwoFactorOption] = [
    TwoFactorOption(
        scenario="Setting up 2FA for your email account. Which method is most secure?",
        options=[
            "SMS text message codes",
            "Authenticator app (Google Authenticator, Authy)",
            "Email verification codes",
            "Security questions"
        ],
        correct_index=1,
        explanation="Authenticator apps are more secure than SMS. SMS can be intercepted via SIM swapping attacks.",
    ),
    TwoFactorOption(
        scenario="You lost your phone with your authenticator app. What should you do?",
        options=[
            "Wait and hope you find it",
            "Use backup codes to disable 2FA and set up new method",
            "Contact support immediately to secure your account"
        ],
        correct_index=2,
        explanation="Contact support immediately! They can help you secure your account and set up new 2FA methods.",
    ),
    TwoFactorOption(
        scenario="Which 2FA method is best for someone who doesn't have a smartphone?",
        options=[
            "SMS codes",
            "Hardware security key",
            "No 2FA (too complicated)",
            "Email codes"
        ],
        correct_index=1,
        explanation="Hardware security keys (like YubiKey) are excellent for non-smartphone users. They're more secure than SMS.",
    ),
    TwoFactorOption(
        scenario="You receive an unexpected 2FA code request. What should you do?",
        options=[
            "Approve it in case you forgot",
            "Ignore it - someone may have your password",
            "Click approve to see what happens"
        ],
        correct_index=1,
        explanation="Never approve unexpected 2FA requests! Someone likely has your password. Change your password immediately.",
    ),
]


# --- Spot the Scam Game ---
@dataclass
class ScamChallenge:
    text: str  # Scam message or scenario
    is_scam: bool
    explanation: str


SCAM_CHALLENGES: List[ScamChallenge] = [
    ScamChallenge(
        text="Congratulations! You've won $1,000,000! To claim your prize, send $500 processing fee to claim@prize-winner.com",
        is_scam=True,
        explanation="Classic scam! Legitimate prizes don't require upfront fees. Real winners are contacted through official channels.",
    ),
    ScamChallenge(
        text="Your computer has a virus! Call 1-800-TECH-HELP now or your files will be deleted. Press 1 to speak with our technician.",
        is_scam=True,
        explanation="Tech support scam! Legitimate companies don't call unsolicited. This is a tactic to get remote access and payment.",
    ),
    ScamChallenge(
        text="Your Amazon order #123-4567890 has shipped. Track your package: https://www.amazon.com/track",
        is_scam=False,
        explanation="Legitimate! Official Amazon domain and standard order notification format.",
    ),
    ScamChallenge(
        text="I'm a Nigerian prince with millions to share. I need your help transferring funds. Send your bank details and you'll receive 20%.",
        is_scam=True,
        explanation="Classic advance-fee scam! No legitimate person asks for bank details via email to share money.",
    ),
    ScamChallenge(
        text="Your Social Security number has been suspended due to suspicious activity. Call immediately or face arrest: 1-800-SSA-FAKE",
        is_scam=True,
        explanation="Government impersonation scam! SSA never suspends numbers or calls with threats. This is identity theft.",
    ),
    ScamChallenge(
        text="You've inherited $50,000 from a distant relative! Reply with your personal information and bank account to receive funds.",
        is_scam=True,
        explanation="Inheritance scam! Legitimate inheritances go through lawyers and courts, not random emails.",
    ),
    ScamChallenge(
        text="Your PayPal account has been limited. Click here to verify: https://www.paypal.com/account",
        is_scam=False,
        explanation="Legitimate! Official PayPal domain. However, always verify by logging in directly, never via email links.",
    ),
    ScamChallenge(
        text="Urgent! Your grandson is in jail and needs $2,000 bail money. Send gift cards immediately!",
        is_scam=True,
        explanation="Grandparent scam! Scammers create urgency and ask for untraceable payment methods like gift cards.",
    ),
    ScamChallenge(
        text="Make $5,000 a week working from home! No experience needed. Just pay $99 for our starter kit and you'll be rich!",
        is_scam=True,
        explanation="Work-from-home scam! Legitimate jobs don't require upfront payments. This is a pyramid scheme or fraud.",
    ),
    ScamChallenge(
        text="Your Netflix subscription expires tomorrow. Update payment: https://www.netflix.com/account",
        is_scam=False,
        explanation="Legitimate! Official Netflix domain. Always access account settings directly from the Netflix website.",
    ),
    ScamChallenge(
        text="I'm a US soldier stationed overseas. I found a crate of gold and need help. Send $1,000 for shipping, get $100,000 in return!",
        is_scam=True,
        explanation="Romance/military scam! Scammers impersonate soldiers and ask for money with promises of large returns.",
    ),
    ScamChallenge(
        text="Bitcoin investment opportunity! Double your money in 24 hours! Guaranteed returns! Invest now!",
        is_scam=True,
        explanation="Investment scam! No legitimate investment guarantees returns, especially not in 24 hours. This is a Ponzi scheme.",
    ),
]


# --- Phish Hunter Game ---
@dataclass
class PhishChallenge:
    text: str  # URL, email subject, or email snippet
    is_phish: bool
    explanation: str


PHISH_HUNTER_CHALLENGES: List[PhishChallenge] = [
    PhishChallenge(
        text="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        is_phish=False,
        explanation="Legitimate Microsoft OAuth endpoint. Official microsoftonline.com domain with correct path structure.",
    ),
    PhishChallenge(
        text="https://microsoftonline.com.login.secure-reset-verify.com",
        is_phish=True,
        explanation="Phishing! Deceptive structure with extra words. Real Microsoft domain would be microsoftonline.com, not a subdomain of another domain.",
    ),
    PhishChallenge(
        text="URGENT: Your account will be suspended in 24 hours! Click here to verify.",
        is_phish=True,
        explanation="Phishing! Creates false urgency to make you act without thinking. Legitimate companies don't suspend accounts with such threats.",
    ),
    PhishChallenge(
        text="https://accounts.google.com/ServiceLogin",
        is_phish=False,
        explanation="Legitimate Google login page. Official accounts.google.com domain is correct.",
    ),
    PhishChallenge(
        text="Password expiry notice: https://it.example-co.com/reset",
        is_phish=True,
        explanation="Phishing! Domain mismatch suggests it's not from the official company. Legitimate IT departments use official company domains.",
    ),
    PhishChallenge(
        text="Invoice #8472 attached - payment due today",
        is_phish=True,
        explanation="Phishing! Unsolicited invoice with urgency is a common scam tactic. Always verify unexpected invoices.",
    ),
    PhishChallenge(
        text="You've won $10,000! Click here to claim your prize!",
        is_phish=True,
        explanation="Phishing! Too good to be true offers are classic scams. Legitimate companies don't send unsolicited prize notifications.",
    ),
    PhishChallenge(
        text="https://github.com/login",
        is_phish=False,
        explanation="Legitimate GitHub login. Official github.com domain is correct.",
    ),
    PhishChallenge(
        text="Your package couldn't be delivered. Track: http://ship-verify.co/track/8472",
        is_phish=True,
        explanation="Phishing! Non-HTTPS link and unknown courier domain. Legitimate delivery companies use HTTPS and official domains.",
    ),
    PhishChallenge(
        text="Security Alert: We detected unusual activity. Verify: https://secure.paypal.com/verify",
        is_phish=True,
        explanation="Phishing! Even though the domain looks legitimate, unexpected security alerts asking for verification are often scams. Contact PayPal directly.",
    ),
    PhishChallenge(
        text="https://www.amazon.com/gp/css/homepage.html",
        is_phish=False,
        explanation="Legitimate Amazon account page. Official amazon.com domain is correct.",
    ),
    PhishChallenge(
        text="Congratulations! You've been selected for a job. Reply with your SSN and bank details.",
        is_phish=True,
        explanation="Phishing! Legitimate employers never ask for SSN or bank details via email. This is identity theft.",
    ),
]


# --- Password Ninja Game ---
@dataclass
class PasswordChallenge:
    password: str
    is_strong: bool
    explanation: str


PASSWORD_CHALLENGES: List[PasswordChallenge] = [
    PasswordChallenge(
        password="P@ssw0rd!",
        is_strong=False,
        explanation="Common substitutions (a→@, o→0) don't add much security. Too short and predictable.",
    ),
    PasswordChallenge(
        password="CorrectHorseBatteryStaple#92",
        is_strong=True,
        explanation="Long passphrase with random words is much stronger than short complex passwords.",
    ),
    PasswordChallenge(
        password="John1990!",
        is_strong=False,
        explanation="Contains personal information (name, birth year) which is easily guessable.",
    ),
    PasswordChallenge(
        password="Qwerty123!",
        is_strong=False,
        explanation="Common keyboard pattern with predictable additions. Very weak.",
    ),
    PasswordChallenge(
        password="Sunset-Mountain-Coffee-42#",
        is_strong=True,
        explanation="Long passphrase format with separators and numbers - strong and memorable.",
    ),
    PasswordChallenge(
        password="Tr0ub4dor&3",
        is_strong=False,
        explanation="Substitutions are predictable. Attackers know these common patterns.",
    ),
    PasswordChallenge(
        password="MyDogFluffy2024!",
        is_strong=False,
        explanation="Personal info (pet name, year) makes it guessable. Avoid personal details.",
    ),
    PasswordChallenge(
        password="Dancing-Pirate-Coffee-7$",
        is_strong=True,
        explanation="Random words with separators and special characters - excellent strength.",
    ),
    PasswordChallenge(
        password="12345678",
        is_strong=False,
        explanation="Sequential numbers are extremely weak. Never use simple patterns.",
    ),
    PasswordChallenge(
        password="ThunderStormLightning99!",
        is_strong=True,
        explanation="Long combination of random words with numbers and symbols is very strong.",
    ),
]


# --- Learning Modules ---
@dataclass
class LearningModule:
    title: str
    category: str
    content: List[str]  # List of paragraphs
    key_points: List[str]
    examples: List[str]


LEARNING_MODULES: List[LearningModule] = [
    LearningModule(
        title="Phishing Awareness",
        category="Phishing",
        content=[
            "Phishing is a cyberattack method where attackers impersonate legitimate organizations to trick you into revealing sensitive information like passwords, credit card numbers, or personal data.",
            "Attackers use various tactics including urgency, fear, and social engineering to manipulate victims into taking action without thinking carefully.",
            "Phishing emails often contain suspicious links, attachments, or requests for sensitive information that legitimate organizations would never ask for via email.",
        ],
        key_points=[
            "Never click links in unsolicited emails—navigate directly to the official website",
            "Verify sender email addresses carefully—look for misspellings or unusual domains",
            "Legitimate organizations rarely ask for passwords or sensitive data via email",
            "Be suspicious of urgent requests or threats (e.g., 'Your account will be closed today!')",
            "When in doubt, contact the organization through official channels",
        ],
        examples=[
            "Legitimate: login.microsoftonline.com - Official Microsoft domain",
            "Phishing: microsoftonline.com.login.secure-reset-verify.com - Deceptive structure",
            "Legitimate: Password reset emails from known company IT portal",
            "Phishing: 'URGENT: Reset password now!' from unknown sender with third-party domain",
        ],
    ),
    LearningModule(
        title="Password Security",
        category="Passwords",
        content=[
            "Strong passwords are your first line of defense against unauthorized access to your accounts.",
            "Length is more important than complexity. A long passphrase with random words is stronger than a short complex password with substitutions.",
            "Password managers help you create and store unique, strong passwords for each account without having to remember them all.",
        ],
        key_points=[
            "Use long passphrases (12+ characters) instead of short complex passwords",
            "Create unique passwords for each account—never reuse passwords",
            "Avoid personal information like names, birthdays, or common words",
            "Use a password manager to generate and store secure passwords",
            "Enable multi-factor authentication (MFA) wherever possible",
        ],
        examples=[
            "Weak: P@ssw0rd! - Common substitutions, short, predictable",
            "Strong: CorrectHorseBatteryStaple#92 - Long, random words, unique",
            "Weak: John1990! - Contains personal info, easily guessable",
            "Strong: Sunset-Mountain-Coffee-42# - Passphrase format, memorable yet secure",
        ],
    ),
    LearningModule(
        title="Multi-Factor Authentication (MFA)",
        category="MFA",
        content=[
            "Multi-Factor Authentication adds an extra layer of security beyond just a password by requiring additional verification.",
            "MFA typically combines something you know (password), something you have (phone/app), or something you are (biometric).",
            "Even if an attacker steals your password, they can't access your account without the second factor.",
        ],
        key_points=[
            "MFA significantly reduces the risk of account compromise from stolen passwords",
            "Use authenticator apps (like Google Authenticator) instead of SMS when possible",
            "Enable MFA on all important accounts: email, banking, social media, work accounts",
            "Backup codes should be stored securely—never in plain text or shared",
            "If you receive an unexpected MFA request, don't approve it—someone may have your password",
        ],
        examples=[
            "Common MFA methods: SMS codes, authenticator apps, hardware tokens, biometrics",
            "Why it works: Password + phone app code = two factors required",
            "Attack prevention: Even with password, attacker needs physical access to your phone",
        ],
    ),
    LearningModule(
        title="Physical Security",
        category="Physical",
        content=[
            "Physical security protects your devices and data from unauthorized physical access.",
            "Attackers may leave malicious USB drives, attempt shoulder surfing, or steal devices to gain access to systems.",
            "Following physical security best practices prevents attackers from bypassing digital security measures.",
        ],
        key_points=[
            "Never plug in unknown USB devices or drives—they may contain malware",
            "Lock your computer when stepping away (Windows+L or Cmd+Ctrl+Q)",
            "Don't leave sensitive documents or passwords visible on your desk",
            "Report found USB drives to IT/Security—never attempt to access them yourself",
            "Use screen protectors to prevent shoulder surfing in public places",
        ],
        examples=[
            "Safe action: Report found USB drive to IT department for safe handling",
            "Unsafe: Plugging unknown USB into your computer to 'check what's on it'",
            "Safe: Locking screen when leaving desk, even briefly",
            "Unsafe: Leaving laptop unlocked in public spaces",
        ],
    ),
    LearningModule(
        title="Malware Protection",
        category="Malware",
        content=[
            "Malware includes viruses, ransomware, spyware, and other malicious software designed to damage or gain unauthorized access to systems.",
            "Malware can be delivered through email attachments, downloads, USB drives, or malicious websites.",
            "Attackers use techniques like double file extensions (.pdf.exe) to trick users into executing malicious files.",
        ],
        key_points=[
            "Don't open attachments from unknown or unexpected senders",
            "Be suspicious of double extensions like 'invoice.pdf.exe'—this is a common malware trick",
            "Keep antivirus software updated and enable real-time scanning",
            "Only download software from official, trusted sources",
            "If unsure about a file, delete it or report it—don't try to open it",
        ],
        examples=[
            "Malicious: invoice.pdf.exe - Appears as PDF but is actually executable malware",
            "Safe: invoice.pdf - Legitimate PDF from trusted sender",
            "Malicious: document.docx.scr - Screen saver file disguised as document",
            "Safe: document.docx - Known file type from verified sender",
        ],
    ),
    LearningModule(
        title="Network Security",
        category="Network",
        content=[
            "Network security protects data as it travels across networks, especially public Wi-Fi networks.",
            "Public Wi-Fi networks are often unsecured, making it easy for attackers to intercept your data.",
            "Using a VPN (Virtual Private Network) encrypts your internet traffic, protecting it from eavesdroppers.",
        ],
        key_points=[
            "Avoid accessing sensitive information on public Wi-Fi without a VPN",
            "Use your personal mobile hotspot when possible—it's more secure than public Wi-Fi",
            "Always use HTTPS websites (look for the padlock icon) when possible",
            "VPNs encrypt your traffic, making it unreadable to attackers on the same network",
            "Don't perform banking or enter passwords on unsecured public networks",
        ],
        examples=[
            "Safe: Personal mobile hotspot with VPN for accessing company data",
            "Unsafe: Hotel Wi-Fi without VPN for sensitive work",
            "Safe: HTTPS websites on any network (traffic is encrypted)",
            "Unsafe: HTTP websites on public Wi-Fi (data can be intercepted)",
        ],
    ),
    LearningModule(
        title="Web Security",
        category="Web",
        content=[
            "Web security involves protecting yourself while browsing the internet and interacting with websites.",
            "SSL/TLS certificates verify website identity and encrypt data between your browser and the website.",
            "Certificate warnings indicate potential security issues and should not be ignored.",
        ],
        key_points=[
            "Always check the URL before entering credentials—look for misspellings or unusual domains",
            "Certificate warnings may indicate man-in-the-middle attacks—don't ignore them",
            "Use HTTPS (not HTTP) for any site where you enter passwords or sensitive data",
            "Be cautious of shortened URLs—they can hide malicious destinations",
            "Look for the padlock icon in your browser's address bar",
        ],
        examples=[
            "Safe: https://accounts.google.com - Official Google domain, HTTPS enabled",
            "Unsafe: http://accounts.google.com - Missing HTTPS encryption",
            "Warning sign: Certificate error on known website - May indicate attack",
            "Phishing: accounts.g00gle.com - Looks similar but is a different domain",
        ],
    ),
    LearningModule(
        title="Security Principles",
        category="Principles",
        content=[
            "Security principles provide foundational guidelines for protecting information and systems.",
            "The principle of least privilege means users should only have the minimum access necessary to perform their job functions.",
            "Defense in depth uses multiple layers of security controls to protect against various attack vectors.",
        ],
        key_points=[
            "Least Privilege: Grant only the minimum access necessary for each user or system",
            "Defense in Depth: Use multiple security layers (firewalls, antivirus, MFA, encryption)",
            "Separation of Duties: Critical operations should require multiple people",
            "Fail Secure: Systems should default to secure state when failures occur",
            "Security by Design: Build security into systems from the beginning, not as an afterthought",
        ],
        examples=[
            "Least Privilege: A junior employee doesn't need admin access to perform daily tasks",
            "Defense in Depth: Password + MFA + encrypted connection + antivirus = multiple layers",
            "Good practice: Regular access reviews to ensure users only have necessary permissions",
            "Bad practice: Giving everyone admin rights 'to make things easier'",
        ],
    ),
    LearningModule(
        title="Software Updates and Patching",
        category="Patching",
        content=[
            "Software updates and patches fix security vulnerabilities, bugs, and add new features.",
            "Cybercriminals actively exploit known vulnerabilities in outdated software.",
            "Keeping software updated is one of the most important security practices you can follow.",
        ],
        key_points=[
            "Enable automatic updates for operating systems and applications when possible",
            "Don't delay critical security updates—they fix exploitable vulnerabilities",
            "Update all software regularly: OS, browsers, applications, plugins",
            "Updates don't slow down devices—they often improve performance and security",
            "Antivirus software alone isn't enough—you still need to patch vulnerabilities",
        ],
        examples=[
            "Important: Security patches fix vulnerabilities attackers are actively exploiting",
            "Why it matters: Unpatched systems are the #1 attack vector for ransomware",
            "Best practice: Enable auto-updates and check for updates monthly",
            "Myth: 'If it works, don't update it' - Outdated software is a security risk",
        ],
    ),
    LearningModule(
        title="Phish Hunter Mastery",
        category="Phishing",
        content=[
            "Phishing detection is a critical skill in cybersecurity. Attackers use sophisticated social engineering to trick victims into compromising their security.",
            "The Phish Hunter game trains you to identify phishing URLs, emails, and messages by examining suspicious indicators.",
            "Red flags include unusual sender addresses, urgent language, requests for sensitive information, and mismatched domains.",
        ],
        key_points=[
            "Examine sender email addresses carefully—look for slight misspellings",
            "Check URL destinations before clicking—hover to see the actual link",
            "Urgent or threatening language ('Act now!' 'Your account is locked') is often phishing",
            "Legitimate companies don't request passwords or sensitive data via email",
            "Trust your instinct—when something feels off, it probably is",
        ],
        examples=[
            "Phishing: From 'support@amazon-verify.com' - Not the real Amazon domain",
            "Legitimate: From 'your-mailing-list@amazon.com' - Proper Amazon domain",
            "Phishing URL: 'http://paypa1.com' - Note the number 1 instead of letter l",
            "Real URL: 'https://www.paypal.com' - Official domain with HTTPS",
        ],
    ),
    LearningModule(
        title="Password Ninja Skills",
        category="Passwords",
        content=[
            "Password strength is determined by length, randomness, and uniqueness. The Password Ninja game teaches you to evaluate password quality.",
            "Long passphrases (15+ characters) are more secure than short passwords with special characters.",
            "Weak passwords use common patterns, personal information, or sequential characters that hackers can guess with specialized tools.",
        ],
        key_points=[
            "Length matters more than complexity—15 characters is better than 8 with symbols",
            "Avoid keyboard patterns (qwerty, asdfgh) and sequential numbers",
            "Don't use family names, birthdays, or pets in passwords",
            "Each account needs a unique password—reuse enables credential stuffing attacks",
            "Use passphrase format: 'Purple-Elephant-Dancing-42!' combines memorability and security",
        ],
        examples=[
            "Weak: Password123 - Contains word 'password' and obvious number pattern",
            "Strong: CrimsonMountain-Sunrise-Guitar#47 - Long random passphrase",
            "Weak: 123456 - Most common password worldwide, extremely weak",
            "Strong: BountyfulGarden-Whisper-Code99 - 31 characters, highly random",
        ],
    ),
    LearningModule(
        title="Spot the Scam Techniques",
        category="Social Engineering",
        content=[
            "Scams come in many forms: romance scams, lottery fraud, tech support scams, and inheritance fraud. Each has distinct characteristics.",
            "The Spot the Scam game teaches you to identify red flags common across different scam types.",
            "Successful scams exploit human psychology: greed, urgency, curiosity, and desire to help.",
        ],
        key_points=[
            "If it sounds too good to be true, it is—especially unsolicited offers",
            "Scammers create artificial urgency: 'Claim your prize in 24 hours!'",
            "Requests for payment or personal information are red flags",
            "Legitimate companies have verifiable contact information and don't pressure you",
            "Tech support scams use pop-ups or calls claiming your device has viruses",
        ],
        examples=[
            "Lottery scam: 'You won! Send $500 for processing fees' - No legitimate lottery works this way",
            "Romance scam: Stranger online claims to love you after days of chatting",
            "Tech scam: Pop-up says 'Your device is infected! Call 1-800-FAKE'",
            "Inheritance scam: Email from 'lawyer' about deceased relative leaving you money",
        ],
    ),
    LearningModule(
        title="Safe to Click Guidelines",
        category="Malware & Links",
        content=[
            "Not all links are safe. The Safe to Click game teaches you to evaluate URLs for danger indicators before clicking.",
            "Malicious links can download malware, lead to phishing pages, or contain exploits for browser vulnerabilities.",
            "Website reputation, HTTPS status, and sender context all matter when deciding whether a link is safe.",
        ],
        key_points=[
            "Shortened URLs hide the destination—avoid clicking unless from trusted sources",
            "Check if HTTPS is enabled (padlock icon) for sites requesting sensitive information",
            "Links from unknown senders should be viewed with extreme suspicion",
            "Hover over links to see the actual destination before clicking",
            "Be wary of links in unexpected messages, even from known contacts whose account may be compromised",
        ],
        examples=[
            "Safe: https://www.example.com - Known domain with HTTPS",
            "Unsafe: bit.ly/xyz123 - Shortened URL could go anywhere",
            "Suspicious: Link in email from 'friend' with subject 'Check this out!' - Possible compromise",
            "Safe: Link from company official website in newsletter you subscribed to",
        ],
    ),
    LearningModule(
        title="Device Defender Security",
        category="Device Management",
        content=[
            "Device security involves protecting your computer or phone from unauthorized access and malware. The Device Defender game teaches secure device settings.",
            "Proper configuration includes automatic updates, antivirus protection, firewall enablement, and disk encryption.",
            "Many devices ship with default settings that prioritize usability over security.",
        ],
        key_points=[
            "Enable automatic security updates on all devices",
            "Use strong passwords or biometric authentication (fingerprint, face recognition)",
            "Enable firewall protection (usually on by default in modern systems)",
            "Use encrypted storage to protect data if device is stolen",
            "Disable unnecessary wireless features (Bluetooth, NFC) when not needed",
        ],
        examples=[
            "Good: Windows Update set to automatic, Defender enabled, Firewall active",
            "Bad: Updates disabled, antivirus turned off to 'speed up' the device",
            "Good: Biometric lock + PIN backup on smartphone",
            "Bad: 'Password is 1234' or device has no lock screen at all",
        ],
    ),
    LearningModule(
        title="2FA Method Selection",
        category="Authentication",
        content=[
            "Multi-factor authentication methods vary in security strength and usability. The Choose 2FA game teaches you which methods work best in different situations.",
            "Authentication factors include: something you know (password), something you have (phone), something you are (biometrics).",
            "Different accounts have different risk levels and may warrant different authentication methods.",
        ],
        key_points=[
            "Authenticator apps (Google Authenticator, Authy) are more secure than SMS",
            "SMS is better than nothing but can be intercepted or redirected by sophisticated attackers",
            "Hardware tokens (YubiKey) provide maximum security but require purchasing physical devices",
            "Biometric authentication (face/fingerprint) is convenient and reasonably secure",
            "Use strongest available MFA method for high-value accounts (email, banking, work)",
        ],
        examples=[
            "Most secure: Hardware token + PIN (used by security professionals)",
            "Very secure: Authenticator app on protected phone",
            "Good: SMS code (widely available, but can be intercepted)",
            "Poor: Email-based 2FA alone (easily compromised if email is hacked)",
        ],
    ),
    LearningModule(
        title="Inbox Investigation",
        category="Email Security",
        content=[
            "Email is a primary attack vector. The Inbox Investigator game simulates real-world phishing and scam emails to train your email security judgment.",
            "Every suspicious email should be evaluated for: sender authenticity, content legitimacy, urgency, and requests for information.",
            "Phishing emails are increasingly sophisticated and may appear legitimate at first glance.",
        ],
        key_points=[
            "Verify sender address matches the organization's official domain",
            "Look for grammatical errors and formatting issues in official emails",
            "Legitimate companies rarely ask for passwords or credit card numbers via email",
            "Check if attachments are expected—unsolicited attachments are often malicious",
            "When in doubt, contact the organization through official channels",
        ],
        examples=[
            "Phishing: CEO urgently needs wire transfer details (CEO fraud scam)",
            "Real: HR notification about upcoming training session",
            "Phishing: 'Confirm account information' with suspicious-looking login form",
            "Real: Notification about security update with link to legitimate portal",
        ],
    ),
    LearningModule(
        title="Email Security",
        category="Email",
        content=[
            "Email is one of the most common attack vectors for phishing, malware distribution, and social engineering attacks.",
            "Most organizations rely heavily on email for business communication, making it a prime target for cybercriminals.",
            "Email security involves verifying sender authenticity, examining content for suspicious elements, and reporting threats.",
        ],
        key_points=[
            "Check sender email addresses match official company domains",
            "Legitimate companies rarely request sensitive information via email",
            "Unsolicited attachments, especially from unknown senders, are often malicious",
            "Use email filters and anti-phishing tools provided by your organization",
            "Report suspicious emails to your IT/Security team rather than ignoring them",
        ],
        examples=[
            "Safe: noreply@company.official.com - Matches official domain",
            "Phishing: noreply@company.official.phishing.com - Similar but deceptive",
            "Safe: Expected attachment from known colleague",
            "Phishing: 'urgent-document.pdf.exe' - Double extension is red flag",
        ],
    ),
    LearningModule(
        title="Social Engineering Defense",
        category="Social Engineering",
        content=[
            "Social engineering manipulates people into divulging confidential information or performing security-breaking actions.",
            "Social engineers use psychological tactics: trust, urgency, authority, fear, and reciprocity.",
            "Defense against social engineering requires awareness, verification, and healthy skepticism.",
        ],
        key_points=[
            "Verify requests for sensitive information through official channels",
            "Be suspicious of urgent requests that bypass normal procedures",
            "Trust your instinct—if something feels wrong, it probably is",
            "Don't feel obligated to comply with requests from authority figures via unusual channels",
            "Use call-back verification: hang up and call the official number yourself",
        ],
        examples=[
            "Social engineer: 'I'm from IT, your account is locked, give me your password now'",
            "Defense: 'I'll call IT directly using the number on our internal directory'",
            "Social engineer: 'Click here to verify your account (urgent!)'",
            "Defense: 'I'll navigate directly to the official website without clicking links'",
        ],
    ),
    LearningModule(
        title="Phish Hunter Advanced Techniques",
        category="Phishing",
        content=[
            "Advanced phishing attacks use sophisticated techniques including domain spoofing, legitimate-looking layouts, and emotional manipulation.",
            "Indicators of phishing include suspicious headers, mismatched sender and reply-to addresses, and unusual link structures.",
            "Modern phishing emails can bypass traditional security measures by using compromised legitimate accounts.",
        ],
        key_points=[
            "Check email headers for routing information and verify sender path",
            "Look for inconsistencies: sender name vs. email address, company logos vs. domain",
            "Hover over links to see actual URL destination before clicking",
            "Be wary of emails from known contacts sent at unusual times with odd requests",
            "Use security tools: check sender reputation, domain verification, and email authentication (SPF, DKIM, DMARC)",
        ],
        examples=[
            "Advanced phishing: Uses stolen logo, professional template, but suspicious sender domain",
            "Red flag: Sender name 'John Smith' but email from 'js.secure@thirdparty.com'",
            "Warning: Email appears to be from your boss but asks for wire transfer to unfamiliar account",
            "Safe: Emails with proper authentication headers and verified domain",
        ],
    ),
    LearningModule(
        title="Password Cracking Defense",
        category="Passwords",
        content=[
            "Passwords can be compromised through various methods: brute force, dictionary attacks, rainbow tables, and credential stuffing.",
            "Strong passwords with sufficient length and entropy can resist these attacks for a practical length of time.",
            "Multi-factor authentication adds protection even if passwords are compromised.",
        ],
        key_points=[
            "Use 12+ character passwords to resist brute force attacks",
            "Unique passwords prevent credential stuffing attacks across multiple services",
            "Password managers reduce likelihood of weak passwords and enable unique per-account passwords",
            "Never reuse passwords across accounts—one breach exposes all accounts with that password",
            "MFA protects accounts even when passwords are compromised",
        ],
        examples=[
            "Dictionary attack: Tests common words and patterns—long random passphrases prevent this",
            "Brute force: Tests all character combinations—longer passwords take exponentially longer",
            "Credential stuffing: Uses leaked password+username pairs—unique passwords prevent this",
            "Defense: Strong unique password + MFA prevents all these methods",
        ],
    ),
    LearningModule(
        title="Two-Factor Authentication Best Practices",
        category="Authentication",
        content=[
            "Two-factor authentication (2FA) dramatically improves account security by requiring a second verification factor.",
            "Different 2FA methods offer different security levels and usability tradeoffs.",
            "Proper 2FA implementation includes backup codes and recovery options.",
        ],
        key_points=[
            "Authenticator apps (TOTP) are more secure than SMS but require setup",
            "SMS codes are convenient but vulnerable to SIM swapping and interception",
            "Hardware tokens (FIDO2, U2F) provide the strongest security against phishing",
            "Always save backup codes in a secure location when enabling 2FA",
            "Never approve unexpected 2FA prompts—your password may have been compromised",
        ],
        examples=[
            "Strongest: Hardware key (YubiKey) - Can't be phished or compromised remotely",
            "Very strong: Authenticator app on protected phone",
            "Good: SMS codes (still better than password alone)",
            "Weak: Security questions alone - Answers are often guessable",
        ],
    ),
    LearningModule(
        title="Device Hardening Techniques",
        category="Device Management",
        content=[
            "Device hardening involves configuring systems to be as secure as possible by reducing attack surface and enabling protections.",
            "Security features like firewalls, antivirus, and encryption should be enabled by default.",
            "Regular maintenance including updates, backups, and access reviews keeps devices secure.",
        ],
        key_points=[
            "Enable and configure firewall protection (Windows Defender Firewall or equivalent)",
            "Keep antivirus software current and enable real-time protection",
            "Enable full disk encryption (BitLocker on Windows, FileVault on Mac)",
            "Disable unnecessary services and features that aren't used",
            "Regularly audit and remove unused software and user accounts",
        ],
        examples=[
            "Hardened: Firewall enabled, Defender active, BitLocker on, auto-updates enabled",
            "Vulnerable: All services enabled, no encryption, antivirus disabled",
            "Best practice: Annual security review and cleanup of unused accounts",
            "Risky: Giving multiple users local admin access to 'make things easier'",
        ],
    ),
    LearningModule(
        title="Scam Prevention and Detection",
        category="Social Engineering",
        content=[
            "Scams take many forms: advance-fee frauds, romance scams, lottery frauds, and tech support scams.",
            "Scammers use psychology and urgency to overcome critical thinking and prevent verification.",
            "Most scams follow predictable patterns that can be identified with awareness.",
        ],
        key_points=[
            "If unsolicited offer sounds too good to be true, it definitely is",
            "Legitimate organizations don't request payment or personal information via unsolicited contact",
            "Never send money to people or organizations you haven't verified",
            "Be especially wary of requests for gift cards, wire transfers, or cryptocurrency",
            "Verify through independent contact—call the organization directly using official phone numbers",
        ],
        examples=[
            "Lottery scam: 'You won a prize! Send $500 processing fee' - Real lotteries don't work this way",
            "Romance scam: Online person rapidly builds relationship, then requests money for emergency",
            "Tech support scam: Pop-up claims device is infected, directs you to call number",
            "Advance-fee fraud: Nigerian prince needs to move money, you'll get cut for helping",
        ],
    ),
    LearningModule(
        title="Secure Link Identification",
        category="Web Security",
        content=[
            "Malicious links can appear legitimate but lead to phishing pages, malware, or credential harvesting sites.",
            "URL structure, website appearance, and sender context all contribute to determining link safety.",
            "Shortened URLs and redirects hide the actual destination, making them inherently risky.",
        ],
        key_points=[
            "Hover over links to preview the actual URL before clicking",
            "Shortened URLs (bit.ly, tinyurl) hide destination—verify source before clicking",
            "Check for HTTPS (padlock icon) when entering any sensitive information",
            "Verify links match expected destinations (e.g., bank website links should go to bank domain)",
            "Be suspicious of links in unexpected emails, even from known senders whose accounts may be compromised",
        ],
        examples=[
            "Safe: https://www.mybank.com/login with padlock icon",
            "Unsafe: http://mybank.co.uk/login - wrong domain and no HTTPS",
            "Red flag: bit.ly/xyz123 - destination unknown",
            "Dangerous: Email from friend with unusual subject and link - account may be compromised",
        ],
    ),
    LearningModule(
        title="Mobile Security Essentials",
        category="Device Management",
        content=[
            "Mobile devices are increasingly targeted by attackers due to personal data and financial access they contain.",
            "Mobile security requires different approaches than desktop security due to app-based architecture.",
            "Users have less visibility into what permissions apps request and what they access.",
        ],
        key_points=[
            "Only download apps from official app stores (Apple App Store, Google Play)",
            "Review app permissions before installing—apps should only request necessary permissions",
            "Keep mobile OS and apps updated—most vulnerabilities are patched with updates",
            "Enable lock screen with strong PIN or biometric authentication",
            "Enable Find My Device/Family Link to track stolen phones",
        ],
        examples=[
            "Risky: Downloading app from third-party website—may contain malware",
            "Safe: Downloading from official app store with reviews and developer verification",
            "Dangerous: App requests camera and location for a simple note-taking app",
            "Good: App requests only permissions needed for its function",
        ],
    ),
    LearningModule(
        title="Data Protection and Privacy",
        category="Data Security",
        content=[
            "Data protection involves safeguarding personal and sensitive information from unauthorized access, use, or disclosure.",
            "Data minimization means collecting and storing only the data you actually need.",
            "Encryption protects data confidentiality even if storage devices are compromised.",
        ],
        key_points=[
            "Use encryption for sensitive files and communications",
            "Minimize collection and retention of personal information",
            "Use strong access controls to limit who can access sensitive data",
            "Securely delete data when no longer needed (not just empty trash)",
            "Be aware of privacy policies on services you use",
        ],
        examples=[
            "Good: Encrypt financial documents and keep only required files",
            "Bad: Storing sensitive data in plain text on shared drives",
            "Good: Using end-to-end encrypted messaging for sensitive conversations",
            "Bad: Sending passwords or financial info via unencrypted email",
        ],
    ),
    LearningModule(
        title="Incident Response and Reporting",
        category="Security Incident",
        content=[
            "When security incidents occur, proper response and reporting can minimize damage and prevent future incidents.",
            "Most organizations have incident response procedures—knowing and following them is crucial.",
            "Early reporting enables faster response and containment of security issues.",
        ],
        key_points=[
            "Report security incidents immediately to your IT/Security team",
            "Document what happened: when, how, and what you did",
            "Don't attempt to investigate or fix security incidents yourself—let professionals handle it",
            "If you fall for phishing, report it immediately so others can be warned",
            "Follow your organization's incident response procedures",
        ],
        examples=[
            "Good: Immediately report suspicious email to security team",
            "Bad: Trying to investigate phishing link yourself",
            "Good: Reporting lost/stolen device immediately",
            "Bad: Hoping device isn't used—immediately reporting enables remote wipe",
        ],
    ),
]


# --- Inbox Investigator (interactive email simulator) ---
@dataclass
class EmailItem:
    sender: str
    subject: str
    preview: str
    body: str
    link_text: str
    link_url: str
    is_phish: bool
    red_flags: List[str]
    explanation: str


INBOX_ITEMS: List[EmailItem] = [
    EmailItem(
        sender="IT Support <support@secure-pass-reset.com>",
        subject="URGENT: Password reset required",
        preview="Your password is expiring today. Reset now to avoid lockout...",
        body="We detected suspicious activity. Reset immediately using the link below.",
        link_text="Reset Password",
        link_url="https://secure-pass-reset.com/company",
        is_phish=True,
        red_flags=[
            "Third-party domain not owned by company",
            "Urgent tone",
            "Unsolicited password reset",
        ],
        explanation="Always navigate to the official portal; don't click unsolicited reset links.",
    ),
    EmailItem(
        sender="HR <hr@company.example>",
        subject="Benefits enrollment window",
        preview="Open enrollment begins next week. Review your options...",
        body="Hello, this is your annual reminder to review benefits options.",
        link_text="Open HR Portal",
        link_url="https://hr.company.example/enroll",
        is_phish=False,
        red_flags=[],
        explanation="Legitimate internal domain and expected seasonal message.",
    ),
    EmailItem(
        sender="Delivery <notice@ship-verify.co>",
        subject="Package on hold: address needed",
        preview="We couldn't deliver your package. Provide your address to release...",
        body="Confirm your address and payment to release your shipment.",
        link_text="Release Package",
        link_url="http://ship-verify.co/track/8472",
        is_phish=True,
        red_flags=[
            "Requests payment info",
            "Non-HTTPS or mixed content",
            "Unknown courier domain",
        ],
        explanation="Common scam to harvest personal/payment data.",
    ),
]


def _new_inbox_state(num_items: int = 5) -> Dict[str, Any]:
    population = INBOX_ITEMS.copy()
    random.shuffle(population)
    items = population[: min(num_items, len(population))]
    return {
        "indices": [INBOX_ITEMS.index(x) for x in items],
        "current": 0,
        "score": 0,
        "actions": [],  # list of dicts: {idx, action, correct}
    }


@app.route("/inbox", methods=["GET", "POST"]) 
def inbox():
    if request.method == "POST":
        session["inbox"] = _new_inbox_state()
        return redirect(url_for("inbox_play"))
    return render_template("inbox_index.html")


@app.route("/inbox/play")
def inbox_play():
    state = session.get("inbox")
    if not state:
        return redirect(url_for("inbox"))
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("inbox_result"))
    idx = state["indices"][state["current"]]
    email = INBOX_ITEMS[idx]
    return render_template(
        "inbox_play.html",
        email=email,
        number=state["current"] + 1,
        total=len(state["indices"]),
    )


@app.route("/inbox/action", methods=["POST"]) 
def inbox_action():
    state = session.get("inbox")
    if not state:
        return redirect(url_for("inbox"))
    action = request.form.get("action")  # 'report' | 'open' | 'delete'
    idx = state["indices"][state["current"]]
    email = INBOX_ITEMS[idx]

    # Scoring logic: report is correct for phish; open is correct for legit; delete counts as safe neutral for phish, incorrect for legit
    correct = False
    if action == "report":
        correct = email.is_phish
    elif action == "open":
        correct = not email.is_phish
    elif action == "delete":
        correct = email.is_phish  # deleting a phish is safe; deleting legit is wrong

    if correct:
        state["score"] += 1
    else:
        state["score"] -= 1

    state["actions"].append({"idx": idx, "action": action, "correct": correct})
    state["current"] += 1
    session["inbox"] = state
    if state["current"] >= len(state["indices"]):
        return redirect(url_for("inbox_result"))
    return redirect(url_for("inbox_play"))


@app.route("/inbox/result")
def inbox_result():
    state = session.get("inbox")
    if not state:
        return redirect(url_for("inbox"))
    details = []
    for entry in state["actions"]:
        e = INBOX_ITEMS[entry["idx"]]
        details.append({
            "sender": e.sender,
            "subject": e.subject,
            "preview": e.preview,
            "body": e.body,
            "link_text": e.link_text,
            "link_url": e.link_url,
            "is_phish": e.is_phish,
            "red_flags": e.red_flags,
            "explanation": e.explanation,
            "action": entry["action"],
            "correct": entry["correct"],
        })
    return render_template("inbox_result.html", score=state["score"], total=len(state["indices"]), details=details)


@app.route("/cyber-landing")
def cyber_landing():
    return render_template("cyber_landing.html")


@app.route("/cyber-leaderboard")
def cyber_leaderboard():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("cyber_leaderboard.html")


@app.route("/cyber-dashboard")
def cyber_dashboard():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("cyber_dashboard.html")


@app.route("/cyber-login")
def cyber_login():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("cyber_login.html")


@app.route("/cyber-signup")
def cyber_signup():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("cyber_signup.html")


@app.route("/cyber-profile")
def cyber_profile():
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("cyber_profile.html")


@app.route("/dashboard")
def dashboard():
    """User learning dashboard with stats and recommendations"""
    # Don't allow admin users to access this route
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("recommendations.html")


# --- Chatbot API ---
CHATBOT_SYSTEM_PROMPT = """You are CyberSecure Quest Assistant, a helpful AI tutor specializing in cybersecurity awareness training. 

Your role is to:
1. Help users understand cybersecurity concepts and best practices
2. Explain game scenarios and questions in detail
3. Provide guidance on identifying phishing, scams, weak passwords, and other threats
4. Answer questions about the platform and games
5. Offer security tips and recommendations
6. Be encouraging and supportive while teaching

When users ask about specific game content:
- Explain the security concepts behind the correct answer
- Help them understand why certain choices are better than others
- Provide real-world examples and context
- Explain common attack methods and defense strategies

Keep responses clear, concise, and educational. Use simple language while maintaining accuracy. 
Emphasize practical security practices users can apply immediately.
Maintain a friendly, approachable tone while being authoritative on cybersecurity topics."""


# Rule-based chatbot responses (no API key needed)
CHATBOT_RESPONSES = {
    "phishing": [
        "Phishing attacks trick users into revealing sensitive information. Always verify sender addresses and hover over links to check URLs before clicking. Be suspicious of urgent requests for passwords or personal data.",
        "Never click links in unsolicited emails. Phishers often impersonate legitimate companies. When in doubt, go directly to the official website rather than using email links.",
        "Check for red flags like generic greetings, grammar errors, suspicious sender addresses, and requests for urgent action. These are common phishing indicators."
    ],
    "password": [
        "Strong passwords should be at least 12 characters long, include uppercase/lowercase letters, numbers, and special characters. Avoid common words and personal information.",
        "Use a password manager to generate and store unique passwords for each service. Never reuse passwords across different accounts.",
        "The best password strategies combine length and complexity. Phrases are often stronger than random characters—'CorrectHorseBatteryStaple#92' is stronger than 'P@ssw0rd!'."
    ],
    "2fa": [
        "Two-factor authentication (2FA) adds a second layer of security beyond passwords. Even if your password is compromised, attackers can't access your account without the second factor.",
        "Common 2FA methods include authenticator apps, SMS codes, security keys, and biometric authentication. Authenticator apps are generally more secure than SMS.",
        "Enable 2FA on all important accounts: email, banking, social media, and work accounts. It significantly reduces the risk of unauthorized access."
    ],
    "malware": [
        "Malware is malicious software that can steal data, encrypt files, or damage your system. Only download software from official sources and keep your antivirus updated.",
        "Be cautious with email attachments, especially from unknown senders. Never execute files unless you're sure they're legitimate.",
        "Regular backups help protect against ransomware. Keep your operating system and software patched with the latest security updates."
    ],
    "social engineering": [
        "Social engineering manipulates people into divulging confidential information. Stay skeptical of unexpected requests, especially ones creating urgency or pressure.",
        "Be wary of pretexting (false pretenses), baiting (offering something enticing), and tailgating (following someone into restricted areas).",
        "When in doubt, verify requests through official channels before providing sensitive information."
    ],
    "secure browsing": [
        "Look for 'https://' and a padlock icon when visiting websites that handle sensitive data. This indicates an encrypted connection.",
        "Avoid public WiFi for sensitive transactions. Use a VPN if you must access sensitive accounts on public networks.",
        "Keep your browser and extensions updated. Disable plugins you don't use regularly."
    ],
    "game": [
        "We have 8 exciting cybersecurity games: Phishing Awareness, Choose 2FA, Device Defender, Inbox Detective, Safe to Click, Spot the Scam, Password Ninja, and Phish Hunter. Each teaches important security concepts!",
        "Try playing the games to learn cybersecurity skills in an interactive way. Each game focuses on different security threats and defenses."
    ],
    "help": [
        "I can help with questions about phishing, passwords, 2FA, malware, social engineering, secure browsing, and our games. What would you like to learn about?",
        "Ask me about cybersecurity topics, game explanations, or security best practices!"
    ],
    "hello": [
        "Hi there! 👋 I'm your CyberSecure Quest Assistant. How can I help you today?",
        "Hello! What cybersecurity topic would you like to learn about?"
    ],
    "default": [
        "That's a great question! I can help with cybersecurity concepts, game strategies, and security best practices. Feel free to ask about phishing, passwords, 2FA, malware, social engineering, or our games.",
        "I'm here to help with cybersecurity questions. Try asking about phishing, password security, 2FA, malware, or our games!"
    ]
}


def _get_chatbot_response(user_message: str) -> str:
    """Generate a response using rule-based logic without API key"""
    message_lower = user_message.lower()
    
    # Check for keywords and return relevant response
    for keyword, responses in CHATBOT_RESPONSES.items():
        if keyword != "default" and keyword in message_lower:
            return random.choice(responses)
    
    # Default response if no keywords match
    return random.choice(CHATBOT_RESPONSES["default"])


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chatbot messages without API key"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        # Get conversation history from session
        if "chat_history" not in session:
            session["chat_history"] = []
        
        chat_history = session["chat_history"]
        
        # Add user message to history
        chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep only last 20 messages
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        # Generate response using rule-based logic
        assistant_message = _get_chatbot_response(user_message)
        
        # Add assistant response to history
        chat_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        session["chat_history"] = chat_history
        
        return jsonify({"response": assistant_message}), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "response": "Sorry, I encountered an error. Please try again."}), 200


@app.route("/api/chat/reset", methods=["POST"])
def reset_chat():
    """Reset chat history"""
    session.pop("chat_history", None)
    return jsonify({"status": "Chat history cleared"}), 200


# --- Stats and Recommendations API ---
@app.route("/api/user-stats", methods=["GET"])
def get_user_stats():
    """Get user performance statistics"""
    stats = _get_user_stats(session)
    return jsonify(stats), 200


@app.route("/api/recommendations", methods=["GET"])
def get_recommendations_api():
    """Get personalized learning recommendations"""
    recommendations = _get_recommendations(session)
    return jsonify({"recommendations": recommendations}), 200


@app.route("/api/next-difficulty", methods=["GET"])
def get_next_difficulty():
    """Get recommended difficulty for next game"""
    stats = _get_user_stats(session)
    if stats["overall_total"] == 0:
        difficulty = "medium"
    else:
        overall_percentage = round((stats["overall_score"] / stats["overall_total"]) * 100, 1)
        difficulty = _get_difficulty_level(overall_percentage)
    
    return jsonify({
        "difficulty": difficulty,
        "overall_score": stats["overall_score"],
        "overall_total": stats["overall_total"],
        "percentage": round((stats["overall_score"] / stats["overall_total"]) * 100, 1) if stats["overall_total"] > 0 else 0,
    }), 200


# Admin authentication
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin@2026")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials"), 401
    
    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    # Collect platform statistics
    total_games = sum(1 for game in ["phishing", "choose_2fa", "device_defender", "inbox", "safe_to_click", "spot_the_scam", "password_ninja", "phish_hunter"])
    
    return render_template("admin_dashboard.html", total_games=total_games)


@app.route("/admin/users")
def admin_users():
    """Get list of users with their rank and badges"""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    # In a real application, this would fetch from database
    # For now, we'll demonstrate with mock data structure
    return render_template("admin_users.html")


@app.route("/api/admin/users")
def api_admin_users():
    """API endpoint to get users data"""
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Mock users data - in production, fetch from database
    users = [
        {
            "id": 1,
            "username": "cybersecurity_pro",
            "email": "user1@example.com",
            "rank": "Gold",
            "xp": 8500,
            "badges": ["Phishing Master", "Password Expert", "Security Guardian"],
            "games_played": 45,
            "privilege": "user"
        },
        {
            "id": 2,
            "username": "security_learner",
            "email": "user2@example.com",
            "rank": "Silver",
            "xp": 5200,
            "badges": ["Quick Learner", "Consistent Performer"],
            "games_played": 28,
            "privilege": "user"
        },
        {
            "id": 3,
            "username": "phishing_hunter",
            "email": "user3@example.com",
            "rank": "Platinum",
            "xp": 12000,
            "badges": ["Phishing Master", "Perfect Streak", "Top Scorer", "Dedicated Player"],
            "games_played": 87,
            "privilege": "user"
        },
        {
            "id": 4,
            "username": "newbie_secure",
            "email": "user4@example.com",
            "rank": "Bronze",
            "xp": 1500,
            "badges": ["First Steps"],
            "games_played": 5,
            "privilege": "user"
        },
        {
            "id": 5,
            "username": "admin_helper",
            "email": "user5@example.com",
            "rank": "Platinum",
            "xp": 15000,
            "badges": ["Phishing Master", "Password Expert", "Security Guardian", "Top Scorer"],
            "games_played": 120,
            "privilege": "moderator"
        },
    ]
    return jsonify(users)


@app.route("/api/admin/user/<int:user_id>/privilege", methods=["PUT"])
def update_user_privilege(user_id):
    """Update user privilege level"""
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    privilege = data.get("privilege")
    
    if privilege not in ["user", "moderator", "banned"]:
        return jsonify({"error": "Invalid privilege level"}), 400
    
    # In production, update database here
    return jsonify({
        "success": True,
        "message": f"User {user_id} privilege updated to {privilege}",
        "user_id": user_id,
        "privilege": privilege
    })


@app.route("/api/admin/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete or ban a user"""
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    # In production, delete/ban user in database
    return jsonify({
        "success": True,
        "message": f"User {user_id} has been removed",
        "user_id": user_id
    })


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# --- Database Initialization ---
def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)


