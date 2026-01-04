# rules.py
# Pattern rules for moderation scoring

import re
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PatternRule:
    name: str
    regex: re.Pattern
    weight: float

def build_sexual_rules() -> List[PatternRule]:
    return [
        PatternRule("explicit_acts",
            re.compile(r"\b(s[3e]x+|s[3e]ks+|ngent[o0]t+|ewe|ewean|ent[o0]t+|coli|colmek|masturb(asi)?|ngewe|hentai|porn+|bokep+|xnxx|xvideos|intercourse)\b", re.I),
            2.0
        ),
        PatternRule("genitals",
            re.compile(r"\b(kontol+|memek+|pepek+|titit+|penis|vagina|pussy|dick|cock|boobs+|tetek+|tete+|payudara|g[-\s]*spot|gspot)\b", re.I),
            1.7
        ),
        PatternRule("invitation",
            re.compile(r"\b(ml|make\s*love|sange|horny|sangean|main\s*yuk|ayo\s*(sex|seks)|ngamar|ons|hookup)\b", re.I),
            1.4
        ),
        PatternRule("escort_terms",
            re.compile(r"\b(open\s*bo|open\s*booking|booking|avail|short\s*time|long\s*time|st|lt|pijat\s*plusplus|plus\s*plus)\b", re.I),
            1.6
        ),
        PatternRule("nudity",
            re.compile(r"\b(telanjang|bugil+|nude+|naked)\b", re.I),
            1.2
        ),
        PatternRule("adult_content",
            re.compile(r"\b(dewasa|adult)\b", re.I),
            1.0
        ),
        PatternRule("suggestive_content",
            re.compile(r"\b(dirty|hot|seksi|sexy|mesum|nakal|kotor)\b", re.I),
            0.9
        ),
        PatternRule("request_media",
            re.compile(r"\b(kirim(in)?|send|share|minta|kasih)\s*(foto|video|gambar|pic)?\s*(bugil|nude|telanjang)\b", re.I),
            1.5
        ),
        PatternRule("context_sexual_request",
            re.compile(r"\b(kirim|send|share|minta|kasih|tolong|bantu)\s*(.+?)?\s*(nude|bugil|telanjang|foto|video|gambar)\b", re.I),
            1.3
        ),
        PatternRule("context_sexual_activity",
            re.compile(r"\b(mau|pengen|ingin|minta)\s*(.+?)?\s*(sex|seks|ngentot|entot|ml|make\s*love)\b", re.I),
            1.4
        ),
        PatternRule("context_transaction",
            re.compile(r"\b(bayar|transfer|kirim|kasih)\s*(.+?)?\s*(uang|duit|money|rp|rupiah|juta|rb|ribu|jt)\b", re.I),
            1.2
        ),
    ]

def build_modus_rules() -> List[PatternRule]:
    return [
        PatternRule("move_off_platform",
            re.compile(r"\b(pindah|lanjut)\s*(wa|whatsapp|tele|telegram|line|ig|instagram|dm|vc|video\s*call|call|gmeet)\b", re.I),
            1.2
        ),
        PatternRule("platform_standalone",
            re.compile(r"\b(telegram|tele|line|gmeet|whatsapp|wa)\b", re.I),
            0.8
        ),
        PatternRule("obfuscated_platform",
            re.compile(r"\b(te\.?le(\.?gram)?|li\.?ne|wa\.?ha?ts?app?|w\.?a\.?|t\.?e\.?l\.?e\.?g\.?r\.?a\.?m|i\.?g|i\.?n\.?s\.?t\.?a\.?g\.?r\.?a\.?m)\b", re.I),
            0.7
        ),
        PatternRule("ask_contact",
            re.compile(r"\b(minta|boleh|kasih|drop|ada)\s*(nomor|no\.?|wa|kontak|telegram|tele|line|ig)\b|\b(kontak)\s*(lain|luar|lainnya)?\b", re.I),
            1.1
        ),
        PatternRule("meetup",
            re.compile(r"\b(ketemu|meet|ngopi|jalan|hangout|main)\s*(yuk|ayo)?\b", re.I),
            0.9
        ),
        PatternRule("hotel_room",
            re.compile(r"\b(hotel|kamar|kosan|apart|apartemen|nginep)\b", re.I),
            0.9
        ),
        PatternRule("rates_money",
            re.compile(r"\b(per\s*jam(nya)?|perjam(nya)?|per\s*malam(nya)?|permalam(nya)?|tarif|rate|bayar|fee|jasa|transfer|tf|gopay|dana|ovo|rekening)\b", re.I),
            1.3
        ),
        PatternRule("coercion",
            re.compile(r"\b(asal\s*kamu|kalau\s*kamu\s*mau|tenang\s*aja|gak\s*usah\s*takut|percaya\s*sama\s*aku|rahasia|jangan\s*bilang\s*siapa|bisa\s*diatur|diatur|pengen)\b", re.I),
            0.9
        ),
        PatternRule("age_probe",
            re.compile(r"\b(umur|usia)\s*\d{1,2}\b|\b(kelas|smp|smk|sma)\b", re.I),
            0.8
        ),
    ]

def build_harassment_rules() -> List[PatternRule]:
    return [
        PatternRule("insults",
            re.compile(r"\b(anjing|bangsat|kontol|memek|bego|tolol|goblok|brengsek|ngentod|asu|kampret)\b", re.I),
            1.5
        ),
        PatternRule("threats",
            re.compile(r"\b(gua\s*bunuh|tak\s*bunuh|mati\s*aja|hajar|gebuk|bacok|tembak|laporin|sebar(in)?)\b", re.I),
            1.4
        ),
        PatternRule("sexual_harass_combo",
            re.compile(r"\b(kontol|memek|tetek|bugil|nude)\b.*\b(kamu|lu|elo)\b|\b(kamu|lu|elo)\b.*\b(kontol|memek|tetek|bugil|nude)\b", re.I),
            1.2
        ),
    ]

def build_scam_rules() -> List[PatternRule]:
    return [
        PatternRule("phishing",
            re.compile(r"\b(otp|kode\s*verifikasi|verification\s*code|pin)\b.*\b(kirim|send|share|kasih)\b|\b(kirim|send|share|kasih)\b.*\b(otp|pin)\b", re.I),
            2.0
        ),
        PatternRule("fraud_keywords",
            re.compile(r"\b(hadiah|menang|undian|saldo|top\s*up|invest|deposit|withdraw|wd|cuan|profit)\b", re.I),
            1.1
        ),
        PatternRule("suspicious_links",
            re.compile(r"\b(https?://|www\.)\S+\b", re.I),
            0.7
        ),
        PatternRule("impersonation",
            re.compile(r"\b(cs|customer\s*service|admin|official)\b.*\b(verifikasi|akun|suspend|blokir)\b", re.I),
            1.2
        ),
    ]

