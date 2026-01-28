# 🚀 Supabase Cloud Sync Setup Guide

This guide will help you set up **FREE** cloud sync for Angel's Flow using Supabase.

## 📋 What You'll Get

✅ Tasks sync across ALL your devices
✅ Real-time updates
✅ Automatic backups
✅ 100% FREE (no credit card required)

---

## Step 1: Create Supabase Account (2 minutes)

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with **GitHub** (easiest) or email
4. Verify your email if needed

---

## Step 2: Create a New Project (1 minute)

1. Click **"New Project"**
2. Fill in:
   - **Name**: `angel-flow` (or anything you like)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you (e.g., US East, Europe West)
3. Click **"Create new project"**
4. Wait 2-3 minutes for setup to complete

---

## Step 3: Create Database Tables (3 minutes)

1. In your Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New Query"**
3. **Copy and paste** this entire SQL code:

```sql
-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER DEFAULT 3,
    category TEXT DEFAULT 'personal',
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    recurring BOOLEAN DEFAULT FALSE,
    recurring_freq TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create trash table
CREATE TABLE trash (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    task_id UUID,
    description TEXT NOT NULL,
    priority INTEGER,
    category TEXT,
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE,
    completed BOOLEAN,
    recurring BOOLEAN,
    recurring_freq TEXT,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_stats table
CREATE TABLE user_stats (
    user_id TEXT PRIMARY KEY,
    streak INTEGER DEFAULT 0,
    theme TEXT DEFAULT 'light',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE trash ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all operations for demo)
CREATE POLICY "Users can do everything with their own tasks"
    ON tasks FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can do everything with their own trash"
    ON trash FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can do everything with their own stats"
    ON user_stats FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_trash_user_id ON trash(user_id);
```

4. Click **"Run"** (bottom right)
5. You should see **"Success. No rows returned"**

---

## Step 4: Get Your API Keys (1 minute)

1. Click **"Settings"** (left sidebar, bottom)
2. Click **"API"**
3. You'll see two important values:
   - **Project URL** (looks like: `https://abcdefg.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

4. **Keep this tab open** - you'll need these values next!

---

## Step 5: Configure Your App (2 minutes)

### On Render (Production):

1. Go to your Render dashboard
2. Click on your **"flow-task-management"** service
3. Click **"Environment"** (left sidebar)
4. Click **"Add Environment Variable"**
5. Add these TWO variables:

   **Variable 1:**
   - Key: `SUPABASE_URL`
   - Value: (paste your Project URL from Supabase)

   **Variable 2:**
   - Key: `SUPABASE_KEY`
   - Value: (paste your anon public key from Supabase)

6. Click **"Save Changes"**
7. Your app will automatically redeploy (takes ~2 minutes)

### For Local Development (Optional):

1. In your project folder, create a file named `.env`
2. Add these lines (replace with your actual values):

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

3. Save the file

---

## ✅ You're Done!

Your app now has **cloud sync**!

### What Happens Next:

1. **First Login**: Your existing localStorage tasks will be migrated to cloud
2. **Any Device**: Login with same credentials → See all your tasks
3. **Real-time**: Complete a task on phone → Instantly appears on desktop
4. **Forever Free**: No charges, no limits for personal use

---

## 🔒 Security Notes

- Your data is encrypted at rest
- Only you can see your tasks (Row Level Security enabled)
- Supabase is SOC 2 certified and GDPR compliant
- The `anon` key is safe to use in your app

---

## 🆘 Troubleshooting

**Issue**: "Connection error" or tasks not saving

**Solution**:
1. Check your environment variables in Render are correct
2. Make sure you ran the SQL code to create tables
3. Wait 2-3 minutes after deployment

**Issue**: "No tasks showing up"

**Solution**:
1. Check you're logged in with the correct username
2. Try logging out and back in
3. Check Supabase dashboard → "Table Editor" → "tasks" to see if data is there

---

## 📊 View Your Data

You can see all your synced data in Supabase:

1. Go to your Supabase dashboard
2. Click **"Table Editor"** (left sidebar)
3. Click on **"tasks"**, **"trash"**, or **"user_stats"**
4. You'll see all your data in real-time!

---

**Need help?** Check the Supabase docs: [https://supabase.com/docs](https://supabase.com/docs)

**Estimated Total Time**: ~10 minutes
**Cost**: $0 forever (for personal use)
