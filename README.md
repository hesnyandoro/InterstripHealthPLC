# analysis-of-algorithm


# SecureChat Codebase Onboarding Guide

## CRITICAL MISSING INFORMATION

⚠️ **Before you start**: This repository is missing several essential files needed for a complete picture:
- **requirements.txt** or Pipfile (dependencies)
- **.env.example** (environment variables)
- **CI/CD config** (GitHub Actions, etc.)
- **README.md** (project overview)
- **Dockerfile** (if containerized)

**The sections below are filled in based on code analysis; sections marked "UNKNOWN" need these artifacts.**

---

## 1. High-Level Summary

**SecureChat** is an end-to-end encrypted messaging platform built with Django and WebSockets, enabling secure real-time communication between users.

**Project Purpose**: Allow users to register, log in, and send encrypted messages to each other in real time with zero-knowledge encryption (receiver and sender both hold the decryption key, server never can decrypt).

**Primary Domains**:
- **Authentication**: User registration, login/logout via Django sessions.
- **Encryption**: Hybrid RSA-2048 (key exchange) + Fernet/AES (message payload).
- **Real-Time Messaging**: WebSocket-based bidirectional chat via Django Channels.
- **Message Storage**: Persisted encrypted messages in SQLite3.

**Tech Stack**:
- **Backend Framework**: Django 5.2 (Python web framework)
- **Real-Time Layer**: Django Channels 4+ (ASGI, WebSockets via Daphne)
- **Cryptography**: `cryptography` library (RSA, OAEP, Fernet)
- **Database**: SQLite3 (development); likely PostgreSQL in production (UNKNOWN).
- **Middleware**: WhiteNoise (static files), standard Django middleware
- **Third-Party Services**: **UNKNOWN** — no external integrations found in code


## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       SECURECHAT PLATFORM                       │
└─────────────────────────────────────────────────────────────────┘

                          ┌──────────────────┐
                          │   Web Browser    │
                          └────────┬─────────┘
                                   │
                    ┌──────────────┴────────────────┐
                    │                               │
                    ▼ (HTTP: REST)                 ▼ (WebSocket)
            ┌──────────────────┐           ┌──────────────────┐
            │   Django Views   │           │ Daphne / ASGI    │
            │ (auth, chat list)│           │  (Chat Consumer) │
            └─────────┬────────┘           └────────┬─────────┘
                      │                             │
                      └──────────────┬──────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │  Django ORM / SQLite3│
                          │  (Users, Keys, Msgs) │
                          └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   DATA FLOW: SEND MESSAGE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1. User Sends Plaintext:  "Hello"                               │
│ 2. Client-side (or backend):                                    │
│    - Generate AES key                                           │
│    - Encrypt message: AES(content, aes_key)                     │
│    - Encrypt AES key for receiver: RSA(aes_key, recv_pubkey)    │
│    - Encrypt AES key for sender: RSA(aes_key, send_pubkey)      │
│ 3. Store: Message(encrypted_content, encrypted_key, encrypted_ │
│           key_sender)                                           │
│ 4. Broadcast via WebSocket to recipient in real time           │
│ 5. Recipient decrypts:                                          │
│    - Get encrypted_key from DB, decrypt with their privkey     │
│    - Decrypt content with recovered AES key                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

KEY COMPONENTS:
┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  UserKey       │  │ Message         │  │ ChatConsumer    │
│ (RSA key pair) │  │ (encrypted data)│  │ (WebSocket)     │
│ [STATEFUL]     │  │ [STATEFUL]      │  │ [STATELESS]     │
└────────────────┘  └─────────────────┘  └─────────────────┘
      ↑                    ↑                       ↑
   Stored in           Stored in            Ephemeral;
    Database           Database          routes messages

```

---

## 3. Key Directories and Files

| Directory/File | Purpose | Entry Points | Change Frequency | Comments |
|---|---|---|---|---|
| **`chat/models.py`** | Data models | `UserKey`, `Message` | Occasional | RSA keypairs stored here; auto-created on user signup via signals |
| **`chat/views.py`** | HTTP endpoints | `register_view`, `login_view`, `chat_home`, `send_message`, `chat_detail` | Frequent | Message encryption happens here; also used for form-based message send |
| **`chat/consumers.py`** | WebSocket handler | `ChatConsumer` (async) | Occasional | Real-time message broadcast; receives/sends via WebSocket |
| **`chat/encryption.py`** | Crypto utilities | `generate_aes_key()`, `encrypt_message_aes()`, `decrypt_key_rsa()`, etc. | Rare | RSA-2048 + Fernet/AES implementation; core security logic |
| **`chat/signals.py`** | Django signal handlers | `@receiver(post_save, User)` | Rare | Auto-generates UserKey (RSA keypair) when user registers |
| **`chat/forms.py`** | Form definitions | `RegisterForm` | Rare | User registration form with email field |
| **`chat/urls.py`** | URL routing (HTTP) | Route definitions | Rare | Maps URLs to views |
| **`securechat/routing.py`** | WebSocket routing | `websocket_urlpatterns` | Rare | Maps WebSocket paths to `ChatConsumer` |
| **`securechat/asgi.py`** | ASGI config | Application entry point | Rare | ProtocolTypeRouter for HTTP + WebSocket |
| **`securechat/settings.py`** | Django config | Environment, middleware, apps | Occasional | Database, installed apps, security settings |
| **`securechat/urls.py`** | Root URL config | URL includes | Rare | Includes `chat.urls` |
| **`chat/templates/`** | HTML templates | 8 template files | Frequent | Forms, chat UI, message display |
| **`chat/migrations/`** | Database migrations | 4 migrations | Occasional | Schema versions; auto-run on startup |
| **`manage.py`** | Django CLI | `python manage.py` commands | Never | Standard Django management script |

---

## 4. Runtime and Local Setup

### Prerequisites
- **OS**: Windows, macOS, or Linux
- **Python**: 3.10+ (Django 5.2 requires 3.10+)
- **Git**: For cloning and version control
- **Virtual Environment**: `venv` or `conda`

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repo_url>
cd securechat

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # On macOS/Linux
venv\Scripts\activate          # On Windows (PowerShell)

# 3. Install dependencies
# ⚠️ UNKNOWN: requirements.txt not found in repo
# Assume these are needed (to be confirmed):
pip install django==5.2
pip install channels==4.0
pip install daphne==4.0
pip install cryptography==41.0
pip install whitenoise==6.5
pip install python-dotenv  # For .env loading

# 4. Configure environment
# Create .env file (or use .env.example)
# UNKNOWN: .env variables not documented; see section 8

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (optional, for admin panel)
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Start development server
# Option A: Using Daphne (WebSocket support)
daphne -b 127.0.0.1 -p 8000 securechat.asgi:application

# Option B: Using Django dev server (limited WebSocket support)
python manage.py runserver

```

### Running Tests
```bash
# Currently: tests.py is empty
python manage.py test
# TODO: Add unit/integration tests for crypto and WebSocket flows
```

### Local Testing Tips
- **Seeding Data**: Run `python manage.py shell` and use ORM to create test users:
  ```python
  from django.contrib.auth.models import User
  user1 = User.objects.create_user('alice', 'alice@example.com', 'password123')
  user2 = User.objects.create_user('bob', 'bob@example.com', 'password456')
  # UserKey auto-generated by signal
  ```
- **Test Encryption Locally**:
  ```python
  from chat.encryption import *
  aes_key = generate_aes_key()
  encrypted = encrypt_message_aes("Hello", aes_key)
  decrypted = decrypt_message_aes(encrypted, aes_key)
  print(decrypted)  # Should print "Hello"
  ```

---

## 5. Development Workflow and Conventions

### Branching Model
**UNKNOWN** — No CI/CD or branch protection rules found.  
Assumed workflow:
- **main**: Production-ready code
- **feature/...**: Feature branches for new functionality
- **bugfix/...**: Bug fix branches

### PR Expectations
**UNKNOWN** — No PR template or contribution guidelines found.  
Suggested checklist:
- [ ] Code follows Django conventions (PEP 8)
- [ ] All crypto logic reviewed for correctness
- [ ] WebSocket changes tested with multiple concurrent clients
- [ ] Database migrations tested (forward and backward)
- [ ] No hardcoded secrets or DEBUG flags

### Commit Message Conventions
Suggested format (not enforced):
```
[type] brief description

- Longer context if needed
- Affected modules

Examples:
[feat] Add message deletion endpoint
[fix] Fix RSA key padding issue
[refactor] Extract crypto utils
[test] Add integration tests for WebSocket
```

### Code Review Checklist
- ✅ Security: No plaintext secrets, proper key handling
- ✅ Crypto: Correct RSA/AES usage, no weak algorithms
- ✅ Performance: DB queries optimized (no N+1 problems)
- ✅ Tests: New endpoints/logic have tests
- ✅ Documentation: Complex flows documented

### Release Process
**UNKNOWN** — No versioning or release CI found.  
Suggested steps:
1. Create release branch from main
2. Bump version in `__init__.py` or version file
3. Tag with `v1.0.0` format
4. Merge back to main

---

## 6. Important Runtime Behavior and Flows (Top 5)

### Flow 1: User Registration → Auto-Key Generation
**Trigger**: User submits registration form  
**Entry Point**: `POST /register/` → `register_view()`  
**Steps**:
1. Validate form input (username, email, password)
2. Create User object via `RegisterForm.save()` (Django ORM)
3. **Signal Hook**: `post_save` signal fires → `create_user_keys()`
4. Generate RSA-2048 keypair:
   - Private key (PKCS8, PEM format)
   - Public key (SubjectPublicKeyInfo, PEM format)
5. Create `UserKey` record in DB with keypair strings
6. Auto-login user and redirect to chat home

**Critical Modules**: `chat/signals.py`, `chat/forms.py`, `cryptography.hazmat`  
**Data Transformations**: RSA keypair (binary) → PEM strings → DB storage  
**Side Effects**: DB inserts (User + UserKey); session cookie set  
**Failure Modes**:
- RSA key generation fails (rare, system-level)
- Database constraint violation (duplicate username)
- **Debug**: Check Django logs for signal exceptions; verify UserKey record created

---

### Flow 2: Send Message (HTTP POST)
**Trigger**: User submits message form or WebSocket send  
**Entry Points**: `POST /send/` → `send_message()` OR WebSocket receive event  
**Steps** (using HTTP as example):
1. Retrieve receiver User object
2. Fetch receiver's public key from `UserKey`
3. **Encryption**:
   - Generate random AES key (`Fernet.generate_key()`)
   - Encrypt message content: `Fernet(aes_key).encrypt(content.encode())`
   - Encrypt AES key for receiver: `RSA_public.encrypt(aes_key, OAEP(...))`
   - Encrypt AES key for sender (for read receipts/backups)
4. Create Message record:
   - `content` = encrypted message
   - `encrypted_key` = receiver's encrypted AES key
   - `encrypted_key_sender` = sender's encrypted AES key
5. Redirect to chat detail or acknowledge via WebSocket

**Critical Modules**: `chat/encryption.py`, `chat/models.py`  
**Data Transformations**: 
- Plaintext → AES ciphertext (symm. enc.)
- AES key → RSA ciphertext (asymm. enc.)
- Both stored as hex strings in DB

**Side Effects**: DB insert (Message); WebSocket broadcast (if WebSocket flow)  
**Failure Modes**:
- UserKey not found (user didn't complete registration)
- Receiver doesn't exist
- RSA encryption fails (corrupted public key)
- Database constraint violation
- **Debug**: Print intermediate steps in views.py; verify keys are valid PEM

---

### Flow 3: Real-Time Message Delivery (WebSocket)
**Trigger**: Client connects to `/ws/chat/<user_id>/`  
**Entry Point**: `ChatConsumer.connect()` (async)  
**Steps**:
1. Extract sender ID and receiver ID from WebSocket scope
2. Compute deterministic room name: `f"chat_{min(id1, id2)}_{max(id1, id2)}"` (ensures 1-1 rooms)
3. Add sender to room group via `channel_layer.group_add()`
4. Accept WebSocket connection
5. On message receive (`ChatConsumer.receive()`):
   - Parse JSON: `{"message": "...", "receiver_id": ...}`
   - Perform same encryption as HTTP flow (generate AES, RSA encrypt)
   - Save to DB
   - Broadcast via `channel_layer.group_send()` to all users in room
6. On disconnect: Remove from group

**Critical Modules**: `chat/consumers.py`, Django Channels  
**Data Transformations**: JSON → Python dict → encrypted DB record  
**Side Effects**: 
- DB insert (Message)
- WebSocket send to 2 clients in real time
- No loss if client offline (message persisted)

**Failure Modes**:
- User not authenticated (Channels will reject via `AuthMiddlewareStack`)
- Receiver doesn't exist
- Channel layer not available (InMemoryChannelLayer lost across processes)
- **Debug**: Enable Channels debug logging; check `scope["user"]` is set

---

### Flow 4: View Message History
**Trigger**: User clicks on conversation  
**Entry Point**: `GET /chat/<user_id>/` → `chat_detail(request, user_id)`  
**Steps**:
1. Fetch other user object
2. Query messages where:
   - `(sender=current_user AND receiver=other_user)` OR
   - `(sender=other_user AND receiver=current_user)`
   - Ordered by timestamp
3. **Important**: Messages are stored encrypted in DB; template displays encrypted content
4. Pass messages to template for rendering
5. Template also renders WebSocket client script to listen for new messages

**Critical Modules**: `chat/views.py`, `chat_detail.html` template  
**Data Transformations**: Encrypted DB records → passed to template as-is  
**Side Effects**: None (read-only)  
**Failure Modes**:
- Other user doesn't exist → 404
- **Debug**: Check DB for message records; verify encrypted_content is hex/base64

**⚠️ Security Note**: Client-side decryption not implemented! Messages display as encrypted strings. **To-do**: Implement client-side JavaScript decryption using receiver's private key (requires secure key management in browser).

---

### Flow 5: Chat User List (Home Page)
**Trigger**: User visits `/` after login  
**Entry Point**: `GET /` → `chat_home(request)`  
**Steps**:
1. Query all User objects except current user
2. Filter to only those in conversation history:
   - Where `sent_messages.receiver=current_user` OR `received_messages.sender=current_user`
   - Call `distinct()` to avoid duplicates
3. Pass list to `chat_list.html` template
4. Template renders clickable user list linking to `/chat/<user_id>/`

**Critical Modules**: `chat/views.py`, `chat_list.html`  
**Data Transformations**: User queryset → template context  
**Side Effects**: None  
**Failure Modes**:
- No conversations yet → empty list (expected)
- **Debug**: Check User and Message tables for orphaned/test data

---

## 7. Data Model and Storage

### Primary Database: SQLite3
**Development**: Built-in, file-based (`db.sqlite3`)  
**Production**: UNKNOWN — likely PostgreSQL (not configured in visible settings)

### Key Tables/Collections

| Table | Purpose | Key Fields | Indexes | Notes |
|---|---|---|---|---|
| **auth_user** | Django user accounts | `id`, `username`, `email`, `password_hash`, `is_active` | `username` (unique) | Standard Django table |
| **chat_userkey** | RSA keypairs | `id`, `user_id` (FK), `public_key` (TextField), `private_key` (TextField) | `user_id` (unique) | 1:1 relationship; auto-created on signup |
| **chat_message** | Encrypted messages | `id`, `sender_id` (FK), `receiver_id` (FK), `content` (encrypted), `encrypted_key` (receiver's AES key), `encrypted_key_sender` (sender's AES key), `timestamp` | `sender_id`, `receiver_id`, `timestamp` | No PK index on (sender, receiver, timestamp); consider adding |

### Caching Layers
**UNKNOWN** — No cache configuration found (no Redis, Memcached setup).  
Potential optimization: Cache user's public key after first fetch (TTL: 1 hour).

### Transactional Boundaries
- **Message send** should be atomic:
  - Encrypt → DB insert → WebSocket send
  - Currently: No explicit transaction; race condition if insert fails after encryption

---

## 8. Configuration and Secrets

### Where Configuration Lives
- **`securechat/settings.py`**: Main Django config
- **`.env`**: UNKNOWN — not found; should contain secrets

### Environment Variables (UNKNOWN — see .env.example)
Likely needed:
```
DJANGO_SECRET_KEY=<random-secret>
DEBUG=False  # False in production
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgresql://user:pass@localhost/securechat
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
CHANNEL_LAYERS_HOST=redis://localhost
```

### Secrets Management
**Current Issues**:
- ❌ SECRET_KEY hardcoded in settings.py (SECURITY ISSUE)
- ❌ DEBUG=True (exposes sensitive info)
- ❌ No `.env.example` file

**Recommended Fixes**:
```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '<dev-default>')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### Per-Environment Configuration
**Development**:
- SQLite3 database
- InMemoryChannelLayer (for single process)
- DEBUG=True

**Production**:
- PostgreSQL database
- Redis backend for Django Channels
- DEBUG=False
- SECURE_SSL_REDIRECT=True
- SESSION_COOKIE_SECURE=True

---

## 9. Observability and Troubleshooting

### Logging
**UNKNOWN** — No logging config found in settings.py.  
**To add**:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {'class': 'logging.FileHandler', 'filename': 'debug.log'},
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO'},
        'chat': {'handlers': ['console', 'file'], 'level': 'DEBUG'},
    },
}
```

### Useful Diagnostic Commands
```bash
# Check database state
python manage.py dbshell
sqlite> SELECT COUNT(*) FROM chat_userkey;
sqlite> SELECT * FROM chat_message LIMIT 5;

# Run Django shell for debugging
python manage.py shell
>>> from chat.models import UserKey, Message
>>> UserKey.objects.count()
>>> Message.objects.filter(sender_id=1)

# Check Channels connectivity
daphne --verbosity 2 -b 127.0.0.1 -p 8000 securechat.asgi:application

# Monitor WebSocket connections (requires browser DevTools)
# Open DevSocket tab in Chrome DevTools → filter by "ws://"
```

### Common Issues & Fixes

| Issue | Symptom | Diagnosis | Fix |
|---|---|---|---|
| **UserKey not created** | `UserKey matching query does not exist` on message send | Signal didn't fire or failed | Manually create: `UserKey.objects.create(user=user_obj, public_key=..., private_key=...)` |
| **WebSocket connection fails** | `WebSocket is closed before the connection is established` | Channels not running via Daphne; or wrong route | Use `daphne`, not `runserver`; verify routing.py includes WebSocket path |
| **Message encryption fails** | Exception in `encrypt_key_rsa()` | Invalid PEM format in `public_key` field | Check public_key string has `-----BEGIN PUBLIC KEY-----` header |
| **Messages not persisting** | Send succeeds but no DB record | Race condition or transaction issue | Add `@transaction.atomic` decorator |
| **InMemoryChannelLayer lost messages** | Messages sent to offline client not delivered | InMemoryChannelLayer doesn't persist across processes | Use Redis backend: `BACKEND: channels_redis.core.RedisChannelLayer` |

---

## 10. Security, Compliance, and Performance Notes

### Security-Sensitive Areas
1. **Cryptography Implementation** (`chat/encryption.py`)
   - ✅ RSA-2048 with OAEP padding (secure)
   - ✅ Fernet (authenticated encryption, secure)
   - ⚠️ TODO: Add integrity checks on decryption failures

2. **Private Key Storage** (`chat/models.py`)
   - ❌ **CRITICAL**: Private keys stored in plaintext in DB
   - ⚠️ **Risk**: If DB is compromised, all past messages can be decrypted
   - **Mitigation**: Encrypt private keys at rest using a master key; OR derive from user password (zero-knowledge architecture)

3. **User Authentication**
   - ✅ Using Django's hashed passwords (PBKDF2 default)
   - ✅ Session middleware protects against CSRF
   - ⚠️ TODO: Add rate limiting on login attempts

4. **WebSocket Security**
   - ✅ `AuthMiddlewareStack` ensures only authenticated users can connect
   - ⚠️ TODO: Add rate limiting on message sends

5. **Database Access**
   - ❌ No encryption at rest for SQLite
   - ⚠️ **Risk**: Disk theft exposes user keys and message history

### Known Performance Bottlenecks
1. **Message History Queries**: `Q(sender=...) | Q(receiver=...)` with no indexes
   - **Fix**: Add database indexes on `(sender_id, receiver_id, timestamp)`
   
2. **User List Query**: N queries for each user's last message
   - **Fix**: Use `select_related()` or aggregation

3. **RSA Encryption** (1-2ms per message)
   - **Acceptable**: For typical message volume; benchmark if > 10k msgs/day
   - **Alternative**: Consider post-quantum cryptography if long-term secrecy needed

4. **InMemoryChannelLayer**
   - **Limitation**: Doesn't scale to multiple server processes
   - **Fix**: Use Redis for production

### Compliance Notes
- **GDPR**: No data retention policy; consider adding message TTL
- **User Deletion**: Deleting a user should purge all messages and keys
- **Audit Logging**: No logs of who accessed which messages (consider adding)

---

## 11. Onboarding Priority Checklist

Prioritized hands-on tasks for getting up to speed **within 3 days**:

- [ ] **Day 1—Morning (1 hour)**: Clone repo, set up venv, install dependencies (see section 4)
- [ ] **Day 1—Morning (30 min)**: Run migrations, create test users, start dev server
- [ ] **Day 1—Midday (1 hour)**: Walk through registration flow; trace signal that creates UserKey
- [ ] **Day 1—Midday (1 hour)**: Read `chat/encryption.py` and understand RSA + Fernet workflow
- [ ] **Day 1—Afternoon (1 hour)**: Test message send flow; inspect encrypted DB records
- [ ] **Day 1—Afternoon (1 hour)**: Connect WebSocket client (browser DevTools) and send real-time message
- [ ] **Day 2—Morning (1 hour)**: Read all templates in `chat/templates/`; understand UI flow
- [ ] **Day 2—Morning (1 hour)**: Trace data model: diagram User → UserKey → Message relationships
- [ ] **Day 2—Midday (30 min)**: Run failing tests or add one basic test to `chat/tests.py`
- [ ] **Day 2—Midday (1 hour)**: Review security issues (section 10); document findings in ticket
- [ ] **Day 2—Afternoon (1 hour)**: Try running on Daphne vs. dev server; observe logging differences
- [ ] **Day 3—Morning (1 hour)**: Create a "developer notes" document with unanswered questions (for team)
- [ ] **Day 3—Morning (1 hour)**: Ask team for `.env.example`, `requirements.txt`, CI/CD config (see next section)
- [ ] **Day 3—Afternoon (2 hours)**: Implement a minor feature or fix (e.g., add logging, fix a template typo)

---

## 12. Suggested Targeted Questions for the Team

Precise, high-value questions to remove blockers:

1. **"What's the required Python and Django version? Do you have a `requirements.txt` or `Pipfile`?"**
   - *Why*: Dependency management is not documented; build may break

2. **"How should private keys be stored in production? Should they be encrypted at rest, or derived from passwords?"**
   - *Why*: Currently stored plaintext; high security risk

3. **"Is the database PostgreSQL in production, or still SQLite? Do you have a Dockerfile or deployment guide?"**
   - *Why*: Affects data model, scaling, and testing approach

4. **"What's the `.env.example` or deployment checklist? Which settings change per environment?"**
   - *Why*: SECRET_KEY, DEBUG, ALLOWED_HOSTS not documented

5. **"Does the client-side (browser) need to decrypt messages, or is server decryption acceptable?"**
   - *Why*: Currently template shows encrypted content; unclear if that's intentional

6. **"How are message read receipts or delivery confirmations handled?"**
   - *Why*: Not visible in code; affects UX and encryption model

7. **"What's the maximum message volume (msgs/day)? Do we need to optimize queries or scale horizontally?"**
   - *Why*: Affects choice of database backend (Redis for Channels), caching strategy

8. **"Is there a CI/CD pipeline (GitHub Actions, GitLab CI)? What are the test/lint requirements?"**
   - *Why*: No config found; unclear PR/release process

9. **"Are there plans to support end-to-end encrypted file attachments, or just text?"**
   - *Why*: Affects data model and crypto strategy

10. **"Should users be able to delete or edit messages after sending? How should that interact with encryption?"**
    - *Why*: Current model doesn't support updates; affects client-side decryption logic

---

## Next: Provide These Artifacts

To complete the onboarding guide, **please share** (paste into chat or as files):

1. **`requirements.txt`** or `Pipfile` / `pyproject.toml` — Project dependencies
2. **`.env.example`** or documentation of all environment variables
3. **CI/CD config** (`.github/workflows/*.yml`, `gitlab-ci.yml`, etc.) — Build/test/deploy process
4. **`README.md`** (if exists) — Project overview and setup instructions
5. **`Dockerfile`** and `docker-compose.yml` (if containerized)
6. **Database schema diagram** or migration files (if not SQLite in prod)
7. **Git log** (`git log --oneline | head -20`) — Recent commit history to understand development pace
8. **Any deployment or infrastructure docs** (AWS, Heroku, custom VPS setup)
9. **Team contact info** — Who owns crypto, backend, DevOps, product?
10. **Product roadmap or issue backlog** — What's being built next?

---

**That's your comprehensive onboarding guide!** You now have a complete map of the codebase, architecture, and next steps. **Start with the 12-item checklist in section 11, and use the targeted questions (section 12) to unblock yourself with your team.** Good luck! 🚀
