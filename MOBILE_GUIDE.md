# 📱 Mobile Guide - Using Task Multiverse on Your Phone

Task Multiverse is now a Progressive Web App (PWA) that you can install and use on your phone just like a native app!

## Quick Start

### Option 1: Use it in Your Browser (Easiest)

1. **Deploy the app** (see deployment options below)
2. **Open the URL** in your phone's browser
3. **Start using it** - That's it! Works immediately

### Option 2: Install as a PWA (Recommended)

Install Task Multiverse on your phone for a native app experience:

#### On iPhone (Safari)

1. Open Safari and navigate to your app URL
2. Tap the **Share** button (square with arrow pointing up)
3. Scroll down and tap **"Add to Home Screen"**
4. Name it "Task Multiverse" and tap **Add**
5. The app icon will appear on your home screen!

#### On Android (Chrome)

1. Open Chrome and navigate to your app URL
2. Tap the **menu** (three dots in the corner)
3. Tap **"Add to Home screen"** or **"Install app"**
4. Tap **Install** on the popup
5. The app will be installed like a native app!

**Alternative for Android:**
- Look for a banner at the bottom of the screen saying "Add Task Multiverse to Home screen"
- Tap **Install**

## Deployment Options

### Option 1: Local Network Access (Testing)

Perfect for testing on your home WiFi:

```bash
# On your computer, run:
python task_multiverse_app.py

# The app will run on port 8051
# Find your computer's IP address:

# On Mac/Linux:
ifconfig | grep "inet "

# On Windows:
ipconfig

# On your phone, connect to same WiFi and open:
# http://YOUR_COMPUTER_IP:8051
# Example: http://192.168.1.100:8051
```

**Pros:** Quick and easy for testing
**Cons:** Only works on same WiFi network

### Option 2: ngrok (Temporary Public URL)

Get a public URL instantly for testing:

```bash
# Install ngrok: https://ngrok.com/download

# Run your app:
python task_multiverse_app.py

# In another terminal, run:
ngrok http 8051

# Use the HTTPS URL provided (e.g., https://abc123.ngrok.io)
```

**Pros:** Works from anywhere, instant setup
**Cons:** URL changes each time, free tier has limits

### Option 3: Cloud Deployment (Production)

Deploy to the cloud for permanent access:

#### Deploy to Google Cloud Run (Recommended)

```bash
# 1. Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Build and deploy
gcloud run deploy task-multiverse \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

# You'll get a URL like: https://task-multiverse-xxx.run.app
```

#### Deploy to Render (Easy Alternative)

1. Create account at [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn task_multiverse_app:server -w 1 --threads 8 --timeout 0 -b 0.0.0.0:$PORT`
5. Click **"Create Web Service"**

#### Deploy to Railway (Another Easy Option)

1. Create account at [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway auto-detects Python and deploys!

**Pros:** Permanent URL, works from anywhere, free tiers available
**Cons:** Requires initial setup

### Option 4: Heroku (Classic Choice)

```bash
# 1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app and deploy
heroku create task-multiverse-yourname
git push heroku main

# 4. Open app
heroku open
```

## Mobile Features

### What Works Great on Mobile

✅ **Touch-optimized interface** - All buttons are touch-friendly (44px minimum)
✅ **Responsive layout** - Adapts to your screen size
✅ **Smooth animations** - Characters move and float smoothly
✅ **No zoom issues** - Input fields sized properly to prevent zoom
✅ **Works offline** - After first visit, works without internet (PWA feature)
✅ **Home screen icon** - Looks like a native app
✅ **No address bar** - Runs in standalone mode when installed
✅ **Fast loading** - Optimized for mobile networks

### Mobile-Specific Features

- **Touch feedback** - Buttons respond to touch with visual feedback
- **Pull to refresh** - Disabled to prevent accidental refreshes
- **Smooth scrolling** - Native-like scrolling behavior
- **Portrait optimized** - Best experience in portrait mode
- **Offline support** - Service worker caches the app

## Tips for Best Mobile Experience

### Before You Start

1. **Use HTTPS**: PWA features require HTTPS (automatic with cloud deployments)
2. **Good network**: First load downloads the app (about 1-2MB)
3. **Install it**: PWA installation provides best experience

### While Using

1. **Portrait mode works best**: The app is optimized for portrait
2. **Stay updated**: Pull down to refresh occasionally for latest features
3. **Complete tasks promptly**: Keeps your reminder notifications relevant
4. **Use high priority wisely**: Reserve Critical priority for truly urgent tasks

### Battery & Data

- **Battery efficient**: Characters update every 2 seconds (gentle on battery)
- **Data usage**: After first load, uses minimal data
- **Offline mode**: Works without internet after first visit
- **Background**: Can run in background (iOS 14+, Android 8+)

## Troubleshooting

### "Cannot install" or No Install Option

**Solution:**
- Make sure you're using HTTPS (required for PWA)
- Try clearing browser cache
- Update your browser to latest version
- On iPhone: Must use Safari (not Chrome)

### App Loads Slowly

**Solution:**
- Check your internet connection
- Wait for service worker to cache app (first load only)
- After first load, should be instant

### Characters Not Moving

**Solution:**
- Make sure JavaScript is enabled
- Try refreshing the page
- Check browser console for errors (Dev Tools)

### Reminders Not Showing

**Solution:**
- Create a task and assign to a character
- Wait 5 seconds for first reminder check
- Verify task has active status

### App Looks Weird on Phone

**Solution:**
- Make sure viewport is set correctly (automatic)
- Try rotating to portrait mode
- Clear browser cache and reload
- Update to latest version

### "Add to Home Screen" Not Working on iPhone

**Must use Safari** - PWA installation only works in Safari on iOS:
1. Open Safari (not Chrome or other browsers)
2. Visit your app URL
3. Tap share button (bottom center)
4. Scroll and tap "Add to Home Screen"

### Service Worker Not Registering

**Solution:**
- Ensure you're using HTTPS or localhost
- Check browser console for errors
- Make sure service-worker.js is accessible at /assets/service-worker.js
- Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

## Technical Details

### PWA Features Enabled

- ✅ Web App Manifest
- ✅ Service Worker for offline support
- ✅ App icons (192x192, 512x512, and more)
- ✅ Splash screen support
- ✅ Standalone display mode
- ✅ Theme color (#667eea)
- ✅ Responsive viewport
- ✅ Touch-optimized UI

### Browser Support

| Browser | Support | Install PWA? |
|---------|---------|-------------|
| Safari (iOS) | ✅ Full | ✅ Yes |
| Chrome (Android) | ✅ Full | ✅ Yes |
| Firefox (Mobile) | ✅ Full | ⚠️ Limited |
| Samsung Internet | ✅ Full | ✅ Yes |
| Edge (Mobile) | ✅ Full | ✅ Yes |

### System Requirements

- **iOS**: 11.3 or higher (PWA support added in 11.3)
- **Android**: 5.0 or higher
- **Browsers**: Chrome 73+, Safari 11.1+, Firefox 79+, Edge 79+

## Security & Privacy

- 🔒 **No data collection**: Everything stays on your device
- 🔒 **No account required**: No sign up, no email
- 🔒 **Client-side storage**: Tasks stored in your browser
- 🔒 **HTTPS required**: Secure connection for PWA features
- 🔒 **No tracking**: No analytics or user tracking

## Frequently Asked Questions

### Q: Will my tasks sync across devices?

**A:** Currently, tasks are stored locally in your browser. Each device maintains its own task list. Future updates may add cloud sync.

### Q: Can I get push notifications?

**A:** The service worker supports notifications, but they're not enabled by default. Future updates will add optional push notifications for task reminders.

### Q: Does it work offline?

**A:** Yes! After your first visit, the app is cached and works offline. You can create and manage tasks without internet. Character animations continue to work offline too.

### Q: How much storage does it use?

**A:** Very minimal:
- App files: ~500KB (cached after first visit)
- Your tasks: ~1KB per task
- Total: Usually under 1MB

### Q: Can I use it on my tablet?

**A:** Absolutely! The app works great on tablets. The responsive design adapts to larger screens while maintaining the mobile-friendly interface.

### Q: What happens if I clear my browser data?

**A:** Your tasks are stored in browser local storage. If you clear browser data, your tasks will be lost. Future updates may add export/backup features.

### Q: Can I customize the characters?

**A:** Currently, the 5 characters (Alex, Maya, Leo, Zara, Sam) are pre-defined. Check the main README for instructions on adding custom characters by editing the source code.

### Q: Is there a limit to how many tasks I can create?

**A:** No hard limit, but performance is best with under 100 active tasks. The app is designed for actionable task management, not long-term storage.

## Need Help?

Having issues? Here's how to get support:

1. **Check this guide** - Most issues are covered above
2. **Check the main README** - Technical details and customization
3. **Browser console** - Look for error messages (Dev Tools → Console)
4. **Create an issue** - Open an issue in the GitHub repository

## Future Mobile Features

Planned enhancements for mobile experience:

- 📱 Push notifications for task reminders
- 🔄 Cloud sync across devices
- 📤 Share tasks with others
- 🎨 Custom character creation
- 🌙 Dark mode
- 🔊 Sound notifications
- 📊 Task analytics dashboard
- ⏰ Scheduled tasks with due dates
- 🏆 Achievements and gamification

---

**Enjoy Task Multiverse on your phone! 🌌📱**

Your characters are ready to help you stay organized, wherever you are!
