# Database Implementation Documentation

## Overview
A SQLite database has been integrated into the CYBER//GUARD application to store and manage user accounts for registration and login functionality.

## Database Setup

### Installation
The required packages have been added to `requirements.txt`:
- **Flask-SQLAlchemy==3.1.1** - ORM for database management

### Database Location
- **File**: `cyberguard.db` (created in the application root directory)
- **Type**: SQLite
- **Auto-initialization**: Database tables are created automatically when the application starts

## User Model

### Fields
```python
- id (Integer, Primary Key)
- username (String, Unique) - User login name
- email (String, Unique) - User email address
- password_hash (String) - Bcrypt hashed password (never stored as plaintext)
- rank (String) - User rank: Bronze, Silver, Gold, Platinum
- xp (Integer) - Experience points
- badges (String) - JSON string of earned badges
- games_played (Integer) - Total games completed
- privilege (String) - user, moderator, or banned
- created_at (DateTime) - Account creation timestamp
- last_login (DateTime) - Last login timestamp
```

### Security Features
- **Password Hashing**: All passwords are hashed using Werkzeug's `generate_password_hash()` and checked with `check_password_hash()`
- **Never stored in plaintext**: Passwords are immediately hashed upon registration
- **Account Protection**: Banned users cannot login
- **Session Management**: User IDs and usernames stored in Flask sessions

## Authentication Routes

### `/register` (GET/POST)
- **Purpose**: User registration
- **Validation**:
  - Username: minimum 3 characters, must be unique
  - Password: minimum 6 characters
  - Passwords must match
  - Email must be unique
- **Success**: Creates user and logs them in
- **Template**: `templates/register.html`

### `/login` (GET/POST)
- **Purpose**: User login
- **Validation**:
  - Username and password required
  - Password must match stored hash
  - Account cannot be banned
- **Success**: Updates `last_login` timestamp and creates session
- **Template**: `templates/login.html`

### `/logout`
- **Purpose**: User logout
- **Action**: Clears session data

## Usage Examples

### Registering a New User
```bash
# Navigate to http://localhost:5000/register
# Fill in:
# - Username: cybersecurity_pro
# - Email: user@example.com
# - Password: SecurePass123
# - Confirm Password: SecurePass123
# Click "CREATE ACCOUNT"
```

### Logging In
```bash
# Navigate to http://localhost:5000/login
# Enter:
# - Username: cybersecurity_pro
# - Password: SecurePass123
# Click "LOGIN"
```

### Accessing User Data (Backend)
```python
# Query user by username
user = User.query.filter_by(username='cybersecurity_pro').first()

# Query user by email
user = User.query.filter_by(email='user@example.com').first()

# Query user by ID
user = User.query.get(1)

# Get all users
all_users = User.query.all()

# Convert to dictionary
user_data = user.to_dict()
```

## Protected Routes

The following routes now redirect admin users away from user areas:
- `/games` - User games listing
- `/dashboard` - User learning dashboard
- `/cyber-dashboard` - Cyber mode dashboard
- `/cyber-login` - Cyber mode login
- `/cyber-signup` - Cyber mode signup
- `/cyber-profile` - User profile
- `/cyber-leaderboard` - User leaderboard

When an admin user tries to access these, they're automatically redirected to `/admin/dashboard`.

## Database Management

### Reinitialize Database
To reset the database (useful during development):
```bash
# Delete the cyberguard.db file
rm cyberguard.db

# Restart the application
python app.py
```

### Add Test Users (Programmatically)
```python
from app import app, db, User

with app.app_context():
    # Create test user
    user = User(
        username='test_user',
        email='test@example.com',
        rank='Gold',
        xp=5000
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    print(f"User created with ID: {user.id}")
```

### Query Examples
```python
# Get total users
total_users = User.query.count()

# Get users by rank
gold_users = User.query.filter_by(rank='Gold').all()

# Get recently registered users
recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

# Get users with most XP
top_users = User.query.order_by(User.xp.desc()).limit(10).all()

# Check if username exists
username_exists = User.query.filter_by(username='test').first() is not None
```

## Admin User Management

### Viewing Users
- Navigate to: `/admin/users` (when logged in as admin)
- View all registered users with their:
  - Username, Email, Rank
  - XP and Badges
  - Games Played
  - Current Privilege Level

### Updating User Privileges
- Select a user from the table
- Change privilege level (User → Moderator → Banned)
- Changes are saved immediately

### Deleting Users
- Click "Delete" button next to a user
- User is removed from the system

## Session Management

### User Session
```python
session["user_id"]      # User's database ID
session["username"]     # User's username
```

### Admin Session
```python
session["admin"]        # True if admin is logged in
```

## Troubleshooting

### Database File Permissions
If you get permission errors:
```bash
# Windows: Restart the application (should auto-recover)
# Linux/Mac: chmod 644 cyberguard.db
```

### Password Verification Fails
- Ensure password is entered exactly (case-sensitive)
- Check that account isn't banned
- Verify username exists in database

### Users Not Persisting
- Ensure `db.session.commit()` is called after creating/updating users
- Check that database file exists in the application root directory
- Verify database is initialized by checking console output

## Future Enhancements

1. **Password Reset**: Add forgot password functionality
2. **Email Verification**: Verify email before account activation
3. **2FA**: Two-factor authentication for accounts
4. **Profile Pictures**: Store user avatars
5. **Password History**: Prevent reuse of old passwords
6. **Account Recovery**: Backup codes for account recovery
7. **Session Expiry**: Auto-logout after inactivity
8. **Audit Logging**: Track all user actions

## Security Best Practices

✅ **Implemented**:
- Password hashing with Werkzeug
- SQL injection prevention with SQLAlchemy ORM
- Session-based authentication
- Admin access restrictions
- Banned user prevention

⚠️ **Recommended for Production**:
- Use environment variables for database URI
- Enable HTTPS/SSL
- Implement CSRF protection
- Add rate limiting to login/register
- Use more secure password hashing (bcrypt, argon2)
- Add email verification
- Implement account lockout after failed login attempts
- Use database backups and replication
