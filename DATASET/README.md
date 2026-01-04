# DATASET - Regex Pattern Documentation

Folder ini berisi dokumentasi regex pattern untuk setiap kategori deteksi moderation.

## Struktur File

Setiap file `.txt` berisi:
- **REGEX_PATTERN**: Pattern regex untuk kategori tersebut
- **WEIGHT**: Bobot scoring (0.0 - 2.0)
- **DESCRIPTION**: Deskripsi kategori
- **EXAMPLES**: Contoh kata/frasa yang terdeteksi

## Kategori

### Sexual Content
- `explicit_acts.txt` - Tindakan eksplisit/seksual
- `genitals.txt` - Organ genital
- `nudity.txt` - Konten telanjang/nude
- `suggestive_content.txt` - Konten suggestif
- `adult_content.txt` - Konten dewasa
- `request_media.txt` - Permintaan foto/video eksplisit
- `invitation.txt` - Ajakan/undangan seksual
- `escort_terms.txt` - Istilah escort/jasa seksual

### Modus (Grooming/Transaction)
- `ask_contact.txt` - Permintaan kontak/nomor
- `move_off_platform.txt` - Ajakan pindah platform
- `platform_standalone.txt` - Mention platform komunikasi
- `obfuscated_platform.txt` - Platform yang di-obfuscate
- `meetup.txt` - Ajakan ketemu/meetup
- `hotel_room.txt` - Mention hotel/kamar
- `rates_money.txt` - Tarif/rate/uang/jasa
- `coercion.txt` - Manipulasi/coercion
- `age_probe.txt` - Pertanyaan umur/usia

### Harassment
- `insults.txt` - Kata kasar/insult
- `threats.txt` - Ancaman
- `sexual_harass_combo.txt` - Kombinasi konten seksual + target

### Scam
- `phishing.txt` - Phishing (permintaan OTP/PIN)
- `fraud_keywords.txt` - Kata kunci fraud/scam
- `suspicious_links.txt` - Link mencurigakan
- `impersonation.txt` - Impersonation (pura-pura CS/admin)

## Penggunaan

Pattern-pattern ini digunakan oleh `rules.py` untuk deteksi moderation. Setiap pattern memiliki weight yang digunakan untuk menghitung score akhir (0-100).

## Catatan

- Semua pattern menggunakan flag `re.I` (case-insensitive)
- Pattern menggunakan word boundaries `\b` untuk match exact words
- Beberapa pattern menggunakan `+` untuk handle repeated characters (typo variations)
- Pattern menggunakan `[3e]`, `[o0]` untuk handle leet speak variations

## Context Checking System

Sistem ini juga menggunakan context checker (semi-LLM rule-based) untuk meningkatkan akurasi:

- **context_patterns.txt** - Pattern context-aware (melihat konteks sebelum/sesudah)
- **context_rules.txt** - Dokumentasi context rules dasar
- **context_rules_advanced.txt** - Dokumentasi context rules advanced (19 rules)

Context checker menggunakan if-else logic untuk:
- Mengecek konteks sebelum pattern (context_before)
- Mengecek konteks sesudah pattern (context_after)
- Exclude jika ada konteks tertentu (exclude_before, exclude_after)
- Adjust weight berdasarkan konteks
- Handle negation (gak/enggak/tidak)

