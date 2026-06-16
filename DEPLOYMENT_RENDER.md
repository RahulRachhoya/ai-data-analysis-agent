## ☁️ Deployment on Render (Free Tier)

This project is configured for easy deployment on Render.com using Docker.

### Step-by-step

1. **Fork or push this repo** to your GitHub.

2. **Deploy the Backend first**
   - Go to [Render Dashboard](https://dashboard.render.com) → New → Blueprint
   - Connect this repo
   - It will create two services from `render.yaml`:
     - `data-analysis-backend` (FastAPI)
     - `data-analysis-frontend` (Next.js)
   - **Important**: After the backend deploys, copy its **Public URL** (it will look like `https://data-analysis-backend-abc123.onrender.com` or with a random suffix like `-745c`).

3. **Set the correct Backend URL for the Frontend**
   - Go to the `data-analysis-frontend` service in Render.
   - Environment → Add Environment Variable:
     ```
     NEXT_PUBLIC_API_URL = https://data-analysis-backend-abc123.onrender.com   (use the real one from step 2, including any suffix)
     ```
   - Also set the same value under the service's "Build" settings if using build args.
   - **Trigger a new deploy** of the frontend (changing the env var requires a rebuild so the URL is baked into the Next.js bundle).

4. **Add your secrets** (required for the AI agent features)
   - In `data-analysis-backend` service → Environment:
     - `GROQ_API_KEY` (or your LLM key)
     - `E2B_API_KEY`
   - These are marked `sync: false` in render.yaml so you must enter them manually in the dashboard.

5. **Test in production**
   - Open the frontend URL.
   - Try uploading a small CSV via the UI.
   - If you still see "NetworkError when attempting to fetch resource" or 404:
     - The `NEXT_PUBLIC_API_URL` in the built frontend is still pointing to the wrong host.
     - Visit your backend URL directly in the browser: `https://<your-backend-url>/health` — it should return `{"status":"ok"}`.
     - If the backend health returns 404 or "no-server", the backend service is not active (check its logs and status in Render dashboard — free tier services sleep after 15 minutes of inactivity).

### Why this happens

Next.js embeds `NEXT_PUBLIC_*` variables at **build time**. If the placeholder `https://data-analysis-backend.onrender.com` (or an old suffixed URL) is used during the frontend build, the browser will try to call a non-existent or sleeping Render hostname, resulting in NetworkError / 404 from Render's router (x-render-routing: no-server).

The backend itself is fine (the /api/data/upload route exists and works when the service is live).

### After fixing the URL

- Redeploy frontend.
- The improved error messages in the UI (from recent updates) will now clearly tell you if the API base URL looks like a placeholder.
