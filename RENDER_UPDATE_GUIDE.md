# 🔄 Updating Flow on Render

This guide explains how to deploy updates to your Flow app on Render.

---

## 🚀 Quick Update (Automatic)

If you have **Auto-Deploy** enabled (default), updates are automatic:

1. **Push changes to GitHub:**
   ```bash
   git push origin claude/task-management-multiverse-app-Ya2OQ
   ```

2. **Render detects the push** and automatically:
   - Pulls latest code
   - Runs build command
   - Deploys new version
   - Zero downtime!

**That's it!** Your app updates in ~2 minutes. ✨

---

## 📋 Manual Update

If Auto-Deploy is disabled or you want manual control:

### Step 1: Push Your Changes

```bash
# Make sure all changes are committed
git add -A
git commit -m "Add edit task feature"
git push origin claude/task-management-multiverse-app-Ya2OQ
```

### Step 2: Trigger Deploy on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click on your **Flow** service
3. Click **"Manual Deploy"** dropdown
4. Select **"Deploy latest commit"**
5. Click **"Deploy"**

**Done!** Render rebuilds and deploys your app.

---

## 🎯 Current Update: Edit Task Feature

### What's New:

✨ **Edit Tasks After Creation**
- Click the ✏️ **Edit** button on any task
- Modal opens with current task data
- Update description, priority, category, or due date
- Click **"Save Changes"** to update
- Click **"Cancel"** to close without saving

### Files Changed:
- `flow_app.py` - Added edit modal and callbacks
- Task cards now have Edit button (✏️) next to Delete (🗑️)

---

## 🔍 Checking Deployment Status

### On Render Dashboard:

1. **Build Logs** - See real-time build progress
2. **Deploy Status** - Shows "Live" when ready
3. **Events Tab** - History of all deployments

### Build Process:
```
1. Pulling code from GitHub...
2. Installing dependencies... (pip install -r requirements.txt)
3. Building application...
4. Starting service... (gunicorn flow_app:server)
5. Health check passing ✓
6. Deployment complete! 🎉
```

**Time:** Usually 1-2 minutes

---

## 🛠️ Troubleshooting Updates

### Build Fails

**Check Build Logs:**
1. Click on your service
2. Go to **"Logs"** tab
3. Look for error messages

**Common Issues:**
- **Syntax Error:** Fix in code and push again
- **Dependency Error:** Update `requirements.txt`
- **Port Error:** Ensure `PORT` environment variable is used

**Fix:**
```bash
# Fix the issue locally
git add .
git commit -m "Fix build error"
git push origin claude/task-management-multiverse-app-Ya2OQ
```

Render auto-deploys the fix.

### Deployment Stuck

If deployment seems stuck:

1. **Wait 5 minutes** - Sometimes it's just slow
2. **Check Logs** - Look for errors
3. **Manual Deploy** - Try triggering again
4. **Rollback** - Use "Manual Deploy" → "Deploy previous version"

### App Not Updating

**Clear Cache:**
1. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Try incognito/private mode

**Check Version:**
- Add a version number in your app to verify updates

---

## 🎨 Updating render.yaml

If you modify `render.yaml`:

```yaml
services:
  - type: web
    name: flow-task-management
    env: python
    branch: claude/task-management-multiverse-app-Ya2OQ
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn flow_app:server --bind 0.0.0.0:$PORT"
```

**Changes auto-apply** on next deployment.

---

## 📱 Testing Updates

### Before Deploying:

```bash
# Test locally first
python flow_app.py

# Open http://localhost:8052
# Test the new feature
# Make sure everything works
```

### After Deploying:

1. **Visit your Render URL**
2. **Clear cache** (Ctrl+Shift+R)
3. **Test the new feature**
4. **Check mobile** if mobile-related changes

---

## ⚡ Zero-Downtime Deploys

Render provides **zero-downtime deployments**:

- Old version keeps running
- New version builds in background
- Health check passes on new version
- Traffic switches to new version
- Old version shuts down

**Users never see downtime!** 🎉

---

## 🔄 Rollback

If something breaks, rollback to previous version:

1. **Go to Render Dashboard**
2. **Click "Manual Deploy"**
3. **Select previous commit from dropdown**
4. **Click "Deploy"**

**Back to working version in 2 minutes!**

---

## 📊 Deployment Best Practices

### 1. Test Locally First
```bash
python flow_app.py
# Test thoroughly before pushing
```

### 2. Use Meaningful Commits
```bash
git commit -m "Add task editing feature with modal"
# Not: "update stuff"
```

### 3. Check Logs After Deploy
- Go to Logs tab
- Verify no errors
- Check startup messages

### 4. Monitor First Few Minutes
- Watch for errors
- Test key features
- Check mobile if needed

### 5. Keep Dependencies Updated
```bash
# Update requirements.txt when adding packages
pip freeze > requirements.txt
```

---

## 🎯 Current Deployment Info

**Branch:** `claude/task-management-multiverse-app-Ya2OQ`
**Build:** `pip install -r requirements.txt`
**Start:** `gunicorn flow_app:server --bind 0.0.0.0:$PORT`
**Region:** Oregon (or your selected region)
**Plan:** Free Tier

---

## 🚨 Emergency Procedures

### App is Down

1. **Check Render Status** - [status.render.com](https://status.render.com)
2. **Check Logs** - Look for crash errors
3. **Rollback** - Deploy previous working version
4. **Restart Service** - Manual Deploy → Clear cache & deploy

### Database Issues (Future)

When you add a database:
1. Check connection string
2. Verify database is running
3. Check database logs
4. Test connection from app

---

## ✅ Update Checklist

Before pushing updates:

- [ ] Test locally (`python flow_app.py`)
- [ ] All features work
- [ ] No syntax errors
- [ ] Dependencies updated if needed
- [ ] Meaningful commit message
- [ ] Push to correct branch

After deployment:

- [ ] Wait for "Live" status
- [ ] Check Logs for errors
- [ ] Clear browser cache
- [ ] Test new feature
- [ ] Test on mobile (if mobile changes)

---

## 📞 Getting Help

**Render Support:**
- Community: [community.render.com](https://community.render.com)
- Docs: [render.com/docs](https://render.com/docs)
- Status: [status.render.com](https://status.render.com)

**Flow App:**
- Check FLOW_README.md
- Review error logs
- Test locally first

---

## 🎉 Summary

**To update your Flow app:**

1. **Make changes** locally
2. **Test** (`python flow_app.py`)
3. **Commit** with good message
4. **Push** to GitHub
5. **Wait** for auto-deploy (2 min)
6. **Verify** app is updated

**That's it!** Render makes deployments effortless. 🚀

---

**Current Update Ready:**
- ✅ Edit task feature implemented
- ✅ All syntax checked
- ✅ Ready to commit and push
- ✅ Will auto-deploy to Render

**Just push to GitHub and Render does the rest!** ✨
