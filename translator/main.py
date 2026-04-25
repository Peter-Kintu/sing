"""
NLLB translation microservice — deploy this to Render Starter ($7/mo).
Handles African languages that LibreTranslate does not support (Luganda, etc.).

Start command:
    uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI(title="NLLB Translation API")

# ---------------------------------------------------------------------------
# Model — loaded once at startup, kept in RAM (~1.2 GB for 600M distilled)
# ---------------------------------------------------------------------------
_MODEL_NAME = "facebook/nllb-200-distilled-600M"
_CACHE_DIR = os.getenv("TRANSFORMERS_CACHE", "/opt/render/project/.cache/huggingface")

print(f"Loading model {_MODEL_NAME} …")
MODEL = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME, cache_dir=_CACHE_DIR)
TOKENIZER = AutoTokenizer.from_pretrained(_MODEL_NAME, cache_dir=_CACHE_DIR)
print("Model loaded ✓")

# ---------------------------------------------------------------------------
# Language code map  (short code → NLLB Flores-200 code)
# Keys use ISO 639-1 (2-letter) where it exists, ISO 639-3 (3-letter) otherwise.
# ---------------------------------------------------------------------------
LANGS: dict[str, str] = {
    # ── Source / pivot ───────────────────────────────────────────────────────
    "en": "eng_Latn",       # English

    # ── Ugandan languages ────────────────────────────────────────────────────
    "lg":  "lug_Latn",      # Luganda        (Central, Buganda)
    "nyn": "nyn_Latn",      # Runyankole     (Southwest – Ankole)
    "ach": "ach_Latn",      # Acholi         (North)
    "lgg": "lgg_Latn",      # Lugbara        (Northwest – West Nile)
    "teo": "teo_Latn",      # Ateso / Teso   (Northeast)
    "xog": "xog_Latn",      # Lusoga / Soga  (East – Busoga)
    "ttj": "ttj_Latn",      # Rutooro / Tooro (West)
    "nyo": "nyo_Latn",      # Runyoro        (West – Bunyoro)
    "laj": "laj_Latn",      # Langi          (North-Central)
    "alz": "alz_Latn",      # Alur           (Northwest – West Nile)

    # ── East Africa ──────────────────────────────────────────────────────────
    "sw":  "swa_Latn",      # Swahili        (Tanzania, Kenya, Uganda, DRC)
    "luo": "luo_Latn",      # Luo / Dholuo   (Kenya, Tanzania)
    "luy": "luy_Latn",      # Luhya / Luyia  (Kenya)
    "kam": "kam_Latn",      # Kamba          (Kenya)
    "ki":  "kik_Latn",      # Kikuyu / Gikuyu (Kenya)
    "rw":  "kin_Latn",      # Kinyarwanda    (Rwanda)
    "rn":  "run_Latn",      # Kirundi        (Burundi)
    "so":  "som_Latn",      # Somali
    "om":  "gaz_Latn",      # Oromo / Borana-Arsi-Guji (Ethiopia)
    "am":  "amh_Ethi",      # Amharic        (Ethiopia)
    "ti":  "tir_Ethi",      # Tigrinya       (Ethiopia, Eritrea)

    # ── West Africa ───────────────────────────────────────────────────────────
    "ha":  "hau_Latn",      # Hausa          (Nigeria, Niger)
    "yo":  "yor_Latn",      # Yoruba         (Nigeria)
    "ig":  "ibo_Latn",      # Igbo           (Nigeria)
    "fuv": "fuv_Latn",      # Nigerian Fulfulde (Nigeria, Cameroon)
    "bm":  "bam_Latn",      # Bambara        (Mali)
    "dyu": "dyu_Latn",      # Dyula          (Côte d'Ivoire, Burkina Faso)
    "mos": "mos_Latn",      # Moore / Mossi  (Burkina Faso)
    "wo":  "wol_Latn",      # Wolof          (Senegal, Gambia)
    "tw":  "twi_Latn",      # Twi            (Ghana)
    "ak":  "aka_Latn",      # Akan           (Ghana)
    "ee":  "ewe_Latn",      # Ewe            (Ghana, Togo)
    "fon": "fon_Latn",      # Fon            (Benin)
    "kbp": "kbp_Latn",      # Kabiyè         (Togo)

    # ── Central Africa ───────────────────────────────────────────────────────
    "ln":  "lin_Latn",      # Lingala        (DRC, Congo)
    "kg":  "kon_Latn",      # Kongo / Kikongo (DRC, Congo, Angola)
    "lua": "lua_Latn",      # Tshiluba / Luba-Kasai (DRC)
    "kmb": "kmb_Latn",      # Kimbundu       (Angola)
    "cjk": "cjk_Latn",      # Chokwe         (Angola, DRC)
    "sg":  "sag_Latn",      # Sango          (Central African Republic)

    # ── Southern Africa ──────────────────────────────────────────────────────
    "zu":  "zul_Latn",      # Zulu           (South Africa)
    "xh":  "xho_Latn",      # Xhosa          (South Africa)
    "st":  "sot_Latn",      # Sesotho / Southern Sotho (Lesotho, South Africa)
    "nso": "nso_Latn",      # Sepedi / Northern Sotho (South Africa)
    "tn":  "tsn_Latn",      # Setswana / Tswana (Botswana, South Africa)
    "ss":  "ssw_Latn",      # Swati / Swazi  (Eswatini, South Africa)
    "ve":  "ven_Latn",      # Tshivenda / Venda (South Africa)
    "nr":  "nbl_Latn",      # South Ndebele  (South Africa)
    "ny":  "nya_Latn",      # Chichewa / Nyanja (Malawi, Zambia, Mozambique)
    "sn":  "sna_Latn",      # Shona          (Zimbabwe)
    "af":  "afr_Latn",      # Afrikaans      (South Africa, Namibia)

    # ── North Africa ─────────────────────────────────────────────────────────
    "ary": "ary_Arab",      # Moroccan Darija (Morocco)

    # ── Indian Ocean ─────────────────────────────────────────────────────────
    "mg":  "plt_Latn",      # Malagasy       (Madagascar)

    # ── Additional Languages for UI Support ──────────────────────────────────
    "fr":  "fra_Latn",      # French
    "es":  "spa_Latn",      # Spanish
    "de":  "deu_Latn",      # German
    "ar":  "arb_Arab",      # Arabic (Standard)
    "zh":  "zho_Hans",      # Chinese (Simplified)
    "ja":  "jpn_Jpan",      # Japanese

    # ── Additional African Languages ─────────────────────────────────────────
    "pcm": "pcm_Latn",      # Nigerian Pidgin (Nigeria)
    "tzm": "tzm_Latn",      # Central Atlas Tamazight (Morocco)
    "kab": "kab_Latn",      # Kabyle (Algeria)
    "ber": "tzm_Latn",      # Berber (Morocco) - using Tamazight as proxy
    "ff":  "fuv_Latn",      # Fulah (West Africa)
    "kr":  "kri_Latn",      # Krio (Sierra Leone)
    "nqo": "nqo_Nkoo",      # N'Ko (Mali, Guinea)
    "vai": "vai_Vaii",      # Vai (Liberia, Sierra Leone)
    "bci": "bci_Latn",      # Baoulé (Côte d'Ivoire)
    "dag": "dag_Latn",      # Dagbani (Ghana)
    "gaa": "gaa_Latn",      # Ga (Ghana)
    "gur": "gur_Latn",      # Gurma (Burkina Faso)
    "kpe": "kpe_Latn",      # Kpelle (Liberia)
    "men": "men_Latn",      # Mende (Sierra Leone)
    "sus": "sus_Latn",      # Susu (Guinea)
    "tem": "tem_Latn",      # Temne (Sierra Leone)
    "efi": "efi_Latn",      # Efik (Nigeria)
    "ibb": "ibb_Latn",      # Ibibio (Nigeria)
    "iso": "iso_Latn",      # Isoko (Nigeria)
    "tiv": "tiv_Latn",      # Tiv (Nigeria)
    "bin": "bin_Latn",      # Edo (Nigeria)
    "ann": "ann_Latn",      # Obolo (Nigeria)
    "gde": "gde_Latn",      # Gude (Nigeria, Cameroon)
    "jbu": "jbu_Latn",      # Jukun (Nigeria)
    "kcg": "kcg_Latn",      # Tyap (Nigeria)
    "mcp": "mcp_Latn",      # Makaa (Cameroon)
    "mfq": "mfq_Latn",      # Moba (Togo)
    "nmg": "nmg_Latn",      # Kwasio (Cameroon)
    "nnh": "nnh_Latn",      # Ngiemboon (Cameroon)
    "pbi": "pbi_Latn",      # Parkwa (Nigeria)
    "pil": "pil_Latn",      # Yom (Nigeria)
    "sba": "sba_Latn",      # Ngambay (Chad)
}


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------
class TranslateRequest(BaseModel):
    text: str
    target: str
    source: str = "en"


class TranslateResponse(BaseModel):
    translated: str
    target: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """Root endpoint — Render pings this for health checks."""
    return {"message": "NLLB API running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "model": _MODEL_NAME}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    # Empty / whitespace-only input — return early, no model call
    if not req.text.strip():
        return TranslateResponse(translated="", target=req.target)

    if req.target not in LANGS:
        raise HTTPException(400, f"Unsupported target '{req.target}'. Supported: {list(LANGS.keys())}")
    if req.source not in LANGS:
        raise HTTPException(400, f"Unsupported source '{req.source}'.")

    try:
        src_flores = LANGS[req.source]
        tgt_flores = LANGS[req.target]

        TOKENIZER.src_lang = src_flores
        encoded = TOKENIZER(
            req.text[:500],          # Hard limit prevents RAM spike
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )
        generated = MODEL.generate(
            **encoded,
            forced_bos_token_id=TOKENIZER.lang_code_to_id[tgt_flores],
            max_length=256,
            num_beams=1,             # Greedy decode — ~30% less RAM, 2× faster
        )
        translated = TOKENIZER.batch_decode(generated, skip_special_tokens=True)[0]
        return TranslateResponse(translated=translated, target=req.target)
    except Exception as e:
        print(f"Translation error: {e}")
        raise HTTPException(500, "Translation failed")
