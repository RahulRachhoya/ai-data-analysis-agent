# 🚀 RENDER DEPLOYMENT GUIDE - Complete Walkthrough

## ✅ Render Compatibility Confirmed!

**YES! Render supports BOTH services:**
- ✅ **Backend**: FastAPI + Python 3.12 + Docker ✅
- ✅ **Frontend**: Next.js 14 + Docker ✅
- ✅ **Free Tier**: 750 hours/month PER service (1,500 hours total!)
- ✅ **Docker Support**: Native Docker container support
- ✅ **Service Communication**: Internal networking between services
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Custom Domains**: Free subdomains + custom domain support

---

## 📋 Pre-Deployment Checklist

### Required API Keys:
- [ ] OpenAI API Key (or Groq/Anthropic/Google)
- [ ] E2B API Key (get free at https://e2b.dev)
- [ ] GitHub account
- [ ] Render account (sign up at https://render.com)

### Repository Status:
- ✅ All code committed to GitHub
- ✅ Dockerfiles present (backend & frontend)
- ✅ render.yaml configured
- ✅ CI/CD pipeline set up

---

## 🎯 Deployment Steps

### **Step 1: Sign Up for Render**
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

---

### **Step 2: Deploy Using Blueprint (Easiest Method)**

#### 2.1 Create New Blueprint
1. In Render dashboard, click **"New"** → **"Blueprint"**
2. Connect your GitHub repository: \RahulRachhoya/ai-data-analysis-agent\
3. Render will automatically detect your \ender.yaml\ file
4. Review the configuration (2 services will be created):
   - \data-analysis-backend\ (FastAPI)
   - \data-analysis-frontend\ (Next.js)

#### 2.2 Configure Environment Variables
Before deploying, you need to add your secret API keys:

**For Backend Service:**
1. Click on the backend service settings
2. Add environment variables:
   `
   OPENAI_API_KEY = your-openai-api-key-here
   E2B_API_KEY = your-e2b-api-key-here
   LLM_PROVIDER = openai
   OPENAI_MODEL = gpt-4o
   PORT = 8000
   `

**For Frontend Service:**
1. Click on the frontend service settings
2. The \NEXT_PUBLIC_API_URL\ will be set automatically
3. After backend deploys, update it to: \https://data-analysis-backend.onrender.com\

#### 2.3 Deploy!
1. Click **"Apply"** to create both services
2. Render will:
   - Build Docker images
   - Deploy backend first
   - Deploy frontend with backend URL
   - Assign URLs to both services

---

### **Step 3: Alternative - Manual Deployment**

If Blueprint doesn't work, you can deploy manually:

#### 3.1 Deploy Backend First
1. Click **"New"** → **"Web Service"**
2. Select your GitHub repository
3. Configure:
   - **Name**: \data-analysis-backend\
   - **Environment**: Docker
   - **Region**: Choose closest to you
   - **Branch**: \master\
   - **Dockerfile Path**: \./backend/Dockerfile\
   - **Docker Context**: \./backend\
4. Add environment variables (see Step 2.2 above)
5. Select **Free** plan
6. Click **"Create Web Service"**
7. **Wait for deployment to complete** (~5-10 minutes)
8. Copy the backend URL (e.g., \https://data-analysis-backend.onrender.com\)

#### 3.2 Deploy Frontend
1. Click **"New"** → **"Web Service"**
2. Select your GitHub repository
3. Configure:
   - **Name**: \data-analysis-frontend\
   - **Environment**: Docker
   - **Region**: Same as backend
   - **Branch**: \master\
   - **Dockerfile Path**: \./frontend/Dockerfile\
   - **Docker Context**: \./frontend\
4. Add environment variable:
   `
   NEXT_PUBLIC_API_URL = https://data-analysis-backend.onrender.com
   `
5. Select **Free** plan
6. Click **"Create Web Service"**
7. Wait for deployment (~5-10 minutes)

---

## 🔧 Post-Deployment Configuration

### Update Backend CORS (if needed)
Your backend already allows all origins (\llow_origins=["*"]\), so no changes needed!

### Verify Service Communication
1. Open your frontend URL: \https://data-analysis-frontend.onrender.com\
2. Try uploading a dataset
3. Check if backend API calls work

### Monitor Logs
- **Backend logs**: Render Dashboard → Backend Service → Logs
- **Frontend logs**: Render Dashboard → Frontend Service → Logs

---

## ⚠️ Important Notes

### Free Tier Limitations:
- ⏰ **Cold Starts**: Services spin down after 15 minutes of inactivity
- 🐌 **Startup Time**: ~30-60 seconds to wake up from sleep
- 💾 **No Persistent Storage**: Uploaded datasets are lost on restart
- ⏱️ **750 hours/month** per service (about 31 days if running 24/7)

### Solutions:
1. **Keep Services Alive**: Use a service like [UptimeRobot](https://uptimerobot.com) (free) to ping your frontend every 5 minutes
2. **Upgrade to Paid Plan**: \$7/month per service removes cold starts
3. **Use External Storage**: Store datasets in AWS S3 or similar

---

## 🎊 Expected Deployment URLs

After successful deployment:
- **Frontend**: \https://data-analysis-frontend.onrender.com\
- **Backend**: \https://data-analysis-backend.onrender.com\
- **Backend Health Check**: \https://data-analysis-backend.onrender.com/health\

---

## 🐛 Troubleshooting

### Build Fails?
- Check Dockerfiles are in correct paths
- Verify \equirements.txt\ and \package.json\ are complete
- Check Render build logs for specific errors

### Frontend Can't Connect to Backend?
1. Verify \NEXT_PUBLIC_API_URL\ is set correctly
2. Check backend URL is accessible: \https://your-backend.onrender.com/health\
3. Verify CORS is enabled in backend

### Cold Start Issues?
- First request after 15 min will be slow (30-60s)
- Use UptimeRobot to keep services alive
- Or upgrade to paid plan

---

## 📊 Deployment Timeline

| Task | Time |
|------|------|
| Sign up & authorize | 2 minutes |
| Configure services | 5 minutes |
| Backend build & deploy | 5-10 minutes |
| Frontend build & deploy | 5-10 minutes |
| Testing & verification | 5 minutes |
| **Total** | **~25-35 minutes** |

---

## 🎯 Next Steps After Deployment

1. **Test Your App**: Upload a dataset and run an analysis
2. **Set Up Monitoring**: Add UptimeRobot for uptime monitoring
3. **Custom Domain** (optional): Configure in Render dashboard
4. **Share Your App**: Your AI Data Analysis Agent is live! 🎉

---

## 🆘 Need Help?

If you encounter any issues:
1. Check Render documentation: https://render.com/docs
2. Review build logs in Render dashboard
3. Verify all environment variables are set correctly
4. Check GitHub Actions to ensure latest code is pushed

---

## 💡 Pro Tips

1. **Monitor Usage**: Check Render dashboard to track your 750 hours
2. **Use Secrets**: Never commit API keys to GitHub
3. **Test Locally First**: Run \docker-compose up\ before deploying
4. **Enable Auto-Deploy**: Render can auto-deploy when you push to GitHub

---

## ✅ Final Checklist

- [ ] Render account created
- [ ] Repository connected to Render
- [ ] Backend service deployed with environment variables
- [ ] Frontend service deployed with backend URL
- [ ] Both services showing "Live" status
- [ ] Frontend URL accessible in browser
- [ ] Backend health check returns 200 OK
- [ ] Test dataset upload and analysis
- [ ] **SUCCESS!** 🎉

---

**Your app will be live at:** \https://data-analysis-frontend.onrender.com\

Ready to deploy? Let me know if you need help with any step!
