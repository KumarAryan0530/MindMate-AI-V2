# MindMate-AI Deployment Guide

## 🚀 Free Deployment Options

This project is configured for **FREE** deployment on cloud platforms. Here are your best options:

### ✅ Recommended: Render.com (BEST for this project)
- **Free PostgreSQL database** (1GB storage)
- **Free Redis instance** (25MB)
- **Free web service** (750 hours/month)
- **Free background workers**
- Supports WebSockets, Celery, and all your features

### 🔄 Alternative Options
1. **Railway.app** - Similar to Render, $5 free credits monthly
2. **Fly.io** - Free tier available with PostgreSQL
3. **PythonAnywhere** - Free tier but limited (no WebSockets on free tier)

### ❌ NOT Suitable
- **Netlify** - Only for static sites (won't work for Django backend)
- **Vercel** - Better for Next.js/static sites
- **GitHub Pages** - Only static sites

---

## 📋 Pre-Deployment Checklist

### 1. **Get Your API Keys**
You'll need these API keys for your application to work:

- **Google Gemini API**: https://aistudio.google.com/apikey
- **Cloudflare API**: https://dash.cloudflare.com/
- **Twilio** (for voice calls): https://www.twilio.com/console
- **ElevenLabs** (for AI voice): https://elevenlabs.io/

### 2. **Push Code to GitHub**
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for deployment"

# Create a new repository on GitHub and push
git remote add origin https://github.com/yourusername/mindmate-ai.git
git branch -M main
git push -u origin main
```

### 3. **Update .env.example**
Make sure your `.env.example` has all required variables (already done).

---

## 🎯 OPTION 1: Deploy to Render.com (Recommended)

### Step 1: Create Render Account
1. Go to https://render.com/
2. Sign up with your GitHub account (FREE)

### Step 2: Deploy Using Blueprint (Easiest!)
1. Click "New" → "Blueprint"
2. Connect your GitHub repository
3. Select the repository containing your `render.yaml`
4. Render will automatically detect the configuration
5. Click "Apply"

### Step 3: Configure Environment Variables
After deployment starts, go to each service and add these environment variables:

#### Web Service Environment Variables:
```
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
GEMINI_API_KEY=your-gemini-key
CLOUDFLARE_API_TOKEN=your-cloudflare-token
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-id
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_AGENT_ID=your-elevenlabs-agent-id
```

### Step 4: Wait for Build
- Render will automatically:
  - Install dependencies
  - Run migrations
  - Collect static files
  - Start all services (web, worker, beat)
  
This takes about 5-10 minutes on the free tier.

### Step 5: Access Your Application
Your app will be live at: `https://your-app-name.onrender.com`

---

## 🎯 OPTION 2: Deploy to Railway.app

### Step 1: Create Railway Account
1. Go to https://railway.app/
2. Sign up with GitHub (FREE - $5 credit monthly)

### Step 2: Deploy
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will auto-detect Django

### Step 3: Add Services
1. Add PostgreSQL database (from Railway marketplace)
2. Add Redis (from Railway marketplace)

### Step 4: Configure Environment Variables
In Railway project settings, add all environment variables from above.

### Step 5: Configure Build & Start Commands
- **Build Command**: `./build.sh`
- **Start Command**: `daphne -b 0.0.0.0 -p $PORT perplex.asgi:application`

### Step 6: Add Worker Services
1. Create new service from same repo
2. Set start command: `celery -A perplex worker --loglevel=info`
3. Create another for beat: `celery -A perplex beat --loglevel=info`

---

## 🎯 OPTION 3: Deploy Using Docker

### Step 1: Install Docker
Download from https://www.docker.com/

### Step 2: Build and Run Locally (Test)
```bash
# Build the image
docker build -t mindmate-ai .

# Run the container
docker run -p 8000:8000 --env-file .env mindmate-ai
```

### Step 3: Deploy to Fly.io (FREE)
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy
```

---

## 📊 Media Files Storage (Important!)

**Problem**: Free tier platforms use ephemeral storage - uploaded files will disappear on restart.

**Solution**: Use free cloud storage for media files.

### Option A: Cloudinary (Recommended - FREE)
1. Sign up at https://cloudinary.com/ (free tier: 25GB)
2. Install package:
```bash
pip install cloudinary django-cloudinary-storage
```

3. Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps
    'cloudinary_storage',
    'cloudinary',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Option B: AWS S3 Free Tier
1. Create AWS account (12 months free - 5GB)
2. Use `django-storages` and `boto3`

---

## 🔧 Post-Deployment Tasks

### 1. Create Superuser (Admin Account)
```bash
# On Render: Use the Shell tab in your web service
python manage.py createsuperuser

# On Railway: Use the terminal in project
python manage.py createsuperuser
```

### 2. Test Your Application
- Visit your site URL
- Test user registration
- Test AI chat features
- Test voice call features (if Twilio configured)
- Access admin panel: `https://your-site.com/admin`

### 3. Monitor Logs
- **Render**: Dashboard → Logs tab
- **Railway**: Project → Logs
- Check for any errors

### 4. Set Up Custom Domain (Optional)
- **Render**: Settings → Custom Domain
- **Railway**: Project → Settings → Domains
- Point your domain's DNS to the provided address

---

## ⚠️ Important Notes for Free Tier

### Limitations:
1. **Render Free Tier**:
   - Services sleep after 15 minutes of inactivity
   - Cold start takes 30-60 seconds
   - 750 hours/month (sufficient for one service 24/7)

2. **Database**:
   - PostgreSQL: 1GB storage (should be enough to start)
   - Redis: 25MB (sufficient for caching and Celery)

3. **Background Workers**:
   - Limited to 1 concurrent worker on free tier
   - Scheduled tasks work but with lower priority

### Workarounds:
1. **Keep Service Awake**:
   - Use UptimeRobot (free) to ping your site every 5 minutes
   - Sign up: https://uptimerobot.com/

2. **Database Cleanup**:
   - Regularly clean old chat history
   - Implement data retention policies

3. **Optimize Images**:
   - Compress images before upload
   - Use Cloudinary auto-optimization

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Common issues:
1. Missing dependencies → Check requirements.txt
2. Python version mismatch → Ensure Python 3.11
3. Database migrations fail → Check DATABASE_URL
```

### Application Won't Start
```bash
# Check:
1. Environment variables are set correctly
2. DATABASE_URL is configured
3. Static files collected successfully
4. Logs for specific error messages
```

### WebSocket Not Working
```bash
# Ensure:
1. Using Daphne (ASGI server) not Gunicorn
2. Redis is configured properly
3. REDIS_URL environment variable is set
4. Channels properly installed
```

### Celery Tasks Not Running
```bash
# Verify:
1. Worker service is running
2. Redis connection is active
3. CELERY_BROKER_URL is configured
4. Check worker logs for errors
```

---

## 🎓 Next Steps After Deployment

1. **Setup Monitoring**:
   - Use Render's built-in metrics
   - Set up UptimeRobot for uptime monitoring

2. **Implement Backups**:
   - Regular database backups (Render provides this)
   - Export user data periodically

3. **Security**:
   - Never commit `.env` file
   - Rotate API keys periodically
   - Monitor for suspicious activity

4. **Scale When Ready**:
   - Upgrade to paid tier if traffic increases
   - Consider CDN for static files
   - Implement caching strategies

---

## 📞 Support & Resources

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app/
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **Channels Deployment**: https://channels.readthedocs.io/en/stable/deploying.html

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] All API keys obtained
- [ ] Platform account created (Render/Railway)
- [ ] Services configured using render.yaml/blueprint
- [ ] Environment variables set
- [ ] Database and Redis provisioned
- [ ] Build completed successfully
- [ ] Application accessible via URL
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] All features tested
- [ ] Media storage configured (Cloudinary)
- [ ] UptimeRobot configured (keep-alive)
- [ ] Logs monitored for errors

---

## 💰 Cost Estimate

**Total Monthly Cost: $0 (FREE!)**

- Web Service: FREE (Render/Railway)
- PostgreSQL: FREE (1GB)
- Redis: FREE (25MB)
- Worker & Beat: FREE
- Cloudinary: FREE (25GB)
- Domain (optional): ~$10-15/year

**When to Upgrade:**
- Heavy traffic (>100 concurrent users)
- Need faster response times
- Want custom domain with SSL
- Need more storage
- Want 24/7 uptime without sleep

---

Good luck with your deployment! 🚀
Your MindMate-AI will be live and helping users in no time!
