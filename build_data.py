#!/usr/bin/env python3
"""
Build script for Durga Saptashati data.js (v2 - maxxed out)

Sources:
  - source_durga700.itx (Sanskrit Documents - main text + Trayanga + Devi Suktam + Aparadha Kshamapana)
  - source_kunjika.itx (Siddha Kunjika)
  - source_devi_atharva.itx (Devi Atharvashirsha)
  - source_rahasya_*.txt (Pradhanika, Vaikritika, Murti - Devanagari, sourced from Drik Panchang)

Outputs:
  - data.js (Devanagari + IAST + chapters/angas/charitas/navadurga/saptamatrika/hymns/navratri)
"""

import json
import re
import os
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

ROOT = os.path.dirname(os.path.abspath(__file__))


def read_file(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return f.read()


def clean_itrans(text):
    """Strip LaTeX/comments from ITRANS, keep verses."""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("%"): continue
        if s.startswith("\\"): continue
        if s.startswith("#"): continue
        if s.startswith("|| ") or s.startswith("||"): continue
        s = re.sub(r"\\,", "", s)
        s = re.sub(r"\\\.", ".", s)
        lines.append(s)
    return "\n".join(lines).strip()


def to_devanagari(text):
    return transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)


def to_iast(text):
    return transliterate(text, sanscript.ITRANS, sanscript.IAST)


def deva_to_iast(text):
    return transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)


def extract_lines(text, start, end):
    return "\n".join(text.split("\n")[start - 1:end])


# ============================================================
# Chapter metadata
# ============================================================

CHAPTERS = [
    {"num": 1, "title_sa": "मधुकैटभवधो", "title_en": "Madhu Kaitabha Vadha",
     "subtitle": "The Slaying of Madhu and Kaitabha", "charita": "prathama", "deity": "Mahakali",
     "narrator": "Sage Medhas",
     "summary": "King Suratha, dispossessed by his ministers, and merchant Samadhi, betrayed by his family, meet in the forest hermitage of sage Medhas. Both wonder why attachment still binds them despite all they have lost. Medhas reveals that this is the work of Mahamaya - the Divine Mother. He recounts how, at the dawn of creation, the demons Madhu and Kaitabha emerged from Vishnu's ear-wax to kill Brahma. Brahma invoked Yoganidra (Mahamaya), who withdrew from Vishnu, allowing him to awaken and slay the demons. The chapter is presided over by Mahakali.",
     "verses_approx": 87, "key_hymns": ["Brahma-Stuti (Brahma's praise of Yoganidra)"],
     "lines": (290, 477), "phala": "Removes confusion, restores clarity, awakens dormant power"},
    {"num": 2, "title_sa": "महिषासुरसैन्यवधो", "title_en": "Mahishasura Sainya Vadha",
     "subtitle": "The Slaughter of Mahishasura's Armies", "charita": "madhyama", "deity": "Mahalakshmi",
     "narrator": "Sage Medhas",
     "summary": "After Mahishasura defeats Indra and the gods, the displaced devas pour their combined energies into a single radiant form - Devi Durga. Each god gifts her his weapon. Mounted on her lion, she emerges to confront the buffalo demon's vast army. The chapter narrates the slaughter of Mahishasura's generals and their immense forces.",
     "verses_approx": 69, "key_hymns": ["Devi's emergence from combined divine tejas"],
     "lines": (481, 634), "phala": "Destroys hostile forces, removes opposition, gathers scattered energy"},
    {"num": 3, "title_sa": "महिषासुरवधो", "title_en": "Mahishasura Vadha",
     "subtitle": "The Slaying of Mahishasura", "charita": "madhyama", "deity": "Mahalakshmi",
     "narrator": "Sage Medhas",
     "summary": "Mahishasura himself enters the battlefield, shape-shifting between buffalo, lion, man, and elephant. Devi finally pierces his heart with her trident as he emerges from the buffalo's mouth, beheading the demon and earning the name Mahishasura Mardini.",
     "verses_approx": 44, "key_hymns": [], "lines": (638, 730),
     "phala": "Slays the inner Mahishasura - tamas, sloth, ignorance, ego"},
    {"num": 4, "title_sa": "शक्रादिस्तुतिः", "title_en": "Shakradi Stuti",
     "subtitle": "Praise by Indra and the Other Gods", "charita": "madhyama", "deity": "Mahalakshmi",
     "narrator": "Sage Medhas",
     "summary": "Indra and the devas, restored to their realms, offer one of the great hymns of the text - the Shakradi Stuti. They praise Devi as the cause of all causes, the supreme Shakti who pervades all forms. Devi grants them the boon of remembrance: she promises to manifest whenever the world is in danger from demonic forces.",
     "verses_approx": 42, "key_hymns": ["Shakradi Stuti (Hymn of Indra and gods)"],
     "lines": (734, 863), "phala": "Brings Devi's boon of remembrance and protection in calamity"},
    {"num": 5, "title_sa": "देव्या दूतसंवादो", "title_en": "Devyā Dūta Saṃvāda",
     "subtitle": "The Devi's Conversation with the Messenger", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Demons Shumbha and Nishumbha conquer the three worlds. Hearing of Devi's beauty as she bathes in the Ganga (now called Parvati / Ambika / Kaushiki, born from Parvati's sheath), Shumbha sends his messenger Sugriva to demand her as bride. The chapter contains the celebrated 'Ya Devi Sarva Bhuteshu' hymn - Devi praised as residing in all beings as consciousness, intelligence, sleep, hunger, shadow, energy, thirst, forgiveness, and more. Devi sends back a vow: only one who defeats her in battle may marry her.",
     "verses_approx": 129, "key_hymns": ["Ya Devi Sarva Bhuteshu (Aparajita Stuti / Tantric Devi Suktam)"],
     "lines": (867, 1047), "phala": "Confers refuge of Devi in every aspect of being"},
    {"num": 6, "title_sa": "धूम्रलोचनवधो", "title_en": "Dhūmralochana Vadha",
     "subtitle": "The Slaying of Dhumralochana", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Enraged at the messenger's report, Shumbha sends the demon Dhumralochana with sixty thousand troops to capture Devi by force. Ambika reduces him to ashes with a single 'huṃ' sound. Her lion devours the entire army.",
     "verses_approx": 26, "key_hymns": [], "lines": (1051, 1102),
     "phala": "Burns away dim-sightedness (dhumra-lochana = smoke-eyed) - removes the fog of delusion"},
    {"num": 7, "title_sa": "चण्डमुण्डवधो", "title_en": "Chaṇḍa Muṇḍa Vadha",
     "subtitle": "The Slaying of Chanda and Munda", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Shumbha sends his fierce generals Chanda and Munda. Furious, Devi knits her brow and from her forehead emerges Kali - terrifying, garlanded with skulls, draped in tiger skin. Kali devours the demonic forces, severs the heads of Chanda and Munda, and earns the name Chamunda.",
     "verses_approx": 30, "key_hymns": ["Origin of Kali / Chamunda"],
     "lines": (1106, 1165), "phala": "Origin of Kali - destroys violent passion (chanda) and inertia (munda)"},
    {"num": 8, "title_sa": "रक्तबीजवधो", "title_en": "Raktabīja Vadha",
     "subtitle": "The Slaying of Raktabija", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Raktabija enters the battle - boon-protected so that every drop of his blood spawns a clone of equal strength. The Saptamatrika (Seven Mothers - Brahmani, Maheshvari, Kaumari, Vaishnavi, Varahi, Narasimhi, Aindri) emerge from the gods' energies to assist Devi. Kali extends her tongue across the battlefield to drink every drop of Raktabija's blood before it touches the ground. The demon is finally drained and slain.",
     "verses_approx": 63, "key_hymns": ["Origin of Saptamatrika (Seven Mothers)"],
     "lines": (1169, 1300),
     "phala": "Destroys the multiplying-desire demon - cuts off vasanas at root before they sprout"},
    {"num": 9, "title_sa": "निशुम्भवधो", "title_en": "Niśumbha Vadha",
     "subtitle": "The Slaying of Nishumbha", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "King Suratha asks why the Devi who is one became many. Medhas replies that all forms emerged from her one vibhuti. Nishumbha enters the battle. Despite repeated falls, he rises again. Devi finally pierces his heart with her arrow and beheads him.",
     "verses_approx": 41, "key_hymns": [], "lines": (1304, 1391),
     "phala": "Slays self-deception (ni-shumbha = strongly cast-down ego)"},
    {"num": 10, "title_sa": "शुम्भवधो", "title_en": "Śumbha Vadha",
     "subtitle": "The Slaying of Shumbha", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Enraged by his brother's death, Shumbha taunts Devi for fighting with the help of others. Devi replies: 'I alone exist - all are but my manifestations.' She withdraws all her forms back into herself. In a single combat, Devi slays Shumbha with her trident.",
     "verses_approx": 32, "key_hymns": ["'I alone exist' - Advaita declaration"],
     "lines": (1395, 1462), "phala": "Slays primal pride (shumbha = self-conceit). The Advaita declaration."},
    {"num": 11, "title_sa": "नारायणीस्तुतिः", "title_en": "Nārāyaṇī Stuti",
     "subtitle": "Hymn to Narayani", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "The grandest hymn of the text. The gods, freed from oppression, offer the Narayani Stuti - praising Devi as Narayani, as the cause of creation-preservation-destruction, as Mangala, Shiva, Sukshma, and the supreme refuge. Devi grants the boon that whoever recites this hymn with devotion will be freed from all calamities.",
     "verses_approx": 55, "key_hymns": ["Narayani Stuti - the great hymn to Mother as Narayani"],
     "lines": (1465, 1597),
     "phala": "The supreme refuge hymn - confers freedom from all calamities"},
    {"num": 12, "title_sa": "भगवती वाक्यं", "title_en": "Bhagavatī Vākyaṃ",
     "subtitle": "The Promise of Blessings (Phala Shruti)", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Devi declares the fruits of reciting the Devi Mahatmyam. Whoever recites it on Ashtami, Chaturdashi, and Navami with single-pointed devotion will be freed from all afflictions: poverty, illness, fear of enemies, fire, drought, captivity, evil portents. The text itself is established as a mantra and the recitation as a yajna.",
     "verses_approx": 41, "key_hymns": ["Phala Shruti - fruits of recitation"],
     "lines": (1601, 1686),
     "phala": "The Mother's own promise of all benefits from sincere recitation"},
    {"num": 13, "title_sa": "सुरथवैश्ययोर्वरप्रदानं", "title_en": "Suratha Vaiśya Vara Pradāna",
     "subtitle": "The Granting of Boons to King Suratha and the Merchant", "charita": "uttama", "deity": "Mahasaraswati",
     "narrator": "Sage Medhas",
     "summary": "Hearing Medhas' teaching, King Suratha and the merchant Samadhi go to the riverbank, fashion an earthen image of Devi, and worship her with intense austerity for three years. Devi appears and grants them their wishes: Suratha asks for restoration of his kingdom and a future imperishable rule (he will become Savarni Manu); Samadhi asks for knowledge that uproots attachment - the gift of liberation.",
     "verses_approx": 30, "key_hymns": ["Devi grants boons - Savarni Manu prophecy"],
     "lines": (1690, 1743),
     "phala": "Both worldly fulfillment AND moksha - whatever the heart sincerely asks"},
]


# ============================================================
# Anga line ranges in durga700.itx (existing)
# ============================================================

ANGAS_FROM_DURGA700 = [
    {"id": "argala", "name_sa": "अर्गला स्तोत्रम्", "name_en": "Argala Stotram",
     "subtitle": "The Hymn of the Bolt - removes obstacles, opens the heart",
     "phase": "pre", "verse_count": 27, "rishi": "Vishnu",
     "chhanda": "Anushtup", "devata": "Mahalakshmi",
     "summary": "Argala means 'bolt' - this hymn unbolts the door of grace. Composed by Vishnu rishi, each verse ends with the refrain 'rūpaṃ dehi jayaṃ dehi yaśo dehi dviṣo jahi' - 'grant me beauty, grant victory, grant fame, destroy enmity.' Traditionally recited as part of the Trayanga (along with Kavacha and Keelaka) before the Saptashati paath.",
     "lines": (45, 108)},
    {"id": "keelaka", "name_sa": "कीलक स्तोत्रम्", "name_en": "Keelaka Stotram",
     "subtitle": "The Unsealing - removes the lock that guards the mantras",
     "phase": "pre", "verse_count": 16, "rishi": "Shiva",
     "chhanda": "Anushtup", "devata": "Mahasaraswati",
     "summary": "Keelaka means 'wedge' or 'pin'. The mantras of Devi Mahatmyam are said to be locked (keelita) so they bear fruit only for the worthy. This stotram unlocks them. Composed by Shiva rishi. Recited as part of the Trayanga, after Argala and before the chapters.",
     "lines": (110, 150)},
    {"id": "kavacha", "name_sa": "देवी कवचम्", "name_en": "Devi Kavacham",
     "subtitle": "The Armor of the Goddess - protection of body, mind, and direction",
     "phase": "pre", "verse_count": 61, "rishi": "Brahma",
     "chhanda": "Anushtup", "devata": "Chamunda",
     "summary": "The Kavacha names the nine forms of Durga (Navadurga - Shailaputri, Brahmacharini, Chandraghanta, Kushmanda, Skandamata, Katyayani, Kalaratri, Mahagauri, Siddhidatri) and asks each to protect a part of the body, a direction, an organ, and a stage of life. The most comprehensive protective hymn in the Shakta tradition. 61 verses.",
     "lines": (151, 280)},
    {"id": "kshamapana", "name_sa": "अपराधक्षमापणस्तोत्रम्", "name_en": "Aparadha Kshamapana Stotram",
     "subtitle": "Forgiveness for Transgressions",
     "phase": "post", "verse_count": 9, "rishi": "Traditional",
     "chhanda": "", "devata": "Devi",
     "summary": "Concluding hymn asking forgiveness for any errors, omissions, or improper procedures during the recitation. Acknowledges that the devotee, lacking complete knowledge of mantras, ritual, and purity, appeals to the Mother's compassion to make the offering whole.",
     "lines": (1748, 1772)},
    {"id": "devi-suktam", "name_sa": "देवी सूक्तम्", "name_en": "Devi Suktam (Vagambhrini Suktam)",
     "subtitle": "The Vedic Hymn of the Goddess - Rig Veda 10.125",
     "phase": "post", "verse_count": 8, "rishi": "Vak (daughter of Ambhrina)",
     "chhanda": "Trishtup", "devata": "Para Brahman",
     "summary": "From Rig Veda 10.125 - the famous hymn where Vak, daughter of sage Ambhrina, declares herself to be the Supreme: 'I move with the Rudras, the Vasus, the Adityas. I am the queen, the gatherer of treasures. I am the wind, the rain, the breath. I bend the bow for Rudra to slay the hater of devotion. I dwell in the waters, in the highest heaven; from there I extend over all worlds.' The capstone of the entire Saptashati recitation.",
     "lines": (1774, 1825)},
]


# ============================================================
# Saptashloki Durga (Amba Stuti) - hardcoded ITRANS
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
# Builders
# ============================================================

def build_chapter(itx, ch):
    raw = extract_lines(itx, *ch["lines"])
    cleaned = clean_itrans(raw)
    return {
        "num": ch["num"],
        "titleSa": ch["title_sa"],
        "titleEn": ch["title_en"],
        "subtitle": ch["subtitle"],
        "charita": ch["charita"],
        "deity": ch["deity"],
        "narrator": ch["narrator"],
        "summary": ch["summary"],
        "versesApprox": ch["verses_approx"],
        "keyHymns": ch["key_hymns"],
        "phala": ch["phala"],
        "devanagari": to_devanagari(cleaned).strip(),
        "iast": to_iast(cleaned).strip(),
    }


def build_anga_from_itrans_lines(itx, a):
    raw = extract_lines(itx, *a["lines"])
    cleaned = clean_itrans(raw)
    return base_anga(a, to_devanagari(cleaned).strip(), to_iast(cleaned).strip())


def base_anga(meta, devanagari, iast):
    return {
        "id": meta["id"],
        "nameSa": meta["name_sa"],
        "nameEn": meta["name_en"],
        "subtitle": meta["subtitle"],
        "phase": meta["phase"],
        "verseCount": meta["verse_count"],
        "rishi": meta["rishi"],
        "chhanda": meta["chhanda"],
        "devata": meta["devata"],
        "summary": meta["summary"],
        "devanagari": devanagari,
        "iast": iast,
    }


def build_devi_atharva():
    """Devi Atharvashirsha from ITX file."""
    itx = read_file("source_devi_atharva.itx")
    cleaned = clean_itrans(itx)
    meta = {
        "id": "devi-atharva",
        "name_sa": "देव्यथर्वशीर्षम्",
        "name_en": "Devi Atharvashirsha",
        "subtitle": "The Upanishad of the Goddess - Devi declares 'I am Brahman'",
        "phase": "pre",
        "verse_count": 32,
        "rishi": "Atharva (Upanishadic)",
        "chhanda": "Mixed",
        "devata": "Devi as Brahman",
        "summary": (
            "From the Atharva Veda Upanishadic corpus. Also called Devi Upanishad. "
            "When the gods asked 'Who are you, Mahadevi?', she replied: 'I am Brahman. "
            "From me the universe of Prakriti and Purusha emerges. I am void and non-void; "
            "I am bliss and non-bliss; I am knowledge and ignorance.' One of the most "
            "powerful Vedantic declarations of Devi as the Para Brahman, beyond all forms. "
            "Traditionally recited during Devi worship, especially during Navaratri."
        ),
    }
    return base_anga(meta, to_devanagari(cleaned).strip(), to_iast(cleaned).strip())


def build_rahasya(filename, meta):
    """Build a Rahasya from a Devanagari source text file."""
    deva = read_file(filename).strip()
    return base_anga(meta, deva, deva_to_iast(deva).strip())


def build_kunjika():
    itx = read_file("source_kunjika.itx")
    cleaned = clean_itrans(itx)
    meta = {
        "id": "kunjika",
        "name_sa": "सिद्ध कुञ्जिका स्तोत्रम्",
        "name_en": "Siddha Kunjika Stotram",
        "subtitle": "The Master Key - synthesizing Kavacha, Argala, and Keelaka",
        "phase": "post",
        "verse_count": 14,
        "rishi": "Shiva (taught to Parvati)",
        "chhanda": "Anushtup",
        "devata": "Chamunda",
        "summary": (
            "The 'master key' (kunjika) stotram. Tradition holds that one who recites Kunjika "
            "alone receives the merit of the entire Saptashati - without needing to recite "
            "Kavacha, Argala, Keelaka, the Rahasyas, or any other anga. Sourced from the "
            "Rudrayamala Tantra. Contains the powerful Navarna Mantra: 'Aim Hreem Kleem "
            "Chamundayai Vichche'. 14 verses, brief but exceptionally potent."
        ),
    }
    return base_anga(meta, to_devanagari(cleaned).strip(), to_iast(cleaned).strip())


def build_saptashloki():
    cleaned = SAPTASHLOKI_TEXT
    meta = {
        "id": "saptashloki",
        "name_sa": "सप्तश्लोकी दुर्गा",
        "name_en": "Saptashloki Durga (Amba Stuti)",
        "subtitle": "Seven verses - the essence of the entire Saptashati",
        "phase": "pre",
        "verse_count": 7,
        "rishi": "Shiva",
        "chhanda": "Mixed",
        "devata": "Durga",
        "summary": (
            "When Lord Shiva was asked by Parvati for the simplest path to Devi's grace, "
            "he condensed the entire Saptashati into seven verses. Tradition holds that "
            "reciting Saptashloki alone, with sincere devotion, yields the fruit of the "
            "full 700-verse paath. Each verse contains the seed of a major hymn from "
            "the parent text."
        ),
    }
    return base_anga(meta, to_devanagari(cleaned).strip(), to_iast(cleaned).strip())


def build_chandika_dhyana():
    itx = read_file("source_durga700.itx")
    raw = extract_lines(itx, 35, 43)
    cleaned = clean_itrans(raw)
    meta = {
        "id": "chandika-dhyana",
        "name_sa": "श्री चण्डिका ध्यानम्",
        "name_en": "Sri Chandika Dhyanam",
        "subtitle": "Meditation verse on Devi Chandika - opens the paath",
        "phase": "pre",
        "verse_count": 2,
        "rishi": "Traditional",
        "chhanda": "",
        "devata": "Chandika",
        "summary": (
            "The opening dhyana verse on Devi Chandika - bandhuka-flower-hued, garlanded "
            "with skulls, three-eyed, holding book, rosary, boon-giving and abhaya mudras. "
            "Sets the visualization for the entire recitation."
        ),
    }
    return base_anga(meta, to_devanagari(cleaned).strip(), to_iast(cleaned).strip())


# ============================================================
# Navarna mantra
# ============================================================

NAVARNA_MANTRA = {
    "id": "navarna",
    "nameSa": "नवार्ण मन्त्र",
    "nameEn": "Navarna Mantra",
    "subtitle": "The nine-syllable mantra - heart of all Devi sadhana",
    "devanagari": "ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे",
    "iast": "oṃ aiṃ hrīṃ klīṃ cāmuṇḍāyai vicce",
    "summary": (
        "The Navarna ('nine-letter') mantra is the supreme bija mantra of Durga Saptashati. "
        "Each syllable encodes a cosmic principle. Recited 108 times before and after the "
        "paath, and at the junction of each chapter (chapter-sandhi) for sealing the energy."
    ),
    "wordBreakdown": [
        {"word": "ॐ", "iast": "oṃ", "meaning": "Pranava - the primordial sound, all-encompassing"},
        {"word": "ऐं", "iast": "aiṃ", "meaning": "Saraswati bija - knowledge, vak (speech), wisdom"},
        {"word": "ह्रीं", "iast": "hrīṃ", "meaning": "Lakshmi/Bhuvaneshwari bija - heart of Devi, all auspiciousness"},
        {"word": "क्लीं", "iast": "klīṃ", "meaning": "Kali/Kama bija - attraction, fulfillment of desires"},
        {"word": "चामुण्डायै", "iast": "cāmuṇḍāyai", "meaning": "to Chamunda - the unified destroyer of Chanda-Munda"},
        {"word": "विच्चे", "iast": "vicce", "meaning": "bestower of liberation; the seal of the mantra"},
    ],
}


# ============================================================
# Charitas
# ============================================================

CHARITAS = [
    {"id": "prathama", "name_sa": "प्रथम चरित्र", "name_en": "Prathama Charita",
     "deity": "Mahakali", "deity_sa": "महाकाली", "guna": "Tamasika",
     "principle": "Destroyer of ignorance",
     "chapters": [1],
     "narrative": "Madhu-Kaitabha Vadha - awakening of Vishnu through Yoganidra",
     "color_label": "deep blue-black (Kali's complexion)",
     "summary": "The First Episode contains a single chapter. It tells of Vishnu in cosmic yogic sleep at the dissolution of the universe, when the demons Madhu and Kaitabha emerge from his ear-wax to attack Brahma. Brahma invokes the Yoganidra of Vishnu - Mahamaya, the Devi - who withdraws from him so he may awaken. Mahakali presides. The hymn here is Brahma-Stuti."},
    {"id": "madhyama", "name_sa": "मध्यम चरित्र", "name_en": "Madhyama Charita",
     "deity": "Mahalakshmi", "deity_sa": "महालक्ष्मी", "guna": "Rajasika",
     "principle": "Sustainer, sovereign of action",
     "chapters": [2, 3, 4],
     "narrative": "Mahishasura Vadha - the slaying of the buffalo demon",
     "color_label": "golden",
     "summary": "The Middle Episode is the most central section of the text. The gods pour their combined energies into a single radiant form - Devi Durga - and arm her with their weapons. She slays Mahishasura's army, then the buffalo demon himself, becoming Mahishasura Mardini. Mahalakshmi presides. The closing chapter contains the great Shakradi Stuti. Tradition holds: never interrupt this charita mid-recitation."},
    {"id": "uttama", "name_sa": "उत्तम चरित्र", "name_en": "Uttama Charita",
     "deity": "Mahasaraswati", "deity_sa": "महासरस्वती", "guna": "Sattvika",
     "principle": "Creator of knowledge, granter of liberation",
     "chapters": [5, 6, 7, 8, 9, 10, 11, 12, 13],
     "narrative": "Shumbha-Nishumbha Vadha + the granting of boons",
     "color_label": "white-pearlescent",
     "summary": "The Final Episode spans nine chapters and is the longest. Devi as Ambika (Kaushiki, born from Parvati's body-sheath) confronts Shumbha and Nishumbha. Kali emerges from her brow; the Saptamatrika emerge from the gods. After slaying Dhumralochana, Chanda-Munda, Raktabija, Nishumbha, and finally Shumbha, Devi receives the great Narayani Stuti. The text closes with the Phala Shruti and the boons granted to King Suratha and Samadhi. Mahasaraswati presides."},
]


# ============================================================
# Navadurga - 9 forms of Durga
# ============================================================

NAVADURGA = [
    {
        "day": 1, "id": "shailaputri",
        "name_sa": "शैलपुत्री", "name_en": "Shailaputri",
        "meaning": "Daughter of the Mountain (Himavan)",
        "color": "Red",
        "vahana": "Bull (Nandi)",
        "weapons": "Trishul, Lotus",
        "story": "Born as the daughter of Himalaya. The first incarnation of Adi Shakti after Sati's self-immolation - reborn as Parvati. She represents the foundation, the mountain, the unwavering ground of being.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं शैलपुत्र्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ śailaputryai namaḥ",
        "dhyana": "वन्दे वाञ्छितलाभाय चन्द्रार्धकृतशेखराम्। वृषारूढां शूलधरां शैलपुत्रीं यशस्विनीम्॥",
        "boon": "Stability, courage, foundation for sadhana"
    },
    {
        "day": 2, "id": "brahmacharini",
        "name_sa": "ब्रह्मचारिणी", "name_en": "Brahmacharini",
        "meaning": "She who walks in Brahman / The ascetic",
        "color": "Royal Blue",
        "vahana": "On foot (no vahana)",
        "weapons": "Rudraksha mala and kamandalu",
        "story": "Parvati's incarnation as the great tapasvini who performed thousand-year austerities to win Shiva. She lived on bilva leaves, then nothing - earning the name Aparna. Her tapas was so intense that even Brahma had to grant her boon.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं ब्रह्मचारिण्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ brahmacāriṇyai namaḥ",
        "dhyana": "दधाना करपद्माभ्यामक्षमालाकमण्डलू। देवी प्रसीदतु मयि ब्रह्मचारिण्यनुत्तमा॥",
        "boon": "Devotion, perseverance, unwavering vow-keeping"
    },
    {
        "day": 3, "id": "chandraghanta",
        "name_sa": "चन्द्रघण्टा", "name_en": "Chandraghanta",
        "meaning": "She who wears the half-moon shaped like a bell on her forehead",
        "color": "Yellow",
        "vahana": "Tiger / Lion",
        "weapons": "Trishul, Gada, Bow, Arrow, Sword - 10 hands",
        "story": "After Parvati's marriage to Shiva, she adorned the half-moon on her forehead - shaped like a bell (ghanta). She rides into battle with ten arms, ferocious yet calm. The bell sound terrifies all demons.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं चन्द्रघण्टायै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ candraghaṇṭāyai namaḥ",
        "dhyana": "पिण्डजप्रवरारूढा चण्डकोपास्त्रकैर्युता। प्रसादं तनुते मह्यं चन्द्रघण्टेति विश्रुता॥",
        "boon": "Removal of obstacles, courage in battle, peace amid chaos"
    },
    {
        "day": 4, "id": "kushmanda",
        "name_sa": "कूष्माण्डा", "name_en": "Kushmanda",
        "meaning": "She who created the cosmic egg with her divine smile",
        "color": "Green",
        "vahana": "Tiger / Lion",
        "weapons": "Bow, Arrow, Lotus, Rosary, Pot of Nectar - 8 hands",
        "story": "When the universe was nothing but darkness, Devi smiled - and from that smile the cosmic egg was born. The sun resides within her body. She is the source of all radiance.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं कूष्माण्डायै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ kūṣmāṇḍāyai namaḥ",
        "dhyana": "सुरासम्पूर्णकलशं रुधिराप्लुतमेव च। दधाना हस्तपद्माभ्यां कूष्माण्डा शुभदास्तु मे॥",
        "boon": "Health, wealth, vitality, brilliance"
    },
    {
        "day": 5, "id": "skandamata",
        "name_sa": "स्कन्दमाता", "name_en": "Skandamata",
        "meaning": "Mother of Skanda (Kartikeya)",
        "color": "Grey",
        "vahana": "Lion",
        "weapons": "Lotus in two hands, Skanda on lap, abhaya mudra",
        "story": "Mother of Skanda (Kartikeya) - the warrior-god who slew Tarakasura. She holds the infant Skanda on her lap while seated on a lion. The most maternal of the nine forms - represents the protective Mother.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं स्कन्दमात्रै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ skandamātrai namaḥ",
        "dhyana": "सिंहासनगता नित्यं पद्माश्रितकरद्वया। शुभदास्तु सदा देवी स्कन्दमाता यशस्विनी॥",
        "boon": "Love of children, motherly grace, protection of family"
    },
    {
        "day": 6, "id": "katyayani",
        "name_sa": "कात्यायनी", "name_en": "Katyayani",
        "meaning": "Daughter of Sage Katyayana / She who is fierce",
        "color": "Orange",
        "vahana": "Lion",
        "weapons": "Sword, Lotus - 4 hands",
        "story": "Born from the combined wrath of all the gods to slay Mahishasura. Sage Katyayana worshipped her first, hence the name. The form invoked in chapters 2-4 of the Saptashati. The slayer of the buffalo demon.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं कात्यायन्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ kātyāyanyai namaḥ",
        "dhyana": "चन्द्रहासोज्ज्वलकरा शार्दूलवरवाहना। कात्यायनी शुभं दद्याद्देवी दानवघातिनी॥",
        "boon": "Marriage, partnership, slaying of evil"
    },
    {
        "day": 7, "id": "kalaratri",
        "name_sa": "कालरात्रि", "name_en": "Kalaratri",
        "meaning": "The Dark Night / The Night of Time itself",
        "color": "Royal Blue / Black",
        "vahana": "Donkey",
        "weapons": "Sword, Iron hook, Abhaya mudra, Vara mudra",
        "story": "The most fierce form. Black as the dark night, hair flowing wild, three eyes blazing, breathing fire. She emerged from Parvati's skin as Kaushiki and slew Raktabija. The destroyer of all darkness - despite her terrifying form, she is also called Shubhankari ('she who brings auspiciousness').",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं कालरात्र्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ kālarātryai namaḥ",
        "dhyana": "एकवेणी जपाकर्णपूरा नग्ना खरास्थिता। लम्बोष्ठी कर्णिकाकर्णी तैलाभ्यक्तशरीरिणी॥",
        "boon": "Removal of darkness, ignorance, evil spirits, deepest fears"
    },
    {
        "day": 8, "id": "mahagauri",
        "name_sa": "महागौरी", "name_en": "Mahagauri",
        "meaning": "The Greatly White One / Pure radiance",
        "color": "Pink",
        "vahana": "Bull",
        "weapons": "Trishul, Damaru, Abhaya mudra, Vara mudra",
        "story": "After Parvati's tapas turned her dark from austerity, Shiva bathed her in the Ganges and she became dazzlingly white - Mahagauri. The eighth night of Navratri, Durgashtami, is dedicated to her - one of the most important nights of the year for Devi sadhana.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं महागौर्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ mahāgauryai namaḥ",
        "dhyana": "श्वेते वृषे समारूढा श्वेताम्बरधरा शुचिः। महागौरी शुभं दद्यान्महादेवप्रमोददा॥",
        "boon": "Purification of all sins, peace, prosperity, devotion"
    },
    {
        "day": 9, "id": "siddhidatri",
        "name_sa": "सिद्धिदात्री", "name_en": "Siddhidatri",
        "meaning": "Bestower of all siddhis (perfections)",
        "color": "Sky Blue / Purple",
        "vahana": "Lotus / Lion",
        "weapons": "Chakra, Gada, Lotus, Shankha",
        "story": "On the ninth night, Devi grants all eight major siddhis (anima, mahima, garima, laghima, prapti, prakamya, ishitva, vashitva). It is from her that even Shiva received the siddhis - hence Ardhanarishvara form. The supreme bestower.",
        "mantra_sa": "ॐ ऐं ह्रीं क्लीं सिद्धिदात्र्यै नमः",
        "mantra_iast": "oṃ aiṃ hrīṃ klīṃ siddhidātryai namaḥ",
        "dhyana": "सिद्धगन्धर्वयक्षाद्यैरसुरैरमरैरपि। सेव्यमाना सदा भूयात् सिद्धिदा सिद्धिदायिनी॥",
        "boon": "All worldly and spiritual powers - the ultimate fulfillment"
    },
]


# ============================================================
# Saptamatrika - 7 Mothers
# ============================================================

SAPTAMATRIKA = [
    {"id": "brahmani", "name_sa": "ब्राह्मणी", "name_en": "Brahmani",
     "from": "Brahma", "vahana": "Hamsa (swan)", "weapon": "Akshamala, Kamandalu, Veda",
     "shakti_of": "Brahma - creator energy",
     "description": "Emerged from Brahma's tejas (energy) - white-clad, four-faced, holding the rosary and water-pot. The shakti of creative power."},
    {"id": "maheshvari", "name_sa": "माहेश्वरी", "name_en": "Maheshvari",
     "from": "Shiva", "vahana": "Nandi (bull)", "weapon": "Trishul, Damaru, Akshamala",
     "shakti_of": "Shiva - dissolving force",
     "description": "Emerged from Shiva's tejas - three-eyed, crescent moon on forehead, white-bodied. The shakti of cosmic dissolution and yogic stillness."},
    {"id": "kaumari", "name_sa": "कौमारी", "name_en": "Kaumari",
     "from": "Skanda (Kartikeya)", "vahana": "Peacock", "weapon": "Spear (Shakti), bow",
     "shakti_of": "Skanda - youthful warrior",
     "description": "Emerged from Skanda's tejas - red-bodied, riding the peacock, holding the shakti spear. The shakti of youthful battle-fire."},
    {"id": "vaishnavi", "name_sa": "वैष्णवी", "name_en": "Vaishnavi",
     "from": "Vishnu", "vahana": "Garuda (eagle)", "weapon": "Shankha, Chakra, Gada, Padma",
     "shakti_of": "Vishnu - sustaining grace",
     "description": "Emerged from Vishnu's tejas - dark-blue, four-armed, all the Vishnu weapons. The shakti of preservation and dharmic order."},
    {"id": "varahi", "name_sa": "वाराही", "name_en": "Varahi",
     "from": "Varaha (Vishnu's boar avatar)", "vahana": "Buffalo / Boar", "weapon": "Hala (plough), pestle",
     "shakti_of": "Varaha - earth-rescuing might",
     "description": "Emerged from Varaha's tejas - boar-faced, dark-bodied, holding the plough. The shakti of raw earth-power that lifted Bhumi from the cosmic ocean."},
    {"id": "narasimhi", "name_sa": "नारसिंही", "name_en": "Narasimhi",
     "from": "Narasimha (Vishnu's man-lion avatar)", "vahana": "Lion", "weapon": "Claws",
     "shakti_of": "Narasimha - protective fury",
     "description": "Emerged from Narasimha's tejas - lion-faced, golden-bodied, claws extended. The shakti of fearless devotion and protection of the bhakta."},
    {"id": "aindri", "name_sa": "ऐन्द्री", "name_en": "Aindri (Indrani)",
     "from": "Indra", "vahana": "Airavata (elephant)", "weapon": "Vajra (thunderbolt)",
     "shakti_of": "Indra - king of the gods, lightning",
     "description": "Emerged from Indra's tejas - thousand-eyed, riding Airavata, vajra in hand. The shakti of sovereign rulership and lightning-precise action."},
]


# ============================================================
# Hymns - extracted as standalone for the Hymns view
# ============================================================

# Note: 'devanagari' for hymns is hand-curated to ensure clean extraction
# Source: Sanskrit Documents durga700 lines

HYMNS = [
    {
        "id": "brahma-stuti",
        "name_sa": "ब्रह्म स्तुति",
        "name_en": "Brahma-Stuti",
        "subtitle": "Brahma's first hymn to Yoganidra",
        "from_chapter": 1,
        "verse_range": "Verses 73-87",
        "summary": (
            "When the demons Madhu and Kaitabha emerged from Vishnu's ear-wax to attack Brahma "
            "during the cosmic dissolution, Brahma turned to the Yoganidra of Vishnu - the Divine "
            "Mother in her unmanifest sleep-form - and offered this hymn. The very first hymn to "
            "Devi in the Saptashati. She withdrew from Vishnu, allowing him to awaken and slay "
            "the demons."
        ),
        "key_line": "त्वमेव सर्वजननी मूलप्रकृतिरीश्वरी"
    },
    {
        "id": "shakradi-stuti",
        "name_sa": "शक्रादि स्तुति",
        "name_en": "Shakradi Stuti",
        "subtitle": "Indra and the gods praise Devi after Mahishasura's slaying",
        "from_chapter": 4,
        "verse_range": "All of chapter 4",
        "summary": (
            "After Devi slays Mahishasura, the gods restored to their realms offer one of the "
            "most loved hymns of the text. Indra (Shakra) leads. They praise Devi as the cause "
            "of all causes, the supreme Shakti who pervades all forms. In response, Devi grants "
            "the boon of remembrance: she promises to manifest whenever the world is endangered "
            "by demonic forces."
        ),
        "key_line": "या श्रीः स्वयं सुकृतिनां भवनेष्वलक्ष्मीः"
    },
    {
        "id": "ya-devi",
        "name_sa": "या देवी सर्वभूतेषु",
        "name_en": "Ya Devi Sarva Bhuteshu (Aparajita Stuti)",
        "subtitle": "The most chanted hymn from the Saptashati - Devi in all beings",
        "from_chapter": 5,
        "verse_range": "Verses 14-78 (Tantric Devi Suktam)",
        "summary": (
            "The 'Ya Devi Sarva Bhuteshu' hymn is the most beloved and most chanted portion of "
            "the Saptashati. The structure: 'To the Devi who in all beings is established as "
            "[X], salutations, salutations, salutations to her.' Each refrain repeats three "
            "times. She is praised as Vishnu-Maya, Chetana (consciousness), Buddhi (intelligence), "
            "Nidra (sleep), Kshudha (hunger), Chhaya (shadow), Shakti, Trishna (thirst), Kshanti "
            "(forgiveness), Jati (birth), Lajja (modesty), Shanti (peace), Shraddha (faith), "
            "Kanti (beauty), Lakshmi, Vritti (activity), Smriti (memory), Daya (compassion), "
            "Tushti (contentment), Matri (Mother), Bhranti (delusion). Singing this hymn weaves "
            "the Mother into every dimension of the seeker's being."
        ),
        "key_line": "या देवी सर्वभूतेषु शक्तिरूपेण संस्थिता। नमस्तस्यै नमस्तस्यै नमस्तस्यै नमो नमः॥",
        "key_line_iast": "yā devī sarvabhūteṣu śaktirūpeṇa saṃsthitā | namastasyai namastasyai namastasyai namo namaḥ ||",
        "aspects": [
            {"sa": "विष्णुमायेति", "iast": "viṣṇumāyeti", "en": "as the cosmic illusion of Vishnu"},
            {"sa": "चेतनेत्यभिधीयते", "iast": "cetanetyabhidhīyate", "en": "as consciousness itself"},
            {"sa": "बुद्धिरूपेण", "iast": "buddhirūpeṇa", "en": "as the form of intelligence"},
            {"sa": "निद्रारूपेण", "iast": "nidrārūpeṇa", "en": "as the form of sleep"},
            {"sa": "क्षुधारूपेण", "iast": "kṣudhārūpeṇa", "en": "as the form of hunger"},
            {"sa": "छायारूपेण", "iast": "chāyārūpeṇa", "en": "as the form of shadow"},
            {"sa": "शक्तिरूपेण", "iast": "śaktirūpeṇa", "en": "as the form of power"},
            {"sa": "तृष्णारूपेण", "iast": "tṛṣṇārūpeṇa", "en": "as the form of thirst"},
            {"sa": "क्षान्तिरूपेण", "iast": "kṣāntirūpeṇa", "en": "as the form of forgiveness"},
            {"sa": "जातिरूपेण", "iast": "jātirūpeṇa", "en": "as the form of species/birth"},
            {"sa": "लज्जारूपेण", "iast": "lajjārūpeṇa", "en": "as the form of modesty"},
            {"sa": "शान्तिरूपेण", "iast": "śāntirūpeṇa", "en": "as the form of peace"},
            {"sa": "श्रद्धारूपेण", "iast": "śraddhārūpeṇa", "en": "as the form of faith"},
            {"sa": "कान्तिरूपेण", "iast": "kāntirūpeṇa", "en": "as the form of beauty"},
            {"sa": "लक्ष्मीरूपेण", "iast": "lakṣmīrūpeṇa", "en": "as the form of prosperity"},
            {"sa": "वृत्तिरूपेण", "iast": "vṛttirūpeṇa", "en": "as the form of activity"},
            {"sa": "स्मृतिरूपेण", "iast": "smṛtirūpeṇa", "en": "as the form of memory"},
            {"sa": "दयारूपेण", "iast": "dayārūpeṇa", "en": "as the form of compassion"},
            {"sa": "तुष्टिरूपेण", "iast": "tuṣṭirūpeṇa", "en": "as the form of contentment"},
            {"sa": "मातृरूपेण", "iast": "mātṛrūpeṇa", "en": "as the form of Mother"},
            {"sa": "भ्रान्तिरूपेण", "iast": "bhrāntirūpeṇa", "en": "as the form of delusion (which she transcends)"},
        ]
    },
    {
        "id": "narayani-stuti",
        "name_sa": "नारायणी स्तुति",
        "name_en": "Narayani Stuti",
        "subtitle": "The grandest hymn - to Devi as the supreme refuge",
        "from_chapter": 11,
        "verse_range": "All of chapter 11",
        "summary": (
            "The most exalted hymn of the Saptashati. After Devi slays Shumbha, the gods - "
            "freed from oppression - offer this hymn praising her as Narayani: the consort "
            "and shakti of Narayana, but also the cause of creation-preservation-destruction "
            "in her own right. Each refrain ends 'Narayani Namo'stute' - 'Salutations to "
            "you, O Narayani.' Devi grants the boon: whoever recites this hymn with devotion "
            "is freed from all calamities."
        ),
        "key_line": "सर्वमङ्गलमाङ्गल्ये शिवे सर्वार्थसाधिके। शरण्ये त्र्यम्बके गौरि नारायणि नमोऽस्तु ते॥",
        "key_line_iast": "sarvamaṅgalamāṅgalye śive sarvārthasādhike | śaraṇye tryambake gauri nārāyaṇi namo'stu te ||"
    },
    {
        "id": "phala-shruti",
        "name_sa": "फलश्रुति",
        "name_en": "Phala Shruti",
        "subtitle": "Devi's own promise of the fruits of recitation",
        "from_chapter": 12,
        "verse_range": "All of chapter 12",
        "summary": (
            "Devi herself declares the fruits of reciting this Mahatmyam. Whoever recites it "
            "on Ashtami, Chaturdashi, and Navami with single-pointed devotion will be freed "
            "from all afflictions: poverty, illness, fear of enemies, fire, drought, captivity, "
            "evil portents. The text itself is established as a mantra; the recitation as a "
            "great yajna. Hearing or chanting even a single verse with bhava confers protection."
        ),
        "key_line": "इदं स्तोत्रं पठित्वा तु मम स्तोत्रमिदं नरः। पठेद्यो भक्तिमान्नित्यं स याति परमां गतिम्॥"
    },
]


# ============================================================
# Navratri practice
# ============================================================

NAVRATRI = {
    "intro": (
        "Navratri ('Nine Nights') is the most important festival for Devi sadhana. Across nine "
        "consecutive nights, the Mother is worshipped in her nine forms (Navadurga). The first "
        "three nights honor Mahakali (destruction of vasanas), the middle three Mahalakshmi "
        "(prosperity and grace), and the final three Mahasaraswati (knowledge and liberation). "
        "Many devotees complete one full Saptashati paath each night - 9 complete recitations - "
        "or split the chapters following the Kerala Nitya Chandi sequence."
    ),
    "festivals": [
        {"name": "Sharad Navratri (Maha Navratri)", "month": "Ashvin (Sep-Oct)",
         "note": "The most important - leads to Vijayadashami / Dussehra"},
        {"name": "Chaitra Navratri (Vasanta Navratri)", "month": "Chaitra (Mar-Apr)",
         "note": "Spring Navratri - leads to Ram Navami"},
        {"name": "Magha Gupta Navratri", "month": "Magha (Jan-Feb)",
         "note": "Hidden Navratri - for advanced sadhakas, focus on tantric forms"},
        {"name": "Ashadha Gupta Navratri", "month": "Ashadha (Jun-Jul)",
         "note": "Hidden Navratri - the second secret Navratri"},
    ],
    "kerala_nitya_chandi": {
        "name": "Kerala Nitya Chandi (1-2-1-4-2-1-2 sequence)",
        "description": (
            "A 7-day sequence covering the entire Saptashati once. Each day's chapter count "
            "is chosen so the Madhyama Charita (Ch 2-4) is never broken. Practiced daily "
            "throughout the year by serious sadhakas."
        ),
        "schedule": [
            {"day": 1, "chapters": "Chapter 1", "charita": "Prathama complete"},
            {"day": 2, "chapters": "Chapters 2 + 3", "charita": "Madhyama begins"},
            {"day": 3, "chapters": "Chapter 4", "charita": "Madhyama complete (must not break)"},
            {"day": 4, "chapters": "Chapters 5, 6, 7, 8", "charita": "Uttama section 1"},
            {"day": 5, "chapters": "Chapters 9 + 10", "charita": "Uttama section 2"},
            {"day": 6, "chapters": "Chapter 11", "charita": "Narayani Stuti"},
            {"day": 7, "chapters": "Chapters 12 + 13", "charita": "Phala Shruti and conclusion"},
        ]
    },
    "navratri_days": [
        {"night": 1, "form": "Shailaputri", "color": "Red",
         "focus": "Foundation, courage, beginning the journey"},
        {"night": 2, "form": "Brahmacharini", "color": "Royal Blue",
         "focus": "Tapas, vow-keeping, austerity"},
        {"night": 3, "form": "Chandraghanta", "color": "Yellow",
         "focus": "Removal of obstacles, courage in battle"},
        {"night": 4, "form": "Kushmanda", "color": "Green",
         "focus": "Vitality, creativity, abundance"},
        {"night": 5, "form": "Skandamata", "color": "Grey",
         "focus": "Maternal grace, protection of family"},
        {"night": 6, "form": "Katyayani", "color": "Orange",
         "focus": "Slaying inner demons, partnership"},
        {"night": 7, "form": "Kalaratri", "color": "Royal Blue / Black",
         "focus": "Removal of darkest fears - one of the most powerful nights"},
        {"night": 8, "form": "Mahagauri (Durgashtami)", "color": "Pink",
         "focus": "Purification of all sins - traditionally the most sacred night"},
        {"night": 9, "form": "Siddhidatri (Maha Navami)", "color": "Sky Blue / Purple",
         "focus": "Bestowal of all siddhis - the culmination"},
    ]
}


# ============================================================
# Mahishasura Mardini - 18 Weapons
# ============================================================

EIGHTEEN_WEAPONS = {
    "intro": (
        "When the gods could not defeat Mahishasura, they poured their combined energies into a "
        "single radiant form - Devi Durga. Each god then gave her one of his weapons. With these "
        "eighteen arms, she rode forth on her lion to slay the buffalo demon. Each weapon "
        "represents a divine quality."
    ),
    "weapons": [
        {"weapon": "Trishul (Trident)", "from": "Shiva", "represents": "Three gunas under Devi's command"},
        {"weapon": "Chakra (Discus)", "from": "Vishnu", "represents": "Cyclical time, dharmic order"},
        {"weapon": "Shankha (Conch)", "from": "Varuna", "represents": "Pranava, primordial sound"},
        {"weapon": "Agni Astra (Flame Spear)", "from": "Agni", "represents": "Purificatory fire"},
        {"weapon": "Dhanush (Bow)", "from": "Vayu", "represents": "Wind-precision, far-reaching action"},
        {"weapon": "Bana (Arrows)", "from": "Surya", "represents": "Sun-rays, illuminating insight"},
        {"weapon": "Vajra (Thunderbolt)", "from": "Indra", "represents": "Indestructible will"},
        {"weapon": "Ghanta (Bell)", "from": "Airavata", "represents": "Sound that breaks demonic forces"},
        {"weapon": "Danda (Staff)", "from": "Yama", "represents": "Cosmic justice"},
        {"weapon": "Pasha (Noose)", "from": "Varuna (Lord of Waters)", "represents": "Binding of attachment"},
        {"weapon": "Akshamala (Rosary)", "from": "Brahma", "represents": "Mantra-power"},
        {"weapon": "Kamandalu (Water Pot)", "from": "Brahma", "represents": "Ascetic purity"},
        {"weapon": "Khadga (Sword)", "from": "Kala (Time)", "represents": "Cutting through delusion"},
        {"weapon": "Kheta (Shield)", "from": "Kala (Time)", "represents": "Protection from karmic blows"},
        {"weapon": "Parashu (Axe)", "from": "Vishvakarma", "represents": "Cleaving of obstacles"},
        {"weapon": "Padma (Lotus)", "from": "Kshirasagara", "represents": "Spiritual unfoldment"},
        {"weapon": "Naga-pasha (Serpent Noose)", "from": "Naga", "represents": "Kundalini Shakti"},
        {"weapon": "Simha (Lion - vahana)", "from": "Himavan", "represents": "Royal courage, raja-shakti"},
    ]
}


# ============================================================
# Beginner's path
# ============================================================

BEGINNER_PATH = [
    {"stage": 1, "title": "Start with Saptashloki",
     "desc": "Begin with just the seven verses of Saptashloki Durga. Recite daily until comfortable. This alone confers the merit of the full text."},
    {"stage": 2, "title": "Add the Navarna Mantra",
     "desc": "Begin reciting 'Aim Hreem Kleem Chamundayai Vichche' 108 times daily. The heart of all Devi sadhana."},
    {"stage": 3, "title": "Read one chapter at a time",
     "desc": "Begin with Chapter 1 (Prathama Charita). Read it for several days until familiar. Then add Chapters 2-4 as a unit (the Madhyama must always be complete)."},
    {"stage": 4, "title": "Add the Trayanga before chapters",
     "desc": "Once chapters are familiar, prefix the recitation with Argala, Keelaka, and Kavacha. This is the minimum traditional preparation."},
    {"stage": 5, "title": "Add Devi Suktam after chapters",
     "desc": "Conclude with the Vedic Devi Suktam (Vagambhrini Suktam) - the capstone."},
    {"stage": 6, "title": "Full Navangam paath",
     "desc": "Eventually move to the complete sequence: Saptashloki, Devi Atharvashirsha, Navarna, Trayanga, 13 chapters, 3 Rahasyas, Devi Suktam, Kunjika, Aparadha Kshamapana."},
    {"stage": 7, "title": "Daily Kerala Nitya Chandi",
     "desc": "Adopt the 7-day Nitya Chandi sequence - completing one full Saptashati each week. The path of the lifetime sadhaka."},
]


# ============================================================
# Chandi Homa info
# ============================================================

CHANDI_HOMA = {
    "intro": (
        "Chandi Homa is the fire ritual where the verses of the Saptashati are offered into "
        "the sacred fire as oblations. Each verse becomes a mantra; each oblation invokes "
        "Devi's grace directly. The most powerful homa in the Shakta tradition."
    ),
    "types": [
        {"name": "Chandi Homa (1x)",
         "desc": "Single recitation of the 700 verses with offerings into fire. Takes 4-6 hours with a pandit."},
        {"name": "Lakshachandi",
         "desc": "100,000 recitations of the Saptashati - performed by multiple priests over many days, sometimes years."},
        {"name": "Koti Chandi",
         "desc": "10,000,000 recitations - the supreme, performed for kingdom-level concerns or world-peace yajnas."},
        {"name": "Maha Chandi Homa",
         "desc": "The Chandi Homa accompanied by 1008 Trayangas, all angas, all rahasyas - takes 7-9 days."},
    ],
    "occasions": [
        "Navratri (especially on Ashtami, Navami)",
        "Family kalyana (marriages, beginnings)",
        "Removal of grave obstacles",
        "Atonement for serious karmic burden",
        "Restoration of health after long illness",
        "Land/property purification",
    ]
}


# ============================================================
# Paath order (extended)
# ============================================================

PAATH_ORDER = [
    {"phase": "pre", "id": "saptashloki", "label": "Saptashloki Durga"},
    {"phase": "pre", "id": "devi-atharva", "label": "Devi Atharvashirsha"},
    {"phase": "pre", "id": "chandika-dhyana", "label": "Chandika Dhyana"},
    {"phase": "pre", "id": "navarna", "label": "Navarna Mantra (108x)"},
    {"phase": "pre", "id": "argala", "label": "Argala Stotram"},
    {"phase": "pre", "id": "keelaka", "label": "Keelaka Stotram"},
    {"phase": "pre", "id": "kavacha", "label": "Devi Kavacham"},
    {"phase": "main", "id": "chapter-1", "label": "Chapter 1 (Prathama Charita)"},
    {"phase": "main", "id": "chapter-2", "label": "Chapter 2"},
    {"phase": "main", "id": "chapter-3", "label": "Chapter 3"},
    {"phase": "main", "id": "chapter-4", "label": "Chapter 4 (Madhyama complete)"},
    {"phase": "main", "id": "chapter-5", "label": "Chapter 5 (Ya Devi Sarva Bhuteshu)"},
    {"phase": "main", "id": "chapter-6", "label": "Chapter 6"},
    {"phase": "main", "id": "chapter-7", "label": "Chapter 7"},
    {"phase": "main", "id": "chapter-8", "label": "Chapter 8"},
    {"phase": "main", "id": "chapter-9", "label": "Chapter 9"},
    {"phase": "main", "id": "chapter-10", "label": "Chapter 10"},
    {"phase": "main", "id": "chapter-11", "label": "Chapter 11 (Narayani Stuti)"},
    {"phase": "main", "id": "chapter-12", "label": "Chapter 12 (Phala Shruti)"},
    {"phase": "main", "id": "chapter-13", "label": "Chapter 13 (Uttama complete)"},
    {"phase": "post", "id": "rahasya-pradhanika", "label": "Pradhanika Rahasya"},
    {"phase": "post", "id": "rahasya-vaikritika", "label": "Vaikritika Rahasya"},
    {"phase": "post", "id": "rahasya-murti", "label": "Murti Rahasya"},
    {"phase": "post", "id": "devi-suktam", "label": "Devi Suktam (Vedic)"},
    {"phase": "post", "id": "kunjika", "label": "Siddha Kunjika Stotram"},
    {"phase": "post", "id": "kshamapana", "label": "Aparadha Kshamapana"},
]


# ============================================================
# MAIN
# ============================================================

def main():
    print("Reading sources...")
    durga700 = read_file("source_durga700.itx")

    print("Building chapters...")
    chapters = [build_chapter(durga700, ch) for ch in CHAPTERS]

    print("Building angas from durga700.itx...")
    angas_durga700 = [build_anga_from_itrans_lines(durga700, a) for a in ANGAS_FROM_DURGA700]

    print("Building Saptashloki Durga...")
    saptashloki = build_saptashloki()
    print("Building Chandika Dhyana...")
    chandika_dhyana = build_chandika_dhyana()
    print("Building Devi Atharvashirsha...")
    devi_atharva = build_devi_atharva()
    print("Building Siddha Kunjika...")
    kunjika_data = build_kunjika()

    print("Building Rahasyas...")
    pradhanika_rahasya = build_rahasya("source_rahasya_pradhanika.txt", {
        "id": "rahasya-pradhanika",
        "name_sa": "प्राधानिक रहस्यम्",
        "name_en": "Pradhanika Rahasya",
        "subtitle": "The Primary Secret - how the One becomes the many forms",
        "phase": "post", "verse_count": 31,
        "rishi": "Narayana", "chhanda": "Anushtup", "devata": "Mahalakshmi",
        "summary": "The first of the three Rahasyas (secret teachings). Reveals how the singular Mahalakshmi assumes the threefold forms - Mahakali (tamasika), Mahalakshmi (rajasika), and Mahasaraswati (sattvika) - and how all the other deities (Brahma, Vishnu, Shiva, Saraswati, Lakshmi, Gauri) emerge from these three. The metaphysical framework of the entire Saptashati."
    })
    vaikritika_rahasya = build_rahasya("source_rahasya_vaikritika.txt", {
        "id": "rahasya-vaikritika",
        "name_sa": "वैकृतिक रहस्यम्",
        "name_en": "Vaikritika Rahasya",
        "subtitle": "The Secret of Transformation - how the formless takes form",
        "phase": "post", "verse_count": 39,
        "rishi": "Narayana", "chhanda": "Anushtup", "devata": "Tridevi",
        "summary": "The second Rahasya. Describes the threefold manifestation of the Goddess in iconographic detail - the ten-faced Mahakali, the eighteen-armed Mahalakshmi (Mahishasura Mardini), and the eight-armed Mahasaraswati (slayer of Shumbha-Nishumbha). Specifies how each form is to be visualized and worshipped - the basis for all Devi iconography."
    })
    murti_rahasya = build_rahasya("source_rahasya_murti.txt", {
        "id": "rahasya-murti",
        "name_sa": "मूर्ति रहस्यम्",
        "name_en": "Murti Rahasya",
        "subtitle": "The Secret of the Forms - the seven incarnational forms of Devi",
        "phase": "post", "verse_count": 25,
        "rishi": "Narayana", "chhanda": "Anushtup", "devata": "Devi (seven forms)",
        "summary": "The third Rahasya. Describes seven specific incarnational forms (murtis) of Devi: Nanda Bhagavati, Raktadantika, Shakambhari (Shataakshi), Bhima, Bhramari, and others. Each form is described with iconographic precision and the specific kind of devotee they protect. Closing the trilogy with the cosmic-personal bridge - the Mother who comes to specific aid."
    })

    # Combine all angas in order
    all_angas = [
        saptashloki,           # pre
        devi_atharva,          # pre
        chandika_dhyana,       # pre
        angas_durga700[0],     # argala (pre)
        angas_durga700[1],     # keelaka (pre)
        angas_durga700[2],     # kavacha (pre)
        pradhanika_rahasya,    # post
        vaikritika_rahasya,    # post
        murti_rahasya,         # post
        angas_durga700[4],     # devi-suktam (post)
        kunjika_data,          # post
        angas_durga700[3],     # kshamapana (post)
    ]

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
        "navadurga": NAVADURGA,
        "saptamatrika": SAPTAMATRIKA,
        "hymns": HYMNS,
        "navratri": NAVRATRI,
        "eighteenWeapons": EIGHTEEN_WEAPONS,
        "beginnerPath": BEGINNER_PATH,
        "chandiHoma": CHANDI_HOMA,
        "paathOrder": PAATH_ORDER,
    }

    print("Writing data.js...")
    js = "window.DURGA_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    with open(os.path.join(ROOT, "data.js"), "w", encoding="utf-8") as f:
        f.write(js)

    print(f"Done. data.js size: {os.path.getsize(os.path.join(ROOT, 'data.js'))} bytes")
    print(f"Chapters: {len(chapters)}")
    print(f"Angas: {len(all_angas)}")
    print(f"Charitas: {len(CHARITAS)}")
    print(f"Navadurga: {len(NAVADURGA)}")
    print(f"Saptamatrika: {len(SAPTAMATRIKA)}")
    print(f"Hymns: {len(HYMNS)}")
    print(f"Paath items: {len(PAATH_ORDER)}")


if __name__ == "__main__":
    main()
