# CHRONOS Render Deployment Guide

## Prerequisites
- GitHub account with your chronos repository pushed
- Render account (https://render.com)

## Step 1: Set Up PostgreSQL Database on Render

1. Log in to Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `chronos-database`
   - **Database**: `chronos_db`
   - **User**: `chronos_user` (auto-generated is fine)
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click **"Create Database"**
5. **IMPORTANT**: Copy the **Internal Database URL** (starts with `postgres://`)
   - You'll need this for the web service

## Step 2: Deploy Web Service on Render

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `chronos-webapp`
   - **Region**: Same as database
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave empty (root of repo)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd webapp && gunicorn app:app` (or leave empty, it will use Procfile)

4. **Environment Variables** - Click "Advanced" and add these:

   ```
   DATABASE_URL = [Paste the Internal Database URL from Step 1]
   SECRET_KEY = [Generate a random secure key, e.g., openssl rand -hex 32]
   GOOGLE_API_KEY = AIzaSyBd4zmuk2nL11XJycQpmP_5AKqVXUV0E6I
   NEO4J_URL = neo4j+s://4fb49145.databases.neo4j.io
   NEO4J_USERNAME = neo4j
   NEO4J_PASSWORD = FTZFJK90-rHUEb6GM3L6srXlA6mM5nrxnJ8XFBILEmw
   ```

   **IMPORTANT**: Generate a new SECRET_KEY for production:
   ```bash
   openssl rand -hex 32
   ```

5. **Instance Type**: Free (or paid for production)

6. Click **"Create Web Service"**

## Step 3: Verify Deployment

1. Wait for the build to complete (5-10 minutes)
2. Render will provide a URL like: `https://chronos-webapp.onrender.com`
3. Visit the URL and verify:
   - Homepage loads correctly
   - Can register a new user
   - Can login
   - Upload functionality works
   - Community dashboard shows members

## Important Notes

### Database Persistence
✅ **With PostgreSQL**: All user data, ratings, and comments persist across deploys
❌ **Without PostgreSQL**: Data would be lost on every restart (Render has ephemeral filesystem)

### File Uploads
⚠️ **Uploaded files and results are ephemeral** on Render's free tier
- Files will be deleted on each deploy or after 24h of inactivity
- For production, consider using:
  - **Render Disk** (paid add-on for persistent storage)
  - **AWS S3 / Cloudinary** for file storage

### Environment Variables Security
🔒 Never commit `.env` to git - it contains sensitive API keys
🔒 Always set environment variables through Render dashboard
🔒 Use different SECRET_KEY for production vs development

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies in requirements.txt are compatible
- Check Python version (Render uses Python 3.7+ by default)

### Database Connection Errors
- Verify DATABASE_URL is set correctly
- Ensure PostgreSQL database is running
- Check if database is in same region as web service

### 502 Bad Gateway
- Check application logs in Render dashboard
- Verify gunicorn is starting correctly
- Check if port binding is correct (Render provides PORT env var automatically)

### Application Errors
- Check logs: Render Dashboard → Your Service → Logs
- Look for Python tracebacks
- Verify all environment variables are set

## Updating Your Deployment

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. Render will automatically detect and redeploy

## Manual Redeploy

If you need to manually redeploy:
1. Go to Render Dashboard
2. Select your web service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

## Monitoring

- **Logs**: Render Dashboard → Your Service → Logs (real-time)
- **Metrics**: Render Dashboard → Your Service → Metrics
- **Database**: Render Dashboard → PostgreSQL → Metrics

## Cost Estimate (Free Tier)

- PostgreSQL Database: Free (90 days, then $7/month)
- Web Service: Free (spins down after 15 min inactivity)
- Storage: Ephemeral (use Render Disk for $1/GB/month)

## Production Recommendations

For production with real users:

1. **Upgrade to Paid Plans**:
   - Web Service: $7/month (no spin down, better performance)
   - PostgreSQL: $7/month (persistent, backups)

2. **Add Persistent Storage**:
   - Render Disk: Mount at `/opt/render/project/uploads` and `/opt/render/project/results`
   - Or use S3/Cloudinary for file uploads

3. **Security Enhancements**:
   - Strong SECRET_KEY (at least 32 chars, random)
   - Enable HTTPS (automatic on Render)
   - Rate limiting for API endpoints
   - Add CORS if building separate frontend

4. **Monitoring**:
   - Enable Render notifications for crashes
   - Set up error tracking (Sentry)
   - Monitor database size

## Support

If you encounter issues:
1. Check Render documentation: https://render.com/docs
2. Review application logs in Render dashboard
3. Check GitHub repository issues
