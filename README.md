# MindMate - AI-Powered Mental Health & Wellness Platform

<div align="center">

![MindMate](https://img.shields.io/badge/MindMate-Mental_Health_AI-blue)
![Django](https://img.shields.io/badge/Django-5.1.2-darkgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

*A comprehensive, real-time AI-powered mental health and wellness platform with voice capabilities, interactive games, and advanced psychological assessments.*

### Platform Statistics
- **10+ Interactive Features**: Assessments, games, meditation, voice calls, and tools
- **8 Quiz Categories**: 160+ unique AI-generated questions per user
- **6 Mini-Games**: 3 traditional + 3 AI-powered games
- **4 Breathing Exercises**: Evidence-based relaxation techniques
- **3 AI Models**: Gemini 2.5 Flash, Gemini Pro, and Cloudflare AI
- **Multi-Modal Assessment**: Facial emotion + Voice sentiment + Quiz responses
- **Real-time Processing**: WebSocket + Celery for instant feedback

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Setup & Installation](#setup--installation)
- [Quick Start](#quick-start)
- [API Configuration](#api-configuration)
- [Commands Reference](#commands-reference)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Development Tips](#development-tips)
- [License](#license)

---

## 🎯 Overview

**MindMate** is an innovative, enterprise-grade mental health and wellness platform that leverages artificial intelligence to provide accessible, personalized mental health support. Built with Django 5.1, it features real-time voice interactions, AI-driven psychological assessments, an advanced gaming system with AI-powered features, meditation exercises, and comprehensive health tracking tools.

### Key Highlights:
- **🎮 10+ Interactive Features**: Quiz system, mini-games, AI-powered games, breathing exercises
- **🤖 Advanced AI Integration**: Gemini 2.5 for conversations, quiz generation, game hints, riddles, and story creation
- **📞 Voice Call System**: Scheduled wellness check-ins with sentiment analysis and transcript storage
- **📊 Comprehensive Analytics**: Multi-modal assessment combining facial emotion, voice sentiment, and quiz responses
- **💊 Healthcare Tools**: Prescription digitizer with OCR, journal with sentiment analysis
- **🏆 Gamification**: Leaderboards, achievements, streaks, and progress tracking across all features

The platform combines cutting-edge technologies including:
- **Real-time Communication**: WebSocket-based voice call system powered by Daphne and Django Channels
- **AI Intelligence**: Google Gemini 2.5 Flash & Pro for conversational AI, quiz generation, and creative content
- **Voice Integration**: Twilio for telephony and ElevenLabs for high-quality, empathetic text-to-speech
- **Asynchronous Processing**: Celery with Beat scheduler for background tasks and automated wellness calls
- **Real-time Data**: Redis for caching, session management, and WebSocket message brokering

---

## 🆕 Latest Features (February 2026)

### AI-Powered Gaming Suite
- **AI Riddle Challenge**: Infinite unique riddles with intelligent answer validation
- **AI Mystery Detective**: Interactive mystery cases with AI-powered question answering
- **AI Story Adventure**: Dynamic choose-your-own-adventure stories that adapt to choices
- **Smart Hint System**: Context-aware AI hints for Memory Match, Pattern Recognition, and Logic Puzzle games

### Meditation & Wellness
- **Breathing Exercises**: Box Breathing, 4-7-8 Method, Deep Breathing, and Guided Meditation
- **Progress Tracking**: Session history, streak management, and favorite exercise analytics
- **Mood Tracking**: Before and after meditation mood comparison

### Voice Call Enhancements
- **Call Scheduling**: Schedule AI-powered wellness check-ins at specific times
- **Sentiment Analysis**: Advanced emotional scoring and stress indicator detection  
- **Call History**: Complete transcripts with AI responses and emotional breakdowns
- **Custom Prompts**: Personalize AI conversation focus (e.g., stress management, anxiety)

### Healthcare Tools
- **Prescription Digitizer**: Scan and digitize prescriptions with AI-powered OCR
- **Smart Extraction**: Structured data extraction from prescription images and PDFs
- **Journal Sentiment**: AI-powered positive/negative sentiment scoring on journal entries

---

## ✨ Features

### 🎤 Voice-Based Interactions & Scheduling
- **Real-time voice calls** with AI mental health assistants
- **Scheduled wellness check-ins** with customizable prompts
- **Call history tracking** with full transcripts and sentiment analysis
- Twilio-powered WebRTC connectivity
- ElevenLabs text-to-speech for natural, empathetic conversations
- Speech-to-text for user input analysis
- Emotional score calculation and stress indicators detection
- Integration with PHQ-9 mental health assessment

### 🤖 AI-Powered Assessments
- **PHQ-9 Depression Screening** with multi-modal analysis
- **Facial emotion recognition** during assessments using FaceNet and FER
- **Voice sentiment analysis** with audio processing
- Google Gemini API-powered conversational assessments
- Personalized mental health scoring (0-100 scale)
- Comprehensive test result analytics with emotional breakdown
- Audio duration and sentiment tracking
- Historical assessment data with trend visualization

### 🎮 Interactive Mini Games & Activities
- **Memory Match**: Cognitive training game with 3 difficulty levels (4x4 to 8x8 grids)
- **Pattern Recognition**: Simon-says style musical pattern game
- **Logic Puzzle**: 2048-inspired sliding number puzzle
- **AI Riddle Challenge**: Infinite AI-generated riddles with smart validation
- **AI Mystery Detective**: Interactive mystery-solving with AI-generated cases
- **AI Story Adventure**: Dynamic choose-your-own-adventure stories
- Real-time score tracking and leaderboards per game/difficulty
- Progress tracking with statistics (best scores, average, total games)
- Stress-relief and cognitive wellness focus

### 🧠 AI-Enhanced Quiz System
- **8 Genre Categories**: Mental Health, Psychology, Wellness, Stress Management, Mindfulness & Meditation, Cognitive Science, Emotional Intelligence, General Knowledge
- **AI-generated quizzes** with 20 unique questions per session (Gemini 2.5 Flash)
- Advanced scoring system (Correct: +2, Wrong: -1, Skip: 0)
- Accuracy tracking and time-based performance metrics
- Detailed analytics dashboard with genre-wise breakdowns
- Genre-specific leaderboards with global rankings
- Question history tracking to prevent duplicates
- Resume incomplete quizzes

### 🧘 Meditation & Breathing Exercises
- **Box Breathing (4-4-4-4)**: Square breathing technique for anxiety relief
- **4-7-8 Breathing**: Dr. Weil's relaxation breathing method
- **Deep Breathing**: General stress reduction exercise
- **Guided Meditation**: Mindfulness meditation sessions
- Progress tracking with streak management
- Session history with mood before/after tracking
- Total minutes meditated and favorite exercise analytics
- Integration with overall wellness scoring

### 💊 Prescription Digitizer
- **Smart prescription scanning** from images or PDFs
- **AI-powered text extraction** using OCR technology
- Structured data extraction (medications, dosages, instructions)
- HTML-formatted prescription display for easy reading
- Secure storage with image/PDF backup
- Prescription history management
- Edit and delete capabilities

### 📝 Journal & Mental Health Tracking
- **AI-powered sentiment analysis** on journal entries
- Positive and negative score calculation
- Daily mood tracking and reflection
- Historical journal entries with trends
- Integration with overall mental health metrics
- Date-organized entry management

### 👥 User Management & Profiles
- Secure authentication with django-allauth
- Comprehensive user profiles with mental health history
- Phone number integration for voice call features
- Privacy-focused data storage with encryption
- HIPAA-compliant architecture design
- Profile completion tracking

### 📊 Advanced Analytics & Reporting
- **Comprehensive dashboard** with all metrics at a glance
- Mental health score trends over time
- Quiz performance analytics by genre
- Game statistics and achievements
- Meditation progress tracking
- Voice call sentiment analysis
- Journal sentiment patterns
- Prescription management overview

### 🔄 Real-time Features
- **WebSocket support** via Django Channels for live interactions
- Real-time AI chatbot with Google Gemini integration
- Live emotional feedback during assessments
- Instant notifications and alerts
- Real-time progress updates during quizzes and games
- Background task processing with Celery for scheduled calls

---

## 🛠️ Technical Stack

### Backend
- **Framework**: Django 5.1.2
- **Python**: 3.8+
- **Real-time Communication**: Django Channels 4.0.0
- **ASGI Server**: Daphne 4.0.0
- **Task Queue**: Celery 5.3.4 with Redis backend

### Frontend
- **Template Engine**: Django Templates (Jinja2)
- **UI Framework**: Bootstrap 5
- **Real-time Updates**: WebSocket connections
- **JavaScript**: Vanilla JS with WebSocket API

### External Services
- **AI/ML**: Google Generative AI (Gemini 2.5 Flash & Pro)
- **Alternative AI**: Cloudflare AI API
- **Voice**: Twilio 9.0.0 for calling and WebRTC
- **Text-to-Speech**: ElevenLabs 1.0.0 for natural voice synthesis
- **Speech-to-Text**: SpeechRecognition library with Google STT
- **OCR**: Tesseract and Google Vision API for prescription digitization

### Infrastructure
- **Cache/Message Broker**: Redis 5.0.1 for Celery and WebSocket
- **Database**: SQLite (Development), PostgreSQL (Production-ready)
- **Containerization**: Docker & Docker Compose for easy deployment
- **Tunneling**: ngrok for local development webhooks and testing
- **Task Scheduler**: Celery Beat for scheduled voice calls

### Libraries & Tools
- **Computer Vision**: OpenCV 4.x, FaceNet-PyTorch, face-recognition
- **Emotion Detection**: FER (Facial Expression Recognition)
- **Audio Processing**: FFmpeg, moviepy, librosa for audio analysis
- **Data Analysis**: Pandas, NumPy for sentiment and trend analysis
- **Machine Learning**: TensorFlow 2.17.0, PyTorch 2.2.2, scikit-learn
- **Natural Language Processing**: nltk, textblob for sentiment analysis
- **Image Processing**: Pillow (PIL) for prescription image handling

---

## 🏗️ System Architecture

```mermaid
graph TD
    User["👤 Users"] <--> UI["🌐 Django Web UI<br/>(Port: 8000)"]
    UI <--> API["🔌 Daphne ASGI Server"]
    
    subgraph Backend["Backend Services"]
        API --> Auth["🔐 Authentication"]
        API --> Core["⚙️ Core Logic Engine"]
        API --> Voice["🎤 Voice Processor"]
    end
    
    subgraph Storage["Storage Layer"]
        Core --> DB[("🗄️ PostgreSQL<br/>User Data")]
        Auth --> Cache[("⚡ Redis<br/>Cache & Broker")]
        Voice --> Media[("📁 Media Storage")]
    end
    
    subgraph External["External Services"]
        Core --> Gemini["🤖 Google Gemini API"]
        Voice --> STT["🎙️ Google Speech-to-Text"]
        Voice --> TTS["🔊 ElevenLabs TTS"]
        Auth --> Twilio["📞 Twilio Voice API"]
    end
    
    Cache --> Tasks["⏱️ Celery Task Queue"]
    Tasks --> Beat["🔄 Celery Beat Scheduler"]
```

---

## 📦 Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 14+ (optional, for frontend tools)
- **Docker**: 20.10+ (for containerized deployment)
- **Git**: Latest version

### Required Software
- PostgreSQL 12+ (for production)
- Redis 6.0+ (for caching and message broker)
- FFmpeg (for audio/video processing)

### API Keys Required
- Google Generative AI API key ([Get here](https://aistudio.google.com/apikey))
- Twilio Account SID & Auth Token ([Get here](https://www.twilio.com/console))
- ElevenLabs API Key ([Get here](https://elevenlabs.io/))
- Cloudflare API Token ([Get here](https://dash.cloudflare.com/))
- ngrok auth token for development ([Get here](https://ngrok.com/))

---

## 🔐 Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mindmate
DB_NAME=mindmate
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Google AI / Gemini
GOOGLE_API_KEY=your-google-api-key
GEMINI_API_KEY=your-gemini-api-key

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# ElevenLabs
ELEVENLABS_API_KEY=your-elevenlabs-key

# Cloudflare
CLOUDFLARE_API_TOKEN=your-cloudflare-token
CLOUDFLARE_ACCOUNT_ID=your-account-id

# ngrok (Development)
NGROK_URL=https://your-ngrok-url.ngrok.io
NGROK_AUTH_TOKEN=your-ngrok-token

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Application Settings
SITE_URL=http://localhost:8000
PROJECT_NAME=MindMate
ENVIRONMENT=development
```

---

## 🚀 Setup & Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/mindmate.git
cd mindmate
```

### Step 2: Create Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## ⚡ Quick Start

### Using PowerShell Scripts (Windows)

**Setup Environment:**
```powershell
.\setup-env.ps1
```

**Setup Voice Calls:**
```powershell
.\setup-voice-calls.ps1
```

**Start the System:**
```powershell
.\docker-quickstart.ps1
```

### Manual Startup (All Platforms)

#### Terminal 1: Start Redis
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

#### Terminal 2: Start ngrok
```bash
ngrok http 8000
# Copy the https:// URL and update NGROK_URL in .env
```

#### Terminal 3: Start Daphne Server
```bash
# Windows
.\venv\Scripts\Activate.ps1
daphne -b 0.0.0.0 -p 8000 perplex.asgi:application

# macOS/Linux
source venv/bin/activate
daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
```

#### Terminal 4: Start Celery Worker
```bash
# Windows
.\venv\Scripts\Activate.ps1
celery -A perplex worker -l info -P solo

# macOS/Linux
source venv/bin/activate
celery -A perplex worker -l info
```

#### Terminal 5: Start Celery Beat (Scheduler)
```bash
# Windows
.\venv\Scripts\Activate.ps1
celery -A perplex beat -l info

# macOS/Linux
source venv/bin/activate
celery -A perplex beat -l info
```

#### Access the Application
Once all services are running:
- **Web Application**: http://localhost:8000
- **Django Admin Panel**: http://localhost:8000/admin
- **User Dashboard**: http://localhost:8000/dashboard (after login)

### First-Time User Setup

1. **Create Account**: Navigate to http://localhost:8000 and click "Sign Up"
2. **Complete Profile**: Fill in required profile information (name, age, phone for voice features)
3. **Explore Features**:
   - **Dashboard**: View your mental health overview and quick links
   - **Take Assessment**: Start with PHQ-9 screening via webcam for emotion detection
   - **Try Games**: Visit `/games/` to explore quizzes and mini-games
   - **Chat with AI**: Use the chatbot for mental health conversations
   - **Schedule Voice Call**: Set up AI wellness check-in calls
   - **Start Meditation**: Begin breathing exercises and track progress
   - **Scan Prescriptions**: Digitize your medical prescriptions
   - **Write Journal**: Track your thoughts with AI sentiment analysis

### Feature Quick Links

After logging in, access features directly:
- **Mental Health Assessment**: `/assesment/`
- **AI Chatbot**: `/chatbot/`
- **Quiz Games**: `/games/quiz/select-genre/`
- **Mini-Games Hub**: `/games/mini-games/`
- **Schedule Voice Call**: `/voice_calls/schedule/`
- **Voice Call History**: `/voice_calls/history/`
- **Journal**: `/journal/`
- **Prescription Digitizer**: `/prescription-digitizer/`
- **Analytics Dashboard**: `/games/analytics/`
- **Leaderboards**: `/games/leaderboard/`

---

## 🔌 API Configuration

### Google Generative AI (Gemini)

1. **Get API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create a new project
   - Generate an API key
   - Add to `.env` file as `GOOGLE_API_KEY`

2. **Configuration in settings.py:**
   ```python
   GOOGLE_AI_API_KEY = os.getenv('GOOGLE_API_KEY')
   ```

### Twilio Voice Setup

1. **Create Twilio Account:**
   - Sign up at [Twilio Console](https://www.twilio.com/console)
   - Get your Account SID and Auth Token
   - Purchase a phone number or use trial number

2. **Configure Webhook:**
   - Set webhook URL in Twilio: `https://your-ngrok-url/voice_calls/incoming-call/`
   - This handles incoming calls from the platform

3. **Environment Variables:**
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### ElevenLabs Text-to-Speech

1. **Get API Key:**
   - Visit [ElevenLabs Dashboard](https://elevenlabs.io/)
   - Create account and go to API section
   - Generate API key
   - Add to `.env` file

2. **Available Voices:**
   - Can be configured in `voice_calls/services/elevenlabs_service.py`
   - Default high-quality voices available

### ngrok Setup (Development Only)

1. **Install ngrok:**
   ```bash
   # Windows
   choco install ngrok
   
   # macOS
   brew install ngrok
   ```

2. **Authenticate:**
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

3. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Update .env with ngrok URL:**
   ```env
   NGROK_URL=https://xxxxxxxx-xx.ngrok.io
   ```

---

## 📚 Commands Reference

For detailed command reference, see [command list.txt](./command%20list.txt)

### Common Commands

**Database Management:**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show SQL for migrations
python manage.py sqlmigrate app 0001
```

**Static Files:**
```bash
# Collect static files
python manage.py collectstatic

# Clear static files cache
python manage.py clearcache
```

**Testing:**
```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test app.tests

# Run with verbosity
python manage.py test --verbosity=2
```

**Development Server:**
```bash
# Development server (not for production)
python manage.py runserver 0.0.0.0:8000

# Use Daphne for WebSocket support
daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
```

---

## 📁 Project Structure

```
mindmate/
├── accounts/                    # User authentication & profiles
│   ├── migrations/
│   ├── templates/accounts/     # Login, signup, profile templates
│   ├── models.py               # User profile with phone number
│   ├── views.py                # Auth views and profile completion
│   ├── forms.py
│   └── signals.py              # Auto-create profiles on user creation
│
├── app/                         # Core application
│   ├── migrations/
│   ├── templates/app/          # Dashboard, assessments, tools
│   ├── models.py               # TestResult, ChatHistory, JournalEntry, Prescription
│   │                           # MeditationSession, MeditationProgress
│   ├── views.py                # Main views (dashboard, PHQ-9, chatbot, journal,
│   │                           # prescription digitizer, meditation)
│   ├── forms.py
│   ├── urls.py                 # Core app URL patterns
│   └── admin.py
│
├── games/                       # Gamification & wellness games
│   ├── migrations/
│   ├── templates/games/        # Quiz, mini-games, AI games UI
│   ├── models.py               # Quiz, QuizAttempt, Leaderboard, MiniGameScore,
│   │                           # MiniGameLeaderboard, UsedQuestion
│   ├── views.py                # Quiz system (8 genres), 6 mini-games,
│   │                           # AI riddles, mystery, story adventure
│   └── urls.py                 # Games URLs (~35 endpoints)
│
├── voice_calls/                 # Voice integration module
│   ├── migrations/
│   ├── templates/voice_calls/  # Call scheduling, history UI
│   ├── services/               # Twilio, ElevenLabs service integrations
│   │   ├── elevenlabs_service.py
│   │   └── twilio_service.py
│   ├── models.py               # VoiceCallSchedule, VoiceCallHistory, CallSentiment
│   ├── views.py                # Call scheduling, history, TwiML generation
│   ├── consumers.py            # WebSocket consumers for real-time voice
│   ├── routing.py              # WebSocket routing configuration
│   ├── tasks.py                # Celery tasks for scheduled calls
│   └── urls.py                 # Voice call URLs
│
├── perplex/                     # Django project settings
│   ├── settings.py             # Main Django settings with Channels, Celery
│   ├── asgi.py                 # ASGI configuration for WebSockets
│   ├── wsgi.py                 # WSGI configuration for production
│   ├── urls.py                 # Master URL routing
│   ├── celery.py               # Celery app configuration
│   └── routing.py              # WebSocket routing setup
│
├── templates/                   # Global templates
│   ├── base.html               # Base template with navbar, footer
│   ├── account/                # Allauth templates (login, signup, logout)
│   └── includes/               # Header, footer, alerts components
│       ├── header.html
│       └── footer.html
│
├── media/                       # User-uploaded files
│   ├── images/                 # Profile images, emotion captures
│   └── prescriptions/          # Prescription scans (images & PDFs)
│
├── static/                      # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── venv/                        # Python virtual environment
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies (~60 packages)
├── docker-compose.yml           # Docker Compose (dev environment)
├── docker-compose.prod.yml      # Docker Compose (production)
├── Dockerfile                   # Docker image definition
├── docker-entrypoint.sh         # Docker startup script
├── .env                         # Environment variables (not in git)
├── .env.example                 # Example env file template
├── .gitignore                   # Git ignore rules
├── db.sqlite3                   # SQLite database (development)
├── celerybeat-schedule.db       # Celery Beat schedule database
├── dump.rdb                     # Redis persistence file
├── LICENSE                      # Proprietary License
├── README.md                    # This file
├── AI_MINI_GAMES_SUMMARY.md     # Detailed games documentation
│
├── *.ps1                        # PowerShell automation scripts
│   ├── setup-env.ps1           # Environment setup
│   ├── setup-voice-calls.ps1   # Voice system setup
│   ├── start-server.ps1        # Start Django server
│   ├── start-redis.ps1         # Start Redis server
│   ├── start_voice_system.ps1  # Start all voice components
│   ├── stop-redis.ps1          # Stop Redis
│   ├── update-ngrok.ps1        # Update ngrok URL
│   └── docker-quickstart.ps1   # Quick Docker setup
│
└── *.bat                        # Windows batch scripts
    ├── start-celery-worker.bat
    ├── start-celery-beat.bat
    └── start-daphne.bat
```

### Key URLs & Routes

**Main Application** (`/`):
- `/` - Home page
- `/dashboard/` - User dashboard with all metrics
- `/about/` - About page
- `/contact/` - Contact page
- `/how-to-use/` - Feature guide

**Assessments & Tools** (`/app/`):
- `/assesment/` - PHQ-9 depression screening
- `/chatbot/` - AI conversational chatbot
- `/journal/` - Journal with sentiment analysis
- `/prescription-digitizer/` - Prescription scanner
- `/prescriptions/` - Prescription history

**Games & Activities** (`/games/`):
- `/games/` - Games homepage
- `/games/quiz/select-genre/` - Quiz genre selection (8 genres)
- `/games/quiz/take/<id>/` - Take quiz
- `/games/analytics/` - Quiz performance analytics
- `/games/leaderboard/` - Quiz leaderboards
- `/games/mini-games/` - Mini-games hub
- `/games/mini-games/memory-match/` - Memory card game
- `/games/mini-games/pattern-recognition/` - Simon says game
- `/games/mini-games/logic-puzzle/` - 2048-style puzzle
- `/games/mini-games/ai-riddle/` - AI riddle challenge
- `/games/mini-games/mystery-detective/` - AI mystery game
- `/games/mini-games/story-adventure/` - AI story adventure

**Voice Calls** (`/voice_calls/`):
- `/voice_calls/schedule/` - Schedule wellness calls
- `/voice_calls/history/` - Call history with transcripts
- `/voice_calls/call/<id>/` - Individual call details

**Admin Panel**:
- `/admin/` - Django admin (superuser only)

---

## 🐛 Troubleshooting

### Redis Connection Issues

**Problem:** `ConnectionError: Error 111 connecting to localhost:6379`

**Solutions:**
1. Ensure Redis is running:
   ```bash
   # Windows (using Docker)
   docker run -d --name redis -p 6379:6379 redis:latest
   
   # macOS/Linux
   redis-server
   ```

2. Check Redis connection:
   ```bash
   redis-cli ping  # Should return PONG
   ```

### Daphne Server Issues

**Problem:** `Address already in use` on port 8000

**Solutions:**
1. Kill process on port 8000:
   ```powershell
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. Use different port:
   ```bash
   daphne -b 0.0.0.0 -p 8001 perplex.asgi:application
   ```

### Celery Worker Issues

**Problem:** Celery tasks not executing

**Solutions:**
1. Check worker is running:
   ```bash
   celery -A perplex inspect active
   ```

2. Restart worker with verbose logging:
   ```bash
   celery -A perplex worker -l debug -P solo
   ```

3. Ensure Redis is accessible to worker

### WebSocket Connection Failures

**Problem:** WebSocket connection fails in browser console

**Solutions:**
1. Ensure Daphne is running (not Django runserver)
2. Check ALLOWED_HOSTS includes your domain
3. Verify ngrok URL is correct and running
4. Check browser console for specific error messages

### Database Migration Issues

**Problem:** `ProgrammingError` during migration

**Solutions:**
1. Reset database (development only):
   ```bash
   python manage.py migrate zero
   python manage.py migrate
   ```

2. Create new migration if schema changed:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### API Key Errors

**Problem:** `Invalid API key` or authentication failures

**Solutions:**
1. Verify all API keys in `.env` file
2. Ensure `.env` file is in project root
3. Restart server after updating `.env`
4. Check API key hasn't expired in respective dashboards

---

## 💡 Development Tips

### Using Django Shell

```bash
python manage.py shell

# Example: Create test user
from accounts.models import Profile
from django.contrib.auth.models import User

user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)
profile = Profile.objects.create(user=user)
```

### Debugging with ipdb

```python
# Add to code to break execution
import ipdb; ipdb.set_trace()

# In console
$ s  # step into
$ n  # next line
$ c  # continue
$ p variable_name  # print variable
```

### Performance Optimization

1. **Enable Query Logging (Dev Only):**
   ```python
   # In settings.py
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           'django.db.backends': {
               'handlers': ['console'],
               'level': 'DEBUG',
           }
       }
   }
   ```

2. **Use select_related() and prefetch_related():**
   ```python
   # Avoid N+1 queries
   users = User.objects.select_related('profile').all()
   ```

3. **Cache Frequently Accessed Data:**
   ```python
   from django.core.cache import cache
   
   cached_data = cache.get('key')
   if not cached_data:
       cached_data = expensive_operation()
       cache.set('key', cached_data, 3600)
   ```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test app.tests.TestClass

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Managing Celery Tasks

```bash
# Inspect active tasks
celery -A perplex inspect active

# Check registered tasks
celery -A perplex inspect registered

# Purge all queued tasks
celery -A perplex purge

# Check worker status
celery -A perplex inspect ping
```

### Docker Development

```bash
# Build image
docker build -t mindmate:latest .

# Run container
docker run -d --name mindmate \
  -p 8000:8000 \
  -v $(pwd):/code \
  mindmate:latest

# View logs
docker logs -f mindmate

# Stop container
docker stop mindmate
```

---

## 📞 Support & Contribution

For issues, feature requests, or contributions:
- Open an issue on the project repository
- Contact: support@techipedia.com
- Documentation: [Full Docs URL]

---

## 📝 License

© 2026 Techipedia. All rights reserved.

This project and all its contents are the exclusive property of Techipedia. Unauthorized copying, reproduction, or distribution of this project or any of its components is strictly prohibited without prior written permission from Techipedia.

---

<div align="center">

**Built with ❤️ for mental health and wellness**

</div>
