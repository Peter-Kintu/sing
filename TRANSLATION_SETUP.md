# Translation Service Setup Guide 🌍

## Problem: Translation Not Working

The translated text shows as the original text because the NLLB API endpoint is either not deployed or not configured correctly.

## Solution: Two-Service Architecture

You need **TWO separate Render deployments**:

### Service 1: NLLB FastAPI Translator (translator/main.py)
- **Purpose:** Handles African language translations
- **Framework:** FastAPI (uvicorn)
- **Languages:** 60+ African languages + global languages
- **Model:** NLLB-200 (1.2GB, runs in-memory)

### Service 2: Django Web App (sing/settings.py)
- **Purpose:** Web UI + translation routing
- **Framework:** Django + REST Framework
- **Integrates with:** NLLB service + LibreTranslate + MyMemory

---

## Deployment Steps

### Step 1: Deploy NLLB Translator to Render

1. **Create a new Render service** (separate from your Django app)
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your `sing` repository

2. **Configure the NLLB Service:**
   - **Name:** `sing-nllb-translator` (or similar)
   - **Root Directory:** `translator/`
   - **Environment:** Python 3.10
   - **Build Command:** `pip install -r translator/requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Plan:** Starter (at minimum) or higher (recommended: Standard at $7/mo for RAM)

3. **Set Environment Variables for NLLB Service:**
   - `TRANSFORMERS_CACHE`: `/opt/render/project/.cache/huggingface`
   - This ensures the 1.2GB model is cached and not re-downloaded on every restart

4. **Wait for deployment** (~5-10 minutes)
   - Check the logs to ensure the model loads: `Model loaded ✓`
   - Note the service URL (e.g., `https://sing-nllb-translator.onrender.com`)

---

### Step 2: Update Django App to Use NLLB Service

1. **Set the Environment Variable on your Django service:**
   - Go to your Django service settings on Render
   - Add this environment variable:
     ```
     NLLB_API_URL=https://sing-nllb-translator.onrender.com/translate
     ```
   - Replace `sing-nllb-translator` with your actual NLLB service name

2. **No code changes needed** — the Django app already uses this env var

3. **Redeploy** the Django service to pick up the new env var

---

### Step 3: Test the Translation

#### Quick Health Check:
```bash
curl https://sing-nllb-translator.onrender.com/
# Expected: {"message": "NLLB API running", "docs": "/docs"}
```

#### Test a Translation:
```bash
curl -X POST https://sing-nllb-translator.onrender.com/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source": "en", "target": "lg"}'
# Expected: {"translated": "Wasuze", "target": "lg"}
```

#### Test the Django UI:
- Go to `https://sing-sjf2.onrender.com/translate/`
- Enter text, select English → Luganda
- Click "Translate"
- Should show the Luganda translation

---

## Fallback Chain (Automatic)

If translation fails at any stage, the system automatically:

```
TIER 1: NLLB (African languages)
  ↓ (if NLLB_API_URL not set OR timeout/error)
TIER 2: LibreTranslate (Global languages)
  ↓ (if LibreTranslate fails)
TIER 3: MyMemory (Universal fallback)
  ↓ (if all fail)
Return original text (with console logs)
```

---

## Troubleshooting

### Issue: "Translated Text" shows original text
**Cause:** NLLB service not running or unreachable  
**Fix:**
1. Verify `NLLB_API_URL` env var is set correctly
2. Test the health endpoint: `curl https://sing-nllb-translator.onrender.com/`
3. Check NLLB service logs for errors
4. If it says "CPU 0%" → Render suspended it (needs a paid plan)

### Issue: "Unsupported language" error
**Cause:** Language code not in `translator/main.py` LANGS dict  
**Fix:** Already fixed! All 60+ languages are now supported.

### Issue: NLLB is very slow (30+ seconds)
**Cause:** 
- Cold start (first request after service wakes up)
- Insufficient RAM on Starter plan (shared CPU)
**Fix:**
- Upgrade to "Standard" plan (~$7/mo) for dedicated RAM
- Users can wait — caching prevents repeated delays

### Issue: "Connection refused" or "Failed to connect"
**Cause:** NLLB service URL is wrong or deployment failed  
**Fix:**
1. Check exact URL from Render dashboard
2. Ensure no typos in `NLLB_API_URL` env var
3. Redeploy both services

---

## Performance Tips

1. **Caching:** Translations are cached for 24h — repeated requests are instant
2. **Batching:** If translating 20+ posts, add 0.5s delay between requests
3. **Character Limit:** Max 500 chars per request (memory safety on Render)
4. **Lazy Loading:** Only translate when user clicks "Translate" button

---

## Architecture Diagram

```
User Browser
    ↓
[Django Web App] (sing-sjf2.onrender.com)
    ↓
[Translation Router] (translate_smart in views.py)
    ├→ TIER 1: NLLB Service (sing-nllb-translator.onrender.com) — African languages
    ├→ TIER 2: LibreTranslate API — Global languages  
    ├→ TIER 3: MyMemory API — Fallback
    └→ Cache (Redis/SQLite) — 24h caching
```

---

## Environment Variables Summary

### NLLB Service (translator/main.py):
```
TRANSFORMERS_CACHE=/opt/render/project/.cache/huggingface
```

### Django Service (sing/):
```
NLLB_API_URL=https://sing-nllb-translator.onrender.com/translate
SECRET_KEY=<your-key>
DEBUG=False
```

---

## Deployment Checklist

- [ ] Deploy `translator/main.py` to separate Render service
- [ ] Wait for NLLB service to finish loading model
- [ ] Set `NLLB_API_URL` on Django service
- [ ] Redeploy Django service
- [ ] Test `/translate/` UI
- [ ] Verify translations work
- [ ] Check server logs for "TIER 1/2/3" messages

Once complete, your translation system is fully functional! 🎉
