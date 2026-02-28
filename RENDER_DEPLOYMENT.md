# Render Deployment Guide

## Prerequisites

1. **MongoDB Atlas Account** (Free)
   - Sign up at https://www.mongodb.com/cloud/atlas
   - Create a free M0 cluster
   - Create a database user
   - Whitelist all IPs (0.0.0.0/0)
   - Get connection string

2. **Render Account** (Free)
   - Sign up at https://render.com
   - Connect your GitHub account

3. **GitHub Repository**
   - Push your code to GitHub

## Deployment Steps

### Step 1: Set up MongoDB Atlas

1. Go to https://cloud.mongodb.com
2. Create a new project: "DeepVerify"
3. Build a cluster (M0 Free tier)
4. Create database user:
   - Username: deepverify
   - Password: (generate strong password)
5. Network Access → Add IP: 0.0.0.0/0 (Allow from anywhere)
6. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy connection string
   - Replace `<password>` with your password
   - Example: `mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/deepverify`

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 3: Deploy on Render

1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect render.yaml
5. Click "Apply"

### Step 4: Configure Environment Variables

After deployment starts, add these environment variables:

**For deepverify-backend:**

- `MONGO_URI`: Your MongoDB Atlas connection string
- `FRONTEND_ORIGINS`: https://deepverify-frontend.onrender.com (update with actual URL)

**For deepverify-frontend:**

- `NEXT_PUBLIC_API_URL`: https://deepverify-backend.onrender.com (update with actual URL)

### Step 5: Wait for Deployment

- Backend: ~5-10 minutes
- Frontend: ~3-5 minutes
- Redis: ~1 minute

### Step 6: Update CORS

Once both services are deployed:

1. Get the actual frontend URL from Render dashboard
2. Update `FRONTEND_ORIGINS` in backend environment variables
3. Trigger a redeploy of the backend

## Important Notes

### Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free per service

### Ollama Chatbot

The Ollama chatbot will NOT work on Render because:

- Ollama requires local installation
- Render doesn't support running Ollama

**Options:**

- Disable the chatbot feature
- Use OpenAI API instead
- Use Anthropic Claude API
- Host Ollama on a separate VPS

### File Storage

- Render's filesystem is ephemeral
- ML models (model_final.pkl, tfidf_final.pkl) are included in the build
- Don't store user uploads on filesystem

## Troubleshooting

### Backend won't start

- Check MongoDB connection string
- Verify all environment variables are set
- Check build logs for errors

### Frontend can't connect to backend

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running

### Database connection failed

- Verify MongoDB Atlas IP whitelist includes 0.0.0.0/0
- Check connection string format
- Verify database user credentials

## Monitoring

- View logs in Render dashboard
- Set up alerts for service failures
- Monitor response times

## Costs

- Free tier: $0/month
- Paid tier (if needed): $7/month per service

## Support

- Render Docs: https://render.com/docs
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com
