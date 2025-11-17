# 🚀 MongoDB Atlas Setup - Complete Guide

## ✅ **What You'll Do:**
1. Create FREE MongoDB Atlas account (2 minutes)
2. Get connection string (1 minute)
3. Update configuration (30 seconds)
4. Start backend server (10 seconds)

---

## 📋 **STEP 1: Create MongoDB Atlas Account**

### **1.1 Sign Up**
```powershell
# Run this to open registration page:
Start-Process "https://www.mongodb.com/cloud/atlas/register"
```

Or go to: **https://www.mongodb.com/cloud/atlas/register**

### **1.2 Complete Registration**
- Sign up with **Google** (fastest) or email
- Verify your email if needed

### **1.3 Create FREE Cluster**
When asked to choose a plan:
- Select **M0 FREE** tier (512 MB - perfect for development)
- Provider: **AWS**
- Region: **Mumbai (ap-south-1)** or closest to you
- Cluster Name: Leave as **Cluster0** (default)
- Click **"Create Deployment"**

⏰ **Wait 3-5 minutes** for cluster creation

---

## 📋 **STEP 2: Create Database User**

### **2.1 Go to Database Access**
- In left sidebar, click **"Database Access"**
- Click **"+ ADD NEW DATABASE USER"**

### **2.2 Create User**
- Authentication Method: **Password**
- Username: `leadgenai`
- Password: Create strong password (click "Autogenerate Secure Password" or make your own)
- **⚠️ SAVE THIS PASSWORD!** You'll need it!
- Database User Privileges: **Atlas admin**
- Click **"Add User"**

---

## 📋 **STEP 3: Allow Network Access**

### **3.1 Go to Network Access**
- In left sidebar, click **"Network Access"**
- Click **"+ ADD IP ADDRESS"**

### **3.2 Allow Your IP**
For development (easiest):
- Click **"ALLOW ACCESS FROM ANYWHERE"**
- Click **"Confirm"**

⚠️ For production, add only your server's IP address

---

## 📋 **STEP 4: Get Connection String**

### **4.1 Go to Database**
- In left sidebar, click **"Database"**
- You should see your **Cluster0**
- Click **"Connect"** button

### **4.2 Choose Connection Method**
- Select **"Drivers"**
- Driver: **Python**
- Version: **3.6 or later**

### **4.3 Copy Connection String**
You'll see something like this:
```
mongodb+srv://leadgenai:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**IMPORTANT:** 
- Replace `<password>` with your actual password
- Add `/leadgen_db` before the `?`

**Final format:**
```
mongodb+srv://leadgenai:YourPassword123@cluster0.xxxxx.mongodb.net/leadgen_db?retryWrites=true&w=majority
```

---

## 📋 **STEP 5: Update Backend Configuration**

### **Option A: Automatic (Recommended)**

Run this PowerShell script:
```powershell
cd "d:\project by sujal\B2B smart marketing"
.\update-mongodb-connection.ps1
```

It will:
1. Ask for your connection string
2. Validate it
3. Update `.env.production` file
4. Offer to start the backend automatically

### **Option B: Manual**

1. Open file: `backend\.env.production`
2. Find this line:
   ```
   MONGODB_URL=mongodb://admin:password123@localhost:27017
   ```
3. Replace with your Atlas connection string:
   ```
   MONGODB_URL=mongodb+srv://leadgenai:YourPassword123@cluster0.xxxxx.mongodb.net/leadgen_db?retryWrites=true&w=majority
   ```
4. Save the file
5. Copy to `.env`:
   ```powershell
   Copy-Item "backend\.env.production" "backend\.env" -Force
   ```

---

## 📋 **STEP 6: Start Backend Server**

```powershell
cd "d:\project by sujal\B2B smart marketing\backend"
uvicorn main:app --reload --port 8000
```

### **Expected Output:**
```
INFO:     Will watch for changes in these directories: ['D:\\project by sujal\\B2B smart marketing\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ Connected to MongoDB successfully!
✅ Beanie initialized successfully!
INFO:     Application startup complete.
```

---

## 📋 **STEP 7: Test Your API**

### **Open API Documentation:**
```powershell
Start-Process "http://localhost:8000/docs"
```

Or go to: **http://localhost:8000/docs**

### **Test Endpoints:**

1. **Create Account:**
   - Expand `POST /api/auth/signup`
   - Click "Try it out"
   - Fill in:
     ```json
     {
       "email": "test@example.com",
       "password": "test123456",
       "full_name": "Test User"
     }
     ```
   - Click "Execute"
   - ✅ Should return 200 with access token

2. **Login:**
   - Expand `POST /api/auth/login`
   - Click "Try it out"
   - Enter email and password
   - Click "Execute"
   - ✅ Copy the `access_token`

3. **Test Protected Endpoint:**
   - Click 🔒 "Authorize" button at top
   - Paste your access token
   - Click "Authorize"
   - Now try `GET /api/auth/me`
   - ✅ Should return your user info!

---

## 🎉 **SUCCESS!**

Your backend is now:
- ✅ Running on http://localhost:8000
- ✅ Connected to MongoDB Atlas (cloud database)
- ✅ JWT authentication working
- ✅ Ready to discover B2B leads!

---

## 🚀 **Next Steps:**

1. **Test Lead Discovery:**
   ```
   POST /api/leads/discover
   {
     "business_name": "Tech Consulting",
     "business_desc": "IT consulting services",
     "max_leads": 3
   }
   ```

2. **Start Frontend:**
   ```powershell
   cd "d:\project by sujal\B2B smart marketing\frontend"
   npm run dev
   ```
   Access at: http://localhost:3000

3. **Build Frontend Pages:**
   - Landing page
   - Login/Signup
   - Dashboard
   - Lead discovery page

---

## 🆘 **Troubleshooting:**

### **Error: "No module named 'pymongo'"**
```powershell
pip install pymongo motor beanie
```

### **Error: "Connection refused"**
Check your MongoDB Atlas:
- Network Access: IP whitelist set?
- Database User: Created with correct password?
- Connection string: Has `/leadgen_db` before `?`?

### **Error: "Authentication failed"**
- Check password in connection string
- Make sure user has "Atlas admin" role

---

## 📞 **MongoDB Atlas Links:**

- Dashboard: https://cloud.mongodb.com
- Documentation: https://docs.mongodb.com/atlas
- Free Tier Limits: 512 MB storage, shared RAM

---

**Last Updated:** October 28, 2025
