# Neo4j Aura Deployment Guide for CHRONOS

## 🎯 Quick Setup Guide

### Step 1: Create Neo4j Aura Account

1. **Visit Neo4j Aura Console**
   - Go to: https://console.neo4j.io/
   - Click "Start Free" or "Sign Up"
   - Create account with email

2. **Create New AuraDB Free Instance**
   - Click "New Instance" button
   - Choose: **"AuraDB Free"** (Forever free tier)
   - Configuration:
     - **Name**: `chronos-production`
     - **Region**: Choose closest to your Render deployment
       - US East (Virginia) - if Render is in Oregon/US
       - Europe (Frankfurt) - if Render is in Europe
     - **Version**: Latest (automatically selected)
   - Click "Create"

3. **IMPORTANT: Save Your Credentials** ⚠️

   After creation, you'll see credentials **ONLY ONCE**. Save these immediately!

   ```
   Connection URI: neo4j+s://xxxxx.databases.neo4j.io
   Username: neo4j
   Password: GeneratedPassword123
   Database: neo4j (default)
   ```

   **Download the .txt file** or copy to password manager NOW!

4. **Wait for Instance to Start**
   - Status will show "Running" (usually takes 1-2 minutes)
   - Green indicator means ready to use

---

### Step 2: Test Connection Locally

Before deploying to Render, test the connection on your local machine:

```bash
# Update your local .env file
cd /home/sidharth/Desktop/chronos
nano .env
```

Update these lines with your Aura credentials:
```env
NEO4J_URL=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YourAuraGeneratedPassword
```

Test locally:
```bash
cd webapp
python3 app.py
```

Upload a test file and verify it works!

---

### Step 3: Configure Render Environment Variables

1. **Go to Render Dashboard**
   - Navigate to: https://dashboard.render.com/
   - Select your web service (chronos-webapp)

2. **Add Environment Variables**
   - Click "Environment" in left sidebar
   - Click "Add Environment Variable"

   Add these three variables:

   | Key | Value | Type |
   |-----|-------|------|
   | `NEO4J_URL` | `neo4j+s://xxxxx.databases.neo4j.io` | Secret |
   | `NEO4J_USERNAME` | `neo4j` | Plain |
   | `NEO4J_PASSWORD` | `YourAuraPassword` | Secret |
   | `GOOGLE_API_KEY` | `your_google_api_key` | Secret |
   | `OPENAI_API_KEY` | `your_openai_key` | Secret |
   | `FUTUREHOUSE_API_KEY` | `your_futurehouse_key` | Secret |

3. **Important Settings**
   - Mark password fields as **"Secret"**
   - Render will automatically redeploy after saving

---

### Step 4: Configure Network Access (Optional Security)

**Option A: Allow All (Easiest for testing)**
1. In Neo4j Aura Console → Select your instance
2. Click "Network Access" tab
3. Keep default: `0.0.0.0/0` (allows all IPs)

**Option B: Restrict to Render IPs (More Secure)**
1. Get Render's outbound IPs:
   - Render doesn't guarantee static IPs on free tier
   - For production, upgrade to paid tier for static IPs
2. Add Render IPs to allowlist in Aura

For now, keep **Option A** for simplicity.

---

### Step 5: Verify Deployment

1. **Check Render Logs**
   ```
   Render Dashboard → Your Service → Logs
   ```

   Look for successful connection messages:
   ```
   ✅ Neo4j connection established!
   ```

2. **Test Upload**
   - Visit your deployed URL: `https://your-app.onrender.com`
   - Upload a test PDF/image
   - Verify pipeline completes without Neo4j errors

3. **Check Neo4j Aura**
   - Aura Console → Your Instance → Query
   - Run query to see your data:
   ```cypher
   MATCH (n) RETURN count(n) as node_count
   ```

---

## 🔍 Troubleshooting

### Error: "Connection refused"
**Cause**: Neo4j URL is wrong or instance isn't running

**Fix**:
1. Check Aura instance status (should be green "Running")
2. Verify `NEO4J_URL` starts with `neo4j+s://` (note the `+s`)
3. Copy-paste URL directly from Aura console (no typos)

### Error: "Authentication failed"
**Cause**: Wrong password

**Fix**:
1. In Aura Console → Instance → Reset Password
2. Get new password
3. Update Render environment variable

### Error: "SSL/TLS handshake failed"
**Cause**: Using `neo4j://` instead of `neo4j+s://`

**Fix**:
- Change URL protocol to `neo4j+s://` (secure connection required for Aura)

### Instance Paused
**Cause**: Aura Free tier pauses after 3 days of inactivity

**Fix**:
- Click "Resume" in Aura Console
- Instance will restart in ~30 seconds

---

## 📊 Neo4j Aura Free Tier Limits

| Feature | Limit |
|---------|-------|
| **Storage** | 50 MB (sufficient for 1000s of nodes) |
| **Memory** | 1 GB RAM |
| **Instances** | 1 free instance per account |
| **Databases** | Multiple databases per instance ✅ |
| **Uptime** | Pauses after 3 days inactive |
| **SSL/TLS** | Required (neo4j+s://) |
| **Backups** | Automatic daily backups |

For CHRONOS: 50MB is enough for ~5000-10000 hypotheses!

---

## 💡 Best Practices

### Database Naming Convention
Each user upload gets a unique database:
```python
# Automatic in our code
database_name = f"chronos_{filename}_{timestamp}"
```

Example:
- `chronos_spine_study_20251104_120000`
- `chronos_medical_text_20251104_120530`

### Cleanup Old Databases
Aura Free has 50MB limit. Periodically clean old databases:

```cypher
// List all databases
SHOW DATABASES

// Drop old database (in Aura Console Query tab)
DROP DATABASE chronos_old_20251001_000000
```

### Monitor Usage
- Aura Console → Instance → Metrics
- Watch storage usage
- Each analysis ~1-5MB depending on complexity

---

## 🎉 Success Checklist

- [ ] Neo4j Aura account created
- [ ] Free instance provisioned and running (green status)
- [ ] Credentials saved securely
- [ ] Local .env updated and tested
- [ ] Render environment variables configured
- [ ] Deployment successful (check logs)
- [ ] Test upload completed without errors
- [ ] Data visible in Aura Query console

---

## 📞 Support

**Neo4j Aura Issues:**
- Documentation: https://neo4j.com/docs/aura/
- Community: https://community.neo4j.com/
- Support: support@neo4j.com

**Render Issues:**
- Documentation: https://render.com/docs
- Support: https://render.com/support

**CHRONOS Issues:**
- Check application logs in Render Dashboard
- Verify all API keys are set correctly
