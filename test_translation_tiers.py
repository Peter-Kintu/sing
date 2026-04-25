#!/usr/bin/env python
"""
Translation Service Diagnostic Test
Tests all three tiers of the translation fallback chain
"""
import os
import sys
import requests

print("=" * 70)
print("🔍 TRANSLATION SERVICE DIAGNOSTIC TEST")
print("=" * 70)

# Test parameters
TEST_TEXT = "Hello, how are you?"
SOURCE = "en"
TARGET = "lg"  # Luganda

NLLB_URL = os.getenv("NLLB_API_URL", "https://sing-nllb-translator.onrender.com/translate")
LIBRE_URL = "https://libretranslate.com/translate"
MYMEMORY_URL = "https://api.mymemory.translated.net/get"

print(f"\n📋 Configuration:")
print(f"  Text: '{TEST_TEXT}'")
print(f"  Route: {SOURCE} → {TARGET}")
print(f"  NLLB Endpoint: {NLLB_URL}")

# ═══════════════════════════════════════════════════════════════════════════
# TIER 1: NLLB
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🔄 TIER 1: Testing NLLB API")
print("=" * 70)

try:
    print(f"  → POST {NLLB_URL}")
    r = requests.post(
        NLLB_URL,
        json={"text": TEST_TEXT, "source": SOURCE, "target": TARGET},
        timeout=15
    )
    print(f"  ← Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        translated = data.get("translated")
        print(f"  ✓ NLLB SUCCESS")
        print(f"    Translated: '{translated}'")
    else:
        print(f"  ❌ NLLB ERROR")
        print(f"    Response: {r.text[:200]}")
except requests.Timeout:
    print(f"  ⏱ NLLB TIMEOUT (server likely cold-starting or insufficient RAM)")
except requests.ConnectionError:
    print(f"  ❌ NLLB CONNECTION ERROR")
    print(f"    Check NLLB_API_URL: {NLLB_URL}")
except Exception as e:
    print(f"  ❌ NLLB ERROR: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# TIER 2: LibreTranslate
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🔄 TIER 2: Testing LibreTranslate API")
print("=" * 70)

try:
    print(f"  → POST {LIBRE_URL}")
    r = requests.post(
        LIBRE_URL,
        json={
            "q": TEST_TEXT,
            "source": SOURCE,
            "target": TARGET,
            "format": "text"
        },
        timeout=6
    )
    print(f"  ← Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        translated = data.get("translatedText")
        print(f"  ✓ LibreTranslate SUCCESS")
        print(f"    Translated: '{translated}'")
    else:
        print(f"  ⚠️ LibreTranslate returned {r.status_code}")
        print(f"    Response: {r.text[:200]}")
except requests.Timeout:
    print(f"  ⏱ LibreTranslate TIMEOUT")
except requests.ConnectionError:
    print(f"  ❌ LibreTranslate CONNECTION ERROR")
except Exception as e:
    print(f"  ❌ LibreTranslate ERROR: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# TIER 3: MyMemory
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🔄 TIER 3: Testing MyMemory API")
print("=" * 70)

try:
    url = f"{MYMEMORY_URL}?q={TEST_TEXT}&langpair={SOURCE}|{TARGET}"
    print(f"  → GET {url[:70]}...")
    r = requests.get(url, timeout=5)
    print(f"  ← Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        if data.get("responseStatus") == 200:
            translated = data.get("responseData", {}).get("translatedText")
            print(f"  ✓ MyMemory SUCCESS")
            print(f"    Translated: '{translated}'")
        else:
            print(f"  ⚠️ MyMemory API error: {data.get('responseStatus')}")
    else:
        print(f"  ⚠️ MyMemory returned {r.status_code}")
except requests.Timeout:
    print(f"  ⏱ MyMemory TIMEOUT")
except requests.ConnectionError:
    print(f"  ❌ MyMemory CONNECTION ERROR")
except Exception as e:
    print(f"  ❌ MyMemory ERROR: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("✅ Diagnostic Complete")
print("=" * 70)
print("\n💡 Next Steps:")
print("1. If TIER 1 (NLLB) failed: Deploy translator/main.py to Render")
print("2. If TIER 1 times out: The NLLB service may be cold-starting")
print("3. If TIER 1 is 'unreachable': Check NLLB_API_URL env var")
print("4. TIER 2 (LibreTranslate) should always work (it's public)")
print("5. TIER 3 (MyMemory) is last resort (limited to 1000 words/day free)")

print("\n📊 Expected behavior:")
print("  • Tier 1 succeeds → Use NLLB translation (best for African languages)")
print("  • Tier 1 fails → Fall back to Tier 2")
print("  • Tier 2 fails → Fall back to Tier 3")
print("  • All fail → Return original text (last resort)")
