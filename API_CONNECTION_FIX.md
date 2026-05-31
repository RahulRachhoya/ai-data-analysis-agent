# 🔧 API CONNECTION FIX - "Not Found" Error

## ❌ The Problem

Frontend shows: {"detail":"Not Found"} when uploading CSV files.

## 🔍 Root Cause

The NEXT_PUBLIC_API_URL environment variable is not being set correctly in the deployed frontend, so the frontend is trying to connect to the wrong backend URL.

## ✅ The Solution

You need to set the environment variable in Render Dashboard for the frontend service.

---

## 🚀 **FIX STEPS - Do This in Render Dashboard**

### **Step 1: Go to Frontend Service Settings**

1. Go to: https://dashboard.render.com
2. Click on your data-analysis-frontend service
3. Click on **"Environment"** in the left sidebar

### **Step 2: Verify/Add Environment Variable**

Check if NEXT_PUBLIC_API_URL exists:

- **If it exists**: Verify the value is: https://data-analysis-backend.onrender.com
- **If it doesn't exist**: Click "Add Environment Variable" and add:
  - **Key**: NEXT_PUBLIC_API_URL
  - **Value**: https://data-analysis-backend.onrender.com

**IMPORTANT**: Make sure there's NO trailing slash (/)

✅ Correct: https://data-analysis-backend.onrender.com  
❌ Wrong: https://data-analysis-backend.onrender.com/

### **Step 3: Save and Redeploy**

1. Click **"Save Changes"**
2. Render will automatically redeploy the frontend
3. Wait ~10-15 minutes for the build to complete

---

## 📋 **Quick Checklist**

Before redeploying:
- [ ] Frontend environment has NEXT_PUBLIC_API_URL set
- [ ] Value is https://data-analysis-backend.onrender.com (no trailing slash)
- [ ] Backend service is "Live" and healthy
- [ ] Backend health check works: https://data-analysis-backend.onrender.com/health

After redeploying:
- [ ] Frontend builds successfully
- [ ] Frontend service shows "Live" status
- [ ] Can upload CSV files
- [ ] No "Not Found" error

---

## 🚀 **Do This Now:**

1. **Go to**: https://dashboard.render.com
2. **Click**: data-analysis-frontend service
3. **Click**: "Environment" tab
4. **Add/Update**: NEXT_PUBLIC_API_URL = https://data-analysis-backend.onrender.com
5. **Save**: Changes → Auto-redeploy starts
6. **Wait**: ~15 minutes
7. **Test**: Upload a CSV file
8. **SUCCESS!** 🎉

---

**Let me know once you've set the environment variable and I can help verify the deployment!**
