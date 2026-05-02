# Sri Durga Saptashati

Interactive guide to Sri Durga Saptashati (Devi Mahatmyam / Chandi Path) - the most revered text of the Shakta tradition. 700 verses across 13 chapters from the Markandeya Purana, presided by Mahakali, Mahalakshmi, and Mahasaraswati.

**Live site**: [durga-saptashati.vercel.app](https://durga-saptashati.vercel.app)

## What's inside

- All 13 chapters (Madhu-Kaitabha, Mahishasura, Shumbha-Nishumbha narratives) with full Devanagari text and IAST transliteration
- 3 charita (episode) breakdown - Prathama (Mahakali), Madhyama (Mahalakshmi), Uttama (Mahasaraswati)
- 8 traditional angas (auxiliary texts) - Saptashloki, Chandika Dhyana, Argala, Keelaka, Devi Kavacha, Devi Suktam, Siddha Kunjika, Aparadha Kshamapana
- Navarna mantra with syllable-by-syllable breakdown
- Full paath checklist in canonical order
- Embedded chanting audio from Vaidic Dharma Sansthan (Bangalore Ashram) Parayanam
- Frame story explainer (Suratha, Samadhi, Sage Medhas, Markandeya)
- Trayanga vs Navangam method comparison
- Four great hymns reference (Brahma-Stuti, Shakradi-Stuti, Ya Devi Sarva Bhuteshu, Narayani Stuti)

## Features

### Home
Stats dashboard, sadhana tracker (log recitations, track streaks), Navarna mantra breakdown, embedded VDS Parayanam audio, quick links to chapters and paath.

### Charitas
Three-card view of the three episodes. Each shows the presiding Devi (Sanskrit + English), guna, narrative theme, summary, and quick links to the chapters within.

### Chapters
All 13 chapters as expandable cards. Each shows: full Sanskrit (Devanagari), IAST transliteration, summary of the narrative, presiding deity, narrator, key hymns. Mark chapters as recited.

### Angas
All auxiliary texts in Purvanga (pre-paath) and Uttaranga (post-paath) order. Same expandable interface as chapters with full Sanskrit, IAST, rishi/devata metadata, and summaries.

### Paath
Full Navangam paath as a checklist in traditional order. Tracks progress across all 22+ components (pre-angas → 13 chapters → post-angas). Resets on demand.

### About
Source explainer, frame story, the 700-mantra breakdown (sloka/ardha-sloka/khanda/uvacha), Trayanga vs Navangam, traditional paath flow, hymn reference, etiquette guide, sister projects.

## Seeker tools

- **Sadhana tracker** - log paath recitations, track daily streaks, monthly counts
- **Recitation tracker** - mark each chapter and anga as recited; persists across sessions
- **Paath checklist** - canonical order, full progress tracking
- **Font size controls** - normal / large / extra-large for Sanskrit reading
- **Light / Dark / System theme** - dark by default, gold accent
- **Export / Import** - backup all progress as JSON
- **Installable PWA** - works offline, add to home screen

## Source texts

- **Primary text (700 verses + Trayanga + Devi Suktam + Aparadha Kshamapana):** [Sanskrit Documents - durga700](https://sanskritdocuments.org/doc_devii/durga700.html) - transliterated by K. Shankaran, Kirk Wortman, Dhruba Chakroborty, Ahto Jarve. Proofread by Sunder Hattangadi.
- **Siddha Kunjika Stotram:** [Sanskrit Documents - siddhakunjikaa](https://sanskritdocuments.org/doc_devii/siddhakunjikaa.html) - source: Rudrayamala Tantra / Damaratantra.
- **Cross-verification:** Gita Press Gorakhpur edition, [Vaidika Vignanam](https://www.vignanam.org/).
- **Saptashloki Durga:** Traditional Markandeya Purana, widely available canonical text.

## Audio source

Vaidic Dharma Sansthan, Bangalore Ashram (Om Swami ji's organisation) - regular Durga Saptashati Parayanam events:
- [Latest Parayanam (02 Jan 2026)](https://www.youtube.com/watch?v=IVrC7uvVICQ)
- [Durga Saptashati Chants playlist](https://www.youtube.com/playlist?list=PLAPrVB8wngPncDkh-98XD_HT21hKENqEX)
- [How to Benefit from Durga Saptashati - Om Swami ji's discourse](https://www.youtube.com/watch?v=2SdjEYSww-Q)

## Tech

Pure vanilla HTML / CSS / JS. No frameworks, no build step (Python script is for data only).

- Fonts: Haffer (local) → Geist → Inter for body; Tiro Devanagari Sanskrit for Sanskrit headings
- Dark theme default with light and system modes
- Charita-coloured borders (Kali violet, Lakshmi gold, Saraswati pearl)
- localStorage for all progress
- Service worker for offline support
- Deployed on Vercel

## Data pipeline

Python script `build_data.py` reads the ITRANS-encoded source files and uses `indic-transliteration` to generate Devanagari and IAST. Output goes to `data.js`. The script also embeds canonical chapter / anga / charita metadata.

```bash
pip3 install indic-transliteration
python3 build_data.py
```

## Running locally

```bash
python3 -m http.server 9000
# visit http://localhost:9000
```

## Sister projects

- **Sri Lalita Sahasranama** - 1000 names of the Divine Mother → [lalita-sahasranama.vercel.app](https://lalita-sahasranama.vercel.app)
- **Sri Rudram** - 22 anuvakas to Lord Rudra → [shri-rudram.vercel.app](https://shri-rudram.vercel.app)

## About the text

Sri Durga Saptashati (also called Devi Mahatmyam, Chandi Path) is from the Markandeya Purana, chapters 81-93. Composed between the 4th and 6th centuries CE, it is the first text in the Hindu canon where the Goddess is declared as the supreme reality - not consort, not aspect, but the One from whom all forms emerge.

The narrative frame: Sage Markandeya teaches it to Krushtuki, who teaches it to Savarni Manu. Within that, sage Medhas explains it to King Suratha (dispossessed by his ministers) and merchant Samadhi (abandoned by his family). Both ask why attachment binds them despite betrayal. Medhas reveals that Mahamaya - the Divine Mother - is the cause of all such bondage and the only one who can liberate.

The 13 chapters unfold across 3 charitas - the slaying of Madhu-Kaitabha (Mahakali presides), the slaying of Mahishasura (Mahalakshmi presides), and the slaying of Shumbha-Nishumbha (Mahasaraswati presides). The text closes with King Suratha receiving the boon of becoming Savarni Manu and Samadhi receiving liberation through self-knowledge.

## Dedication

This is a devotional offering at the feet of Maa Durga, the Divine Mother. May it serve any seeker walking the Shakta path.

जय माता दी ।
