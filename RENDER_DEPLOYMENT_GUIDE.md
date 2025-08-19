# Render.com Deployment Guide for Health Monitoring System

This guide provides step-by-step instructions to deploy your Health Monitoring System on Render.com.

## Prerequisites

- GitHub account with your code repository
- Render.com account (free tier is sufficient)
- Git installed locally

## Step 1: Prepare Your Repository

1. **Ensure all files are committed to Git:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify required files exist:**
   - `render.yaml` - Render configuration
   - `start.sh` - Startup script
   - `requirements.txt` - Python dependencies
   - `.gitignore` - Excludes unnecessary files
   - All your application code

## Step 2: Sign Up/Login to Render

1. Go to [render.com](https://render.com)
2. Sign up for a free account or login
3. Connect your GitHub account when prompted

## Step 3: Deploy Your Application

### Option A: Using render.yaml (Recommended)

1. Click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Render will automatically detect `render.yaml`
4. Review the configuration and click "Apply"
5. Your app will start deploying automatically

### Option B: Manual Setup

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `health-monitor-api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && python train_models.py`
   - **Start Command**: `./start.sh` or `bash start.sh`
   - **Instance Type**: Free

## Step 4: Environment Variables (Optional)

If you need to set environment variables:

1. Go to your service dashboard
2. Click "Environment" in the left sidebar
3. Add variables:
   ```
   DEBUG=false
   ENVIRONMENT=production
   # Add any other variables you need
   ```

## Step 5: Monitor Deployment

1. Watch the deployment logs in the Render dashboard
2. The deployment process will:
   - Install dependencies
   - Train ML models (first deployment)
   - Start the FastAPI server

3. Look for these success messages:
   ```
   ==> Starting Health Monitoring System...
   ==> Model training completed successfully!
   ==> Starting FastAPI server on port $PORT...
   ```

## Step 6: Access Your Application

Once deployed, you'll get a URL like: `https://health-monitor-api.onrender.com`

Test your endpoints:
- API Documentation: `https://health-monitor-api.onrender.com/docs`
- Health Check: `https://health-monitor-api.onrender.com/api/v1/health`
- Root: `https://health-monitor-api.onrender.com/`

## Step 7: Frontend Configuration

To connect your frontend:

1. Update `frontend/script.js` to use your Render URL:
   ```javascript
   const API_BASE_URL = 'https://health-monitor-api.onrender.com';
   ```

2. You can either:
   - Host frontend separately (GitHub Pages, Netlify, Vercel)
   - Serve it through FastAPI (add static file serving)

## Troubleshooting

### Common Issues

1. **Build fails with "ModuleNotFoundError"**
   - Check `requirements.txt` has all dependencies
   - Ensure correct Python version

2. **"Port already in use" error**
   - This shouldn't happen on Render
   - Check you're using `$PORT` environment variable

3. **Models not found error**
   - Check `start.sh` is executable
   - Verify model training completes successfully
   - Check build logs for training errors

4. **Out of memory errors**
   - Free tier has 512MB RAM limit
   - Consider model optimization
   - Use lighter TensorFlow builds

### Viewing Logs

1. Go to your service dashboard
2. Click "Logs" in the left sidebar
3. Filter by:
   - Deploy logs (build process)
   - Service logs (runtime logs)

### Performance Optimization

1. **Cold Starts**: Free tier services sleep after 15 minutes of inactivity
   - First request after sleep takes 30-60 seconds
   - Consider upgrading for always-on service

2. **Model Loading**: Large models may cause slow starts
   - Consider model quantization
   - Use TensorFlow Lite models
   - Cache predictions when possible

## Maintenance

### Updating Your Application

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push origin main
   ```
3. Render auto-deploys from main branch

### Retraining Models

To retrain models on Render:
1. SSH into your service (paid feature)
2. Or trigger rebuild by pushing empty commit:
   ```bash
   git commit --allow-empty -m "Retrain models"
   git push origin main
   ```

### Monitoring

1. Set up health check alerts in Render dashboard
2. Monitor service metrics (CPU, Memory, Response time)
3. Check logs regularly for errors

## Advanced Configuration

### Custom Domain

1. Go to Settings → Custom Domains
2. Add your domain
3. Configure DNS as instructed

### Redis Cache (Optional)

1. Create Redis instance on Render
2. Copy connection URL
3. Set `REDIS_URL` environment variable

### Scheduled Jobs

For periodic model retraining:
1. Create a Cron Job service
2. Set schedule (e.g., weekly)
3. Run `python train_models.py`

## Cost Considerations

### Free Tier Limits
- 750 hours/month (enough for 1 service 24/7)
- 512MB RAM
- Shared CPU
- Auto-sleep after 15 min inactivity

### When to Upgrade
- Need more RAM for larger models
- Want always-on service (no cold starts)
- Need background workers
- Require custom domains with SSL

## Security Best Practices

1. **Never commit sensitive data:**
   - Use environment variables for secrets
   - Keep `.env` in `.gitignore`

2. **API Security:**
   - Consider adding API authentication
   - Implement rate limiting
   - Use HTTPS (automatic on Render)

3. **Dependencies:**
   - Keep packages updated
   - Review security advisories

## Next Steps

1. **Test thoroughly** after deployment
2. **Set up monitoring** and alerts
3. **Optimize performance** based on usage
4. **Add authentication** if needed
5. **Scale** as your user base grows

## Support Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Your App Logs](https://dashboard.render.com) (after deployment)

## Quick Commands Reference

```bash
# Check deployment status
curl https://your-app.onrender.com/api/v1/health

# Test prediction endpoint
curl -X POST https://your-app.onrender.com/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 30, "gender": "male", "heart_rate": 70, ...}'

# View API documentation
open https://your-app.onrender.com/docs
```

---

Happy Deploying! 🚀
