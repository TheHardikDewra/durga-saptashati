#!/usr/bin/env python3
"""
Build script for Durga Saptashati data.js

Reads:
  - source_durga700.itx (Sanskrit Documents, K. Shankaran et al)
  - source_kunjika.itx (Siddha Kunjika Stotram)

Outputs:
  - data.js (Devanagari + IAST + structured chapters/angas)
"""

import json
import re
import os
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

ROOT = os.path.dirname(os.path.abspath(__file__))


def read_itx(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return f.read()


def strip_latex_macros(text):
    """Remove LaTeX commands and special markers from ITX text."""
    text = re.sub(r"\\section\{[^}]*\}", "", text)
    text = re.sub(r"\\engtitle\{[^}]*\}", "", text)
    text = re.sub(r"\\itxtitle\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", "", text)
    text = re.sub(r"^\s*\|\|.*?\|\|\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"##.*", "", text)
    text = re.sub(r"^%.*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\\\.", ".", text)
    text = re.sub(r"\\,", "", text)
    text = re.sub(r"\\\\", "", text)
    text = re.sub(r"\^\^", "", text)
    return text


def clean_itrans(text):
    """Clean ITRANS for transliteration: remove section markers, keep verses."""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("%"):
            continue
        if s.startswith("\\"):
            continue
        if s.startswith("#"):
            continue
        if s.startswith("|| ") or s.startswith("||"):
            continue
        s = re.sub(r"\\,", "", s)
        s = re.sub(r"\\\.", ".", s)
        lines.append(s)
    return "\n".join(lines).strip()


def to_devanagari(text):
    return transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)


def to_iast(text):
    return transliterate(text, sanscript.ITRANS, sanscript.IAST)


def extract_section(itx, start_marker, end_marker=None, end_pattern=None):
    """Extract text between markers from the ITX file."""
    start_re = re.escape(start_marker)
    m = re.search(start_re, itx)
    if not m:
        return None
    start = m.end()
    if end_marker:
        end_re = re.escape(end_marker)
        em = re.search(end_re, itx[start:])
        if em:
            return itx[start : start + em.start()]
    if end_pattern:
        em = re.search(end_pattern, itx[start:])
        if em:
            return itx[start : start + em.start()]
    return itx[start:]


def extract_lines_between(itx, start_line, end_line):
    """Extract text between specific line numbers (1-indexed, inclusive)."""
    lines = itx.split("\n")
    return "\n".join(lines[start_line - 1 : end_line])


# ============================================================
# Chapter metadata - canonical structure
# ============================================================

CHAPTERS = [
    {
        "num": 1,
        "title_sa": "मधुकैटभवधो",
        "title_en": "Madhu Kaitabha Vadha",
        "subtitle": "The Slaying of Madhu and Kaitabha",
        "charita": "prathama",
        "deity": "Mahakali",
        "narrator": "Sage Medhas",
        "summary": (
            "King Suratha, dispossessed by his ministers, and merchant Samadhi, "
            "betrayed by his family, meet in the forest hermitage of sage Medhas. "
            "Both wonder why attachment still binds them despite all they have lost. "
            "Medhas reveals that this is the work of Mahamaya - the Divine Mother. "
            "He recounts how, at the dawn of creation, the demons Madhu and Kaitabha "
            "emerged from Vishnu's ear-wax to kill Brahma. Brahma invoked Yoganidra "
            "(Mahamaya), who withdrew from Vishnu, allowing him to awaken and slay "
            "the demons. The chapter is presided over by Mahakali."
        ),
        "verses_approx": 87,
        "key_hymns": ["Brahma-Stuti (Brahma's praise of Yoganidra)"],
        "lines": (290, 477),
    },
    {
        "num": 2,
        "title_sa": "महिषासुरसैन्यवधो",
        "title_en": "Mahishasura Sainya Vadha",
        "subtitle": "The Slaughter of Mahishasura's Armies",
        "charita": "madhyama",
        "deity": "Mahalakshmi",
        "narrator": "Sage Medhas",
        "summary": (
            "After Mahishasura defeats Indra and the gods, the displaced devas pour "
            "their combined energies into a single radiant form - Devi Durga. Each "
            "god gifts her his weapon. Mounted on her lion, she emerges to confront "
            "the buffalo demon's vast army. The chapter narrates the slaughter of "
            "Mahishasura's generals and their immense forces."
        ),
        "verses_approx": 69,
        "key_hymns": ["Devi's emergence from combined divine tejas"],
        "lines": (481, 634),
    },
    {
        "num": 3,
        "title_sa": "महिषासुरवधो",
        "title_en": "Mahishasura Vadha",
        "subtitle": "The Slaying of Mahishasura",
        "charita": "madhyama",
        "deity": "Mahalakshmi",
        "narrator": "Sage Medhas",
        "summary": (
            "Mahishasura himself enters the battlefield, shape-shifting between "
            "buffalo, lion, man, and elephant. Devi finally pierces his heart with "
            "her trident as he emerges from the buffalo's mouth, beheading the demon "
            "and earning the name Mahishasura Mardini."
        ),
        "verses_approx": 44,
        "key_hymns": [],
        "lines": (638, 730),
    },
    {
        "num": 4,
        "title_sa": "शक्रादिस्तुतिः",
        "title_en": "Shakradi Stuti",
        "subtitle": "Praise by Indra and the Other Gods",
        "charita": "madhyama",
        "deity": "Mahalakshmi",
        "narrator": "Sage Medhas",
        "summary": (
            "Indra and the devas, restored to their realms, offer one of the great "
            "hymns of the text - the Shakradi Stuti. They praise Devi as the cause "
            "of all causes, the supreme Shakti who pervades all forms. Devi grants "
            "them the boon of remembrance: she promises to manifest whenever the "
            "world is in danger from demonic forces."
        ),
        "verses_approx": 42,
        "key_hymns": ["Shakradi Stuti (Hymn of Indra and gods)"],
        "lines": (734, 863),
    },
    {
        "num": 5,
        "title_sa": "देव्या दूतसंवादो",
        "title_en": "Devyā Dūta Saṃvāda",
        "subtitle": "The Devi's Conversation with the Messenger",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Demons Shumbha and Nishumbha conquer the three worlds. Hearing of Devi's "
            "beauty as she bathes in the Ganga (now called Parvati / Ambika / Kaushiki, "
            "born from Parvati's sheath), Shumbha sends his messenger Sugriva to "
            "demand her as bride. The chapter contains the celebrated 'Ya Devi Sarva "
            "Bhuteshu' hymn - Devi praised as residing in all beings as consciousness, "
            "intelligence, sleep, hunger, shadow, energy, thirst, forgiveness, and more. "
            "Devi sends back a vow: only one who defeats her in battle may marry her."
        ),
        "verses_approx": 129,
        "key_hymns": ["Ya Devi Sarva Bhuteshu (Aparajita Stuti / Tantric Devi Suktam)"],
        "lines": (867, 1047),
    },
    {
        "num": 6,
        "title_sa": "धूम्रलोचनवधो",
        "title_en": "Dhūmralochana Vadha",
        "subtitle": "The Slaying of Dhumralochana",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Enraged at the messenger's report, Shumbha sends the demon Dhumralochana "
            "with sixty thousand troops to capture Devi by force. Ambika reduces him "
            "to ashes with a single 'huṃ' sound. Her lion devours the entire army."
        ),
        "verses_approx": 26,
        "key_hymns": [],
        "lines": (1051, 1102),
    },
    {
        "num": 7,
        "title_sa": "चण्डमुण्डवधो",
        "title_en": "Chaṇḍa Muṇḍa Vadha",
        "subtitle": "The Slaying of Chanda and Munda",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Shumbha sends his fierce generals Chanda and Munda. Furious, Devi knits "
            "her brow and from her forehead emerges Kali - terrifying, garlanded with "
            "skulls, draped in tiger skin. Kali devours the demonic forces, severs "
            "the heads of Chanda and Munda, and earns the name Chamunda."
        ),
        "verses_approx": 30,
        "key_hymns": ["Origin of Kali / Chamunda"],
        "lines": (1106, 1165),
    },
    {
        "num": 8,
        "title_sa": "रक्तबीजवधो",
        "title_en": "Raktabīja Vadha",
        "subtitle": "The Slaying of Raktabija",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Raktabija enters the battle - boon-protected so that every drop of his "
            "blood spawns a clone of equal strength. The Saptamatrika (Seven Mothers - "
            "Brahmani, Maheshvari, Kaumari, Vaishnavi, Varahi, Narasimhi, Aindri) "
            "emerge from the gods' energies to assist Devi. Kali extends her tongue "
            "across the battlefield to drink every drop of Raktabija's blood before "
            "it touches the ground. The demon is finally drained and slain."
        ),
        "verses_approx": 63,
        "key_hymns": ["Origin of Saptamatrika (Seven Mothers)"],
        "lines": (1169, 1300),
    },
    {
        "num": 9,
        "title_sa": "निशुम्भवधो",
        "title_en": "Niśumbha Vadha",
        "subtitle": "The Slaying of Nishumbha",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "King Suratha asks why the Devi who is one became many. Medhas replies "
            "that all forms emerged from her one vibhuti. Nishumbha enters the battle. "
            "Despite repeated falls, he rises again. Devi finally pierces his heart "
            "with her arrow and beheads him."
        ),
        "verses_approx": 41,
        "key_hymns": [],
        "lines": (1304, 1391),
    },
    {
        "num": 10,
        "title_sa": "शुम्भवधो",
        "title_en": "Śumbha Vadha",
        "subtitle": "The Slaying of Shumbha",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Enraged by his brother's death, Shumbha taunts Devi for fighting with "
            "the help of others. Devi replies: 'I alone exist - all are but my "
            "manifestations.' She withdraws all her forms back into herself. In a "
            "single combat, Devi slays Shumbha with her trident."
        ),
        "verses_approx": 32,
        "key_hymns": ["'I alone exist' - Advaita declaration"],
        "lines": (1395, 1462),
    },
    {
        "num": 11,
        "title_sa": "नारायणीस्तुतिः",
        "title_en": "Nārāyaṇī Stuti",
        "subtitle": "Hymn to Narayani",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "The grandest hymn of the text. The gods, freed from oppression, offer "
            "the Narayani Stuti - praising Devi as Narayani, as the cause of "
            "creation-preservation-destruction, as Mangala, Shiva, Sukshma, and the "
            "supreme refuge. Devi grants the boon that whoever recites this hymn "
            "with devotion will be freed from all calamities."
        ),
        "verses_approx": 55,
        "key_hymns": ["Narayani Stuti - the great hymn to Mother as Narayani"],
        "lines": (1465, 1597),
    },
    {
        "num": 12,
        "title_sa": "भगवती वाक्यं",
        "title_en": "Bhagavatī Vākyaṃ",
        "subtitle": "The Promise of Blessings (Phala Shruti)",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Devi declares the fruits of reciting the Devi Mahatmyam. Whoever recites "
            "it on Ashtami, Chaturdashi, and Navami with single-pointed devotion will "
            "be freed from all afflictions: poverty, illness, fear of enemies, fire, "
            "drought, captivity, evil portents. The text itself is established as a "
            "mantra and the recitation as a yajna."
        ),
        "verses_approx": 41,
        "key_hymns": ["Phala Shruti - fruits of recitation"],
        "lines": (1601, 1686),
    },
    {
        "num": 13,
        "title_sa": "सुरथवैश्ययोर्वरप्रदानं",
        "title_en": "Suratha Vaiśya Vara Pradāna",
        "subtitle": "The Granting of Boons to King Suratha and the Merchant",
        "charita": "uttama",
        "deity": "Mahasaraswati",
        "narrator": "Sage Medhas",
        "summary": (
            "Hearing Medhas' teaching, King Suratha and the merchant Samadhi go to "
            "the riverbank, fashion an earthen image of Devi, and worship her with "
            "intense austerity for three years. Devi appears and grants them their "
            "wishes: Suratha asks for restoration of his kingdom and a future "
            "imperishable rule (he will become Savarni Manu); Samadhi asks for "
            "knowledge that uproots attachment - the gift of liberation."
        ),
        "verses_approx": 30,
        "key_hymns": ["Devi grants boons - Savarni Manu prophecy"],
        "lines": (1690, 1743),
    },
]


# Anga line ranges in durga700.itx
ANGAS = [
    {
        "id": "argala",
        "name_sa": "अर्गला स्तोत्रम्",
        "name_en": "Argala Stotram",
        "subtitle": "The Hymn of the Bolt - removes obstacles, opens the heart",
        "phase": "pre",
        "verse_count": 27,
        "rishi": "Vishnu",
        "chhanda": "Anushtup",
        "devata": "Mahalakshmi",
        "summary": (
            "Argala means 'bolt' - this hymn unbolts the door of grace. Composed by "
            "Vishnu rishi, each verse ends with the refrain 'rūpaṃ dehi jayaṃ dehi "
            "yaśo dehi dviṣo jahi' - 'grant me beauty, grant victory, grant fame, "
            "destroy enmity.' Traditionally recited as part of the Trayanga (along "
            "with Kavacha and Keelaka) before the Saptashati paath."
        ),
        "lines": (45, 108),
    },
    {
        "id": "keelaka",
        "name_sa": "कीलक स्तोत्रम्",
        "name_en": "Keelaka Stotram",
        "subtitle": "The Unsealing - removes the lock that guards the mantras",
        "phase": "pre",
        "verse_count": 16,
        "rishi": "Shiva",
        "chhanda": "Anushtup",
        "devata": "Mahasaraswati",
        "summary": (
            "Keelaka means 'wedge' or 'pin'. The mantras of Devi Mahatmyam are said "
            "to be locked (keelita) so they bear fruit only for the worthy. This "
            "stotram unlocks them. Composed by Shiva rishi. Recited as part of the "
            "Trayanga, after Argala and before the chapters."
        ),
        "lines": (110, 150),
    },
    {
        "id": "kavacha",
        "name_sa": "देवी कवचम्",
        "name_en": "Devi Kavacham",
        "subtitle": "The Armor of the Goddess - protection of body, mind, and direction",
        "phase": "pre",
        "verse_count": 61,
        "rishi": "Brahma",
        "chhanda": "Anushtup",
        "devata": "Chamunda",
        "summary": (
            "The Kavacha names the nine forms of Durga (Navadurga - Shailaputri, "
            "Brahmacharini, Chandraghanta, Kushmanda, Skandamata, Katyayani, Kalaratri, "
            "Mahagauri, Siddhidatri) and asks each to protect a part of the body, a "
            "direction, an organ, and a stage of life. The most comprehensive "
            "protective hymn in the Shakta tradition. 61 verses."
        ),
        "lines": (151, 280),
    },
    {
        "id": "kshamapana",
        "name_sa": "अपराधक्षमापणस्तोत्रम्",
        "name_en": "Aparadha Kshamapana Stotram",
        "subtitle": "Forgiveness for Transgressions",
        "phase": "post",
        "verse_count": 9,
        "rishi": "Traditional",
        "chhanda": "",
        "devata": "Devi",
        "summary": (
            "Concluding hymn asking forgiveness for any errors, omissions, or "
            "improper procedures during the recitation. Acknowledges that the "
            "devotee, lacking complete knowledge of mantras, ritual, and purity, "
            "appeals to the Mother's compassion to make the offering whole."
        ),
        "lines": (1748, 1772),
    },
    {
        "id": "devi-suktam",
        "name_sa": "देवी सूक्तम्",
        "name_en": "Devi Suktam (Vagambhrini Suktam)",
        "subtitle": "The Vedic Hymn of the Goddess - Rig Veda 10.125",
        "phase": "post",
        "verse_count": 8,
        "rishi": "Vak (daughter of Ambhrina)",
        "chhanda": "Trishtup",
        "devata": "Para Brahman",
        "summary": (
            "From Rig Veda 10.125 - the famous hymn where Vak, daughter of sage "
            "Ambhrina, declares herself to be the Supreme: 'I move with the Rudras, "
            "the Vasus, the Adityas. I am the queen, the gatherer of treasures. I am "
            "the wind, the rain, the breath. I bend the bow for Rudra to slay the "
            "hater of devotion. I dwell in the waters, in the highest heaven; from "
            "there I extend over all worlds.' The capstone of the entire Saptashati "
            "recitation."
        ),
        "lines": (1774, 1825),
    },
]


# ============================================================
# Special angas: dhyana stotras (extracted manually from itx)
# ============================================================

DHYANA_VERSES = {
    "chandika_dhyanam": {
        "name_en": "Sri Chandika Dhyanam",
        "name_sa": "श्रीचण्डिकाध्यानम्",
        "lines": (35, 41),
    }
}

# ============================================================
# Saptashloki Durga (Amba Stuti) - traditional hymn (not in durga700.itx)
# Source: traditional Markandeya Purana - widely available
# Adding canonical text manually as it's a 7-verse hymn
# ============================================================

SAPTASHLOKI_TEXT = """j~nAninAmapi chetAMsi devI bhagavatI hi sA |
balAdAkR^iShya mohAya mahAmAyA prayachChati ||1||

durge smR^itA harasi bhItimasheShajantoH
svasthaiH smR^itA matimatIva shubhAM dadAsi |
dAridryaduHkhabhayahAriNi kA tvadanyA
sarvopakArakaraNAya sadArdrachittA ||2||

sarvamaN^galamAN^galye shive sarvArthasAdhike |
sharaNye tryambake gauri nArAyaNi namo.astu te ||3||

sharaNAgatadInArtaparitrANaparAyaNe |
sarvasyArtihare devi nArAyaNi namo.astu te ||4||

sarvasvarUpe sarveshe sarvashaktisamanvite |
bhayebhyastrAhi no devi durge devi namo.astu te ||5||

rogAnasheShAnapahaMsi tuShTA
ruShTA tu kAmAn sakalAnabhIShTAn |
tvAmAshritAnAM na vipannarANAM
tvAmAshritA hyAshrayatAM prayAnti ||6||

sarvAbAdhAprashamanaM trailokyasyAkhileshvari |
evameva tvayA kAryamasmadvairivinAshanam ||7||"""


# ============================================================
# Build chapter data
# ============================================================


def build_chapter(itx_full, ch_meta):
    start, end = ch_meta["lines"]
    raw = extract_lines_between(itx_full, start, end)
    # Remove the section line itself if present
    cleaned = clean_itrans(raw)
    devanagari = to_devanagari(cleaned)
    iast = to_iast(cleaned)
    return {
        "num": ch_meta["num"],
        "titleSa": ch_meta["title_sa"],
        "titleEn": ch_meta["title_en"],
        "subtitle": ch_meta["subtitle"],
        "charita": ch_meta["charita"],
        "deity": ch_meta["deity"],
        "narrator": ch_meta["narrator"],
        "summary": ch_meta["summary"],
        "versesApprox": ch_meta["verses_approx"],
        "keyHymns": ch_meta["key_hymns"],
        "devanagari": devanagari.strip(),
        "iast": iast.strip(),
    }


def build_anga(itx_full, anga_meta):
    start, end = anga_meta["lines"]
    raw = extract_lines_between(itx_full, start, end)
    cleaned = clean_itrans(raw)
    devanagari = to_devanagari(cleaned)
    iast = to_iast(cleaned)
    return {
        "id": anga_meta["id"],
        "nameSa": anga_meta["name_sa"],
        "nameEn": anga_meta["name_en"],
        "subtitle": anga_meta["subtitle"],
        "phase": anga_meta["phase"],
        "verseCount": anga_meta["verse_count"],
        "rishi": anga_meta["rishi"],
        "chhanda": anga_meta["chhanda"],
        "devata": anga_meta["devata"],
        "summary": anga_meta["summary"],
        "devanagari": devanagari.strip(),
        "iast": iast.strip(),
    }


def build_kunjika(itx):
    """Siddha Kunjika has its own file with multiple stotras inside."""
    # Find the main kunjika section
    cleaned = clean_itrans(itx)
    devanagari = to_devanagari(cleaned)
    iast = to_iast(cleaned)
    return {
        "id": "kunjika",
        "nameSa": "सिद्ध कुञ्जिका स्तोत्रम्",
        "nameEn": "Siddha Kunjika Stotram",
        "subtitle": "The Master Key - synthesizing Kavacha, Argala, and Keelaka",
        "phase": "post",
        "verseCount": 14,
        "rishi": "Shiva (taught to Parvati)",
        "chhanda": "Anushtup",
        "devata": "Chamunda",
        "summary": (
            "The 'master key' (kunjika) stotram. Tradition holds that one who "
            "recites Kunjika alone receives the merit of the entire Saptashati - "
            "without needing to recite Kavacha, Argala, Keelaka, the Rahasyas, or "
            "any other anga. Sourced from the Rudrayamala Tantra. Contains the "
            "powerful Navarna Mantra: 'Aim Hreem Kleem Chamundayai Vichche'. "
            "14 verses, brief but exceptionally potent."
        ),
        "devanagari": devanagari.strip(),
        "iast": iast.strip(),
    }


def build_saptashloki():
    cleaned = SAPTASHLOKI_TEXT
    devanagari = to_devanagari(cleaned)
    iast = to_iast(cleaned)
    return {
        "id": "saptashloki",
        "nameSa": "सप्तश्लोकी दुर्गा",
        "nameEn": "Saptashloki Durga (Amba Stuti)",
        "subtitle": "Seven verses - the essence of the entire Saptashati",
        "phase": "pre",
        "verseCount": 7,
        "rishi": "Shiva",
        "chhanda": "Mixed",
        "devata": "Durga",
        "summary": (
            "When Lord Shiva was asked by Parvati for the simplest path to Devi's "
            "grace, he condensed the entire Saptashati into seven verses. Tradition "
            "holds that reciting Saptashloki alone, with sincere devotion, yields "
            "the fruit of the full 700-verse paath. Each verse contains the seed "
            "of a major hymn from the parent text."
        ),
        "devanagari": devanagari.strip(),
        "iast": iast.strip(),
    }


def build_chandika_dhyana(itx):
    raw = extract_lines_between(itx, 35, 43)
    cleaned = clean_itrans(raw)
    return {
        "id": "chandika-dhyana",
        "nameSa": "श्री चण्डिका ध्यानम्",
        "nameEn": "Sri Chandika Dhyanam",
        "subtitle": "Meditation verse on Devi Chandika - opens the paath",
        "phase": "pre",
        "verseCount": 2,
        "rishi": "Traditional",
        "chhanda": "",
        "devata": "Chandika",
        "summary": (
            "The opening dhyana verse on Devi Chandika - bandhuka-flower-hued, "
            "garlanded with skulls, three-eyed, holding book, rosary, boon-giving "
            "and abhaya mudras. Sets the visualization for the entire recitation. "
            "Two alternative dhyana verses are traditionally chanted at the start."
        ),
        "devanagari": to_devanagari(cleaned).strip(),
        "iast": to_iast(cleaned).strip(),
    }


# ============================================================
# Navarna Mantra info
# ============================================================

NAVARNA_MANTRA = {
    "id": "navarna",
    "nameSa": "नवार्ण मन्त्र",
    "nameEn": "Navarna Mantra",
    "subtitle": "The nine-syllable mantra - heart of all Devi sadhana",
    "devanagari": "ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे",
    "iast": "oṃ aiṃ hrīṃ klīṃ cāmuṇḍāyai vicce",
    "summary": (
        "The Navarna ('nine-letter') mantra is the supreme bija mantra of Durga "
        "Saptashati. Each syllable encodes a cosmic principle:\n\n"
        "• Aim (ऐं) - Mahasaraswati, knowledge\n"
        "• Hreem (ह्रीं) - Mahalakshmi, prosperity, the heart of Devi\n"
        "• Kleem (क्लीं) - Mahakali, attraction, fulfillment of desires\n"
        "• Chamundayai (चामुण्डायै) - the unified ferocious form who slew Chanda and Munda\n"
        "• Vicche (विच्चे) - bestower of liberation, the seal\n\n"
        "Recited 108 times before and after the paath. Traditionally chanted at "
        "the junction of each chapter (chapter-sandhi) for sealing the energy."
    ),
    "wordBreakdown": [
        {"word": "ऐं", "iast": "aiṃ", "meaning": "Saraswati bija - knowledge, vak"},
        {"word": "ह्रीं", "iast": "hrīṃ", "meaning": "Lakshmi/Bhuvaneshwari bija - heart of Devi, all auspiciousness"},
        {"word": "क्लीं", "iast": "klīṃ", "meaning": "Kali/Kama bija - attraction, fulfillment of desires"},
        {"word": "चामुण्डायै", "iast": "cāmuṇḍāyai", "meaning": "to Chamunda - the unified destroyer of Chanda-Munda"},
        {"word": "विच्चे", "iast": "vicce", "meaning": "bestower of liberation; the seal of the mantra"},
    ],
}


# ============================================================
# Site-level metadata
# ============================================================

CHARITAS = [
    {
        "id": "prathama",
        "name_sa": "प्रथम चरित्र",
        "name_en": "Prathama Charita",
        "deity": "Mahakali",
        "deity_sa": "महाकाली",
        "guna": "Tamasika",
        "principle": "Destroyer of ignorance",
        "chapters": [1],
        "narrative": "Madhu-Kaitabha Vadha - awakening of Vishnu through Yoganidra",
        "color_label": "deep blue-black (Kali's complexion)",
        "summary": (
            "The First Episode contains a single chapter. It tells of Vishnu in cosmic "
            "yogic sleep at the dissolution of the universe, when the demons Madhu and "
            "Kaitabha emerge from his ear-wax to attack Brahma. Brahma invokes the "
            "Yoganidra of Vishnu - Mahamaya, the Devi - who withdraws from him so he "
            "may awaken. Mahakali presides. The hymn here is Brahma-Stuti."
        ),
    },
    {
        "id": "madhyama",
        "name_sa": "मध्यम चरित्र",
        "name_en": "Madhyama Charita",
        "deity": "Mahalakshmi",
        "deity_sa": "महालक्ष्मी",
        "guna": "Rajasika",
        "principle": "Sustainer, sovereign of action",
        "chapters": [2, 3, 4],
        "narrative": "Mahishasura Vadha - the slaying of the buffalo demon",
        "color_label": "golden",
        "summary": (
            "The Middle Episode is the most central section of the text. The gods "
            "pour their combined energies into a single radiant form - Devi Durga - "
            "and arm her with their weapons. She slays Mahishasura's army, then the "
            "buffalo demon himself, becoming Mahishasura Mardini. Mahalakshmi "
            "presides. The closing chapter contains the great Shakradi Stuti. "
            "Tradition holds: never interrupt this charita mid-recitation."
        ),
    },
    {
        "id": "uttama",
        "name_sa": "उत्तम चरित्र",
        "name_en": "Uttama Charita",
        "deity": "Mahasaraswati",
        "deity_sa": "महासरस्वती",
        "guna": "Sattvika",
        "principle": "Creator of knowledge, granter of liberation",
        "chapters": [5, 6, 7, 8, 9, 10, 11, 12, 13],
        "narrative": "Shumbha-Nishumbha Vadha + the granting of boons",
        "color_label": "white-pearlescent",
        "summary": (
            "The Final Episode spans nine chapters and is the longest. Devi as Ambika "
            "(Kaushiki, born from Parvati's body-sheath) confronts Shumbha and "
            "Nishumbha. Kali emerges from her brow; the Saptamatrika emerge from the "
            "gods. After slaying Dhumralochana, Chanda-Munda, Raktabija, Nishumbha, "
            "and finally Shumbha, Devi receives the great Narayani Stuti. The text "
            "closes with the Phala Shruti and the boons granted to King Suratha and "
            "Samadhi. Mahasaraswati presides."
        ),
    },
]


PAATH_ORDER = [
    {"phase": "pre", "id": "saptashloki", "label": "Saptashloki Durga"},
    {"phase": "pre", "id": "chandika-dhyana", "label": "Chandika Dhyana"},
    {"phase": "pre", "id": "navarna", "label": "Navarna Mantra"},
    {"phase": "pre", "id": "argala", "label": "Argala Stotram"},
    {"phase": "pre", "id": "keelaka", "label": "Keelaka Stotram"},
    {"phase": "pre", "id": "kavacha", "label": "Devi Kavacham"},
    {"phase": "main", "id": "chapter-1", "label": "Chapter 1 (Prathama Charita)"},
    {"phase": "main", "id": "chapter-2", "label": "Chapter 2"},
    {"phase": "main", "id": "chapter-3", "label": "Chapter 3"},
    {"phase": "main", "id": "chapter-4", "label": "Chapter 4 (Madhyama complete)"},
    {"phase": "main", "id": "chapter-5", "label": "Chapter 5"},
    {"phase": "main", "id": "chapter-6", "label": "Chapter 6"},
    {"phase": "main", "id": "chapter-7", "label": "Chapter 7"},
    {"phase": "main", "id": "chapter-8", "label": "Chapter 8"},
    {"phase": "main", "id": "chapter-9", "label": "Chapter 9"},
    {"phase": "main", "id": "chapter-10", "label": "Chapter 10"},
    {"phase": "main", "id": "chapter-11", "label": "Chapter 11 (Narayani Stuti)"},
    {"phase": "main", "id": "chapter-12", "label": "Chapter 12 (Phala Shruti)"},
    {"phase": "main", "id": "chapter-13", "label": "Chapter 13 (Uttama complete)"},
    {"phase": "post", "id": "devi-suktam", "label": "Devi Suktam"},
    {"phase": "post", "id": "kunjika", "label": "Siddha Kunjika Stotram"},
    {"phase": "post", "id": "kshamapana", "label": "Aparadha Kshamapana"},
]


# ============================================================
# Main build
# ============================================================

def main():
    print("Reading source files...")
    durga700 = read_itx("source_durga700.itx")
    kunjika = read_itx("source_kunjika.itx")

    print("Building chapters...")
    chapters = [build_chapter(durga700, ch) for ch in CHAPTERS]

    print("Building angas from durga700.itx...")
    angas = [build_anga(durga700, a) for a in ANGAS]

    print("Building Saptashloki Durga...")
    saptashloki = build_saptashloki()

    print("Building Chandika Dhyana...")
    chandika_dhyana = build_chandika_dhyana(durga700)

    print("Building Siddha Kunjika...")
    kunjika_data = build_kunjika(kunjika)

    # Combine all angas (pre + post)
    all_angas = [
        saptashloki,
        chandika_dhyana,
        angas[0],  # argala
        angas[1],  # keelaka
        angas[2],  # kavacha
        angas[4],  # devi-suktam (post)
        kunjika_data,
        angas[3],  # kshamapana
    ]

    # Build the master data object
    data = {
        "meta": {
            "title": "Sri Durga Saptashati",
            "subtitle": "Devi Mahatmyam - 700 verses on the Divine Mother",
            "source": "Markandeya Purana, chapters 81-93 (5th-6th c. CE)",
            "narrator": "Sage Markandeya, retold by Sage Medhas to King Suratha and merchant Samadhi",
            "totalChapters": 13,
            "totalMantras": 700,
            "totalActualVerses": 518,
            "mantraBreakdown": {
                "slokaMantras": 537,
                "ardhaSlokaMantras": 38,
                "khandaMantras": 66,
                "uvachaMantras": 57,
                "punaruktaMantras": 2,
            },
            "buildDate": "2026-05-02",
        },
        "charitas": CHARITAS,
        "chapters": chapters,
        "angas": all_angas,
        "navarnaMantra": NAVARNA_MANTRA,
        "paathOrder": PAATH_ORDER,
    }

    # Write data.js
    print("Writing data.js...")
    js = "window.DURGA_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    with open(os.path.join(ROOT, "data.js"), "w", encoding="utf-8") as f:
        f.write(js)

    print(f"Done. data.js size: {os.path.getsize(os.path.join(ROOT, 'data.js'))} bytes")
    print(f"Chapters: {len(chapters)}")
    print(f"Angas: {len(all_angas)}")
    print(f"Charitas: {len(CHARITAS)}")


if __name__ == "__main__":
    main()
