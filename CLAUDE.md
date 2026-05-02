# Sri Durga Saptashati - Project Context

## What this is
Interactive website for learning and chanting Sri Durga Saptashati (Devi Mahatmyam / Chandi Path) - the heart of Shakta scripture, 700 verses across 13 chapters.

## Sacred Text - Handle With Utmost Care
- This is Markandeya Purana scripture (chapters 81-93). Every Sanskrit syllable matters.
- Source of truth: `source_durga700.itx` (Sanskrit Documents) + `source_kunjika.itx` for Siddha Kunjika
- Canonical secondary: Gita Press Gorakhpur edition for cross-verification
- NEVER edit `data.js` manually - regenerate via `build_data.py`
- NEVER guess Sanskrit text. If unsure, check source_*.itx or fetch from Sanskrit Documents.

## Structure
- 13 chapters arranged as 1 + 3 + 9 (the 3 charitas):
  - Prathama (Ch 1) - Mahakali - Madhu-Kaitabha vadh
  - Madhyama (Ch 2-4) - Mahalakshmi - Mahishasura vadh (NEVER interrupt mid-recitation)
  - Uttama (Ch 5-13) - Mahasaraswati - Shumbha-Nishumbha vadh
- 700 mantras = 537 sloka + 38 ardha-sloka + 66 khanda + 57 uvacha + 2 punarukta (= 518 actual verses)

## Angas Included (in `data.js`)
**Pre-paath:** Saptashloki Durga, Chandika Dhyana, Navarna Mantra (with breakdown), Argala Stotram, Keelaka Stotram, Devi Kavacham
**Post-paath:** Devi Suktam (Vagambhrini Suktam), Siddha Kunjika Stotram, Aparadha Kshamapana Stotram

## Angas NOT Yet Included (potential v2 additions)
- Devi Atharvashirsha (Upanishadic invocation)
- Ratri Suktam (Vedic + Tantric versions)
- Pradhanika Rahasya
- Vaikritika Rahasya
- Murti Rahasya
- Saptashati Nyasa
- Durga Dwatrimsha Namamala
- Devi Ashtottara Shatanama Stotram

If adding these later: source from sanskritdocuments.org/doc_devii/ where possible. Hindupedia has IAST for the rahasyas - convert to Devanagari via indic_transliteration. Always cross-verify against Gita Press.

## Audio Source
Primary: Vaidic Dharma Sansthan (Om Swami ji's organisation), Bangalore Ashram - regular Durga Saptashati Parayanam events on YouTube. Currently embedded: Jan 2 2026 Parayanam (https://youtu.be/IVrC7uvVICQ).
Note: Unlike the Rudram site (which has a single Om Swami production with anuvaka timestamps), Durga Saptashati does not have a single canonical production - the Bangalore Ashram does live parayanams during Navratri. If a new full production becomes available, swap the embedded URL.

## Data Pipeline
- Source: `source_durga700.itx` (ITRANS encoding), `source_kunjika.itx`
- Script: `build_data.py` - uses `indic_transliteration` library to generate Devanagari + IAST
- Output: `data.js` - structured object with chapters, angas, charitas, navarna, paath order
- Chapter content extracted by line ranges (defined in `CHAPTERS` list in build_data.py)
- Anga content extracted by line ranges (defined in `ANGAS` list)
- Saptashloki Durga is hardcoded in build_data.py (not in source itx)
- Run: `python3 build_data.py` - takes ~5 seconds

## Design Rules (inherited from sister projects)
- NO gradients. NO glowy effects. NO box-shadow glows or text-shadow glows.
- Solid flat colors only.
- Fonts: Haffer (local) > Geist > Inter for body; Tiro Devanagari Sanskrit for Sanskrit
- Dark theme default with light + system modes
- Gold accent (#c9a84c)
- Charita-specific border colors:
  - Prathama (Mahakali): #6b4d8c violet
  - Madhyama (Mahalakshmi): #c9a84c gold
  - Uttama (Mahasaraswati): #b8c4cd pearl

## File Structure
- `index.html` - SPA with hash routing (#home, #charitas, #chapters, #angas, #paath, #about)
- `style.css` - All styles, dark theme, mobile responsive, charita colours
- `app.js` - Application logic (IIFE)
- `data.js` - Generated data file (DO NOT edit - regenerate via build_data.py)
- `build_data.py` - Data merge script
- `source_durga700.itx` - Primary ITRANS source (Sanskrit Documents)
- `source_kunjika.itx` - Siddha Kunjika source
- `manifest.json` - PWA manifest
- `sw.js` - Service worker for offline support
- `icon.svg` - Om symbol icon

## Key Architectural Decisions
- Single page app with hash routing
- localStorage for all progress (chapters recited, angas recited, paath checklist, sadhana tracker, theme, font size)
- Chapter / anga cards expandable in place (no modal)
- Text tabs (Devanagari ↔ IAST) per card - default Devanagari
- Paath view auto-syncs with chapter and anga recited state
- No server needed - fully static, works offline via service worker

## Repo & Deployment
- GitHub: TheHardikDewra/durga-saptashati (after April 2026 migration)
- Deploy: Vercel as durga-saptashati.vercel.app
- Sister projects:
  - lalita-sahasranama (https://lalita-sahasranama.vercel.app)
  - shri-rudram (https://shri-rudram.vercel.app)

## Common Tasks
- **Update text content:** edit source_*.itx, run `python3 build_data.py`, commit
- **Update chapter summaries / metadata:** edit `CHAPTERS` list in build_data.py, run script
- **Add new anga:** add entry to `ANGAS` list (with line range from itx) OR fetch new source, run script
- **Update audio:** edit `home-youtube` iframe `src` and `audio-link` href in index.html
