# context_checker.py
# Semi-LLM rule-based context checking system
# Checks context before/after detected patterns to improve accuracy

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class ContextRule:
    """Rule untuk context checking"""
    trigger_pattern: str  # Pattern yang trigger context check
    context_before: Optional[List[str]] = None  # Pattern yang harus ada SEBELUM trigger
    context_after: Optional[List[str]] = None   # Pattern yang harus ada SESUDAH trigger
    exclude_before: Optional[List[str]] = None  # Pattern yang TIDAK boleh ada sebelum
    exclude_after: Optional[List[str]] = None   # Pattern yang TIDAK boleh ada sesudah
    weight_adjust: float = 0.0  # Adjust weight jika context match
    should_flag: bool = True  # Apakah harus flag jika context match

class ContextChecker:
    """Semi-LLM context checker menggunakan rule-based logic"""
    
    def __init__(self):
        self.rules = self._build_context_rules()
    
    def _build_context_rules(self) -> List[ContextRule]:
        """Build context checking rules"""
        return [
            # NUDE - jika ada "art", "photography", "drawing" -> mungkin false positive
            ContextRule(
                trigger_pattern=r"\b(nude|bugil|telanjang)\b",
                exclude_after=[r"\b(art|photography|drawing|painting|sculpture|museum)\b"],
                weight_adjust=-0.5,  # Reduce weight jika ada context exclude
                should_flag=False
            ),
            # NUDE - jika ada "kirim", "send", "share", "minta" -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(nude|bugil|telanjang)\b",
                context_before=[r"\b(kirim|send|share|minta|kasih|tolong|bantu)\b"],
                weight_adjust=0.3,  # Increase weight
                should_flag=True
            ),
            # SEX - jika ada "education", "health" -> false positive
            ContextRule(
                trigger_pattern=r"\b(sex|seks|intercourse)\b",
                exclude_after=[r"\b(education|edukasi|pelajaran|health|kesehatan|therapy|terapi|medical|medis)\b"],
                weight_adjust=-1.0,  # Reduce more aggressively
                should_flag=False
            ),
            # SEX - jika ada "mau", "pengen", "ingin" -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(sex|seks|ngentot)\b",
                context_before=[r"\b(mau|pengen|ingin|minta)\b"],
                weight_adjust=0.4,
                should_flag=True
            ),
            # ADULT - jika ada "content", "only", "18+" -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(dewasa|adult)\b",
                context_after=[r"\b(content|only|18\+|18plus)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # ADULT - jika ada "education" -> false positive
            ContextRule(
                trigger_pattern=r"\b(dewasa|adult)\b",
                exclude_after=[r"\b(education|edukasi|pelajaran)\b"],
                weight_adjust=-0.4,
                should_flag=False
            ),
            # PLATFORM - jika ada "pindah", "lanjut" -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(wa|telegram|line|whatsapp)\b",
                context_before=[r"\b(pindah|lanjut|move)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # MONEY - jika ada "bayar", "transfer", "kirim" sebelum -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(juta|rb|ribu|rupiah|uang|duit)\b",
                context_before=[r"\b(bayar|transfer|kirim|kasih)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # CONTACT - jika ada "minta", "boleh", "kasih" sebelum -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(nomor|wa|kontak|telegram|line)\b",
                context_before=[r"\b(minta|boleh|kasih|drop|ada)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # HOTEL/ROOM - jika ada "ketemu", "meet" sebelum -> HARUS flag
            ContextRule(
                trigger_pattern=r"\b(hotel|kamar|kosan|apartemen)\b",
                context_before=[r"\b(ketemu|meet|ngopi|jalan)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # INTERCOURSE - exclude jika ada "sexual" sebelum (sexual intercourse = medical term)
            ContextRule(
                trigger_pattern=r"\b(intercourse)\b",
                context_before=[r"\b(sexual)\b"],
                exclude_before=[r"\b(kirim|send|mau|pengen)\b"],  # Tapi exclude jika ada action words
                weight_adjust=-0.3,
                should_flag=False
            ),
            # PORNO/BOKEP - jika ada "watch", "tonton", "nonton" -> boost
            ContextRule(
                trigger_pattern=r"\b(porn|bokep|hentai)\b",
                context_before=[r"\b(watch|tonton|nonton|lihat|tayang)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # MASTURB - exclude jika ada "education" atau "health"
            ContextRule(
                trigger_pattern=r"\b(masturb)\b",
                exclude_after=[r"\b(education|edukasi|health|kesehatan)\b"],
                weight_adjust=-0.8,
                should_flag=False
            ),
            # TRANSFER/KIRIM + UANG + BEFORE "foto", "video", "nude" -> boost (transactional)
            ContextRule(
                trigger_pattern=r"\b(transfer|kirim|bayar)\b",
                context_before=[r"\b(foto|video|nude|bugil|telanjang)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # KONTOL/MEMEK + KAMU/LU/ELO -> boost (harassment)
            ContextRule(
                trigger_pattern=r"\b(kontol|memek|tetek|bugil|nude)\b",
                context_after=[r"\b(kamu|lu|elo|kau|anda)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # BOOKING/OPEN BO + BEFORE "per jam", "tarif", "rate" -> boost (transactional)
            ContextRule(
                trigger_pattern=r"\b(booking|open\s*bo|avail)\b",
                context_before=[r"\b(per\s*jam|tarif|rate|bayar)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # PER JAM/PER MALAM + AFTER angka/juta/rb -> boost (transactional)
            ContextRule(
                trigger_pattern=r"\b(per\s*jam|per\s*malam|perjam|permalam)\b",
                context_after=[r"\b(\d+|juta|rb|ribu|jt)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # KETEMU/MEET + AFTER "hotel", "kamar", "apartemen" -> boost
            ContextRule(
                trigger_pattern=r"\b(ketemu|meet|ngopi|jalan)\b",
                context_after=[r"\b(hotel|kamar|kosan|apartemen)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # OTP/PIN + BEFORE/SESUDAH "kirim", "send", "share" -> boost (phishing)
            ContextRule(
                trigger_pattern=r"\b(otp|pin|kode\s*verifikasi)\b",
                context_before=[r"\b(kirim|send|share|kasih|minta)\b"],
                weight_adjust=0.4,
                should_flag=True
            ),
            ContextRule(
                trigger_pattern=r"\b(otp|pin)\b",
                context_after=[r"\b(kirim|send|share|kasih|minta)\b"],
                weight_adjust=0.4,
                should_flag=True
            ),
            # HADIAH/MENANG + BEFORE/SESUDAH "transfer", "bayar", "kirim uang" -> boost (scam)
            ContextRule(
                trigger_pattern=r"\b(hadiah|menang|undian)\b",
                context_after=[r"\b(transfer|bayar|kirim\s*uang|transfer\s*duit)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # CS/ADMIN + BEFORE/SESUDAH "verifikasi", "suspend", "blokir" -> boost (impersonation)
            ContextRule(
                trigger_pattern=r"\b(cs|customer\s*service|admin|official)\b",
                context_after=[r"\b(verifikasi|akun|suspend|blokir)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # GAK/ENGGAK/TAK + SEX/NGENTOT -> exclude (negation)
            ContextRule(
                trigger_pattern=r"\b(sex|seks|ngentot|entot|ml|make\s*love)\b",
                context_before=[r"\b(gak|enggak|tak|tidak|no|jangan|nggak|ga)\b"],
                weight_adjust=-1.0,  # Strong exclusion
                should_flag=False
            ),
            # GAK/ENGGAK/TAK + KIRIM/SEND NUDE -> exclude (negation)
            ContextRule(
                trigger_pattern=r"\b(nude|bugil|telanjang)\b",
                context_before=[r"\b(gak|enggak|tak|tidak|no|jangan)\s*(kirim|send|minta|kasih)\b"],
                weight_adjust=-0.5,
                should_flag=False
            ),
            # KIRIM/SEND + FOTO/VIDEO + BEFORE "nude", "bugil" -> boost
            ContextRule(
                trigger_pattern=r"\b(foto|video|gambar|pic)\b",
                context_before=[r"\b(kirim|send|share|minta|kasih)\b"],
                context_after=[r"\b(nude|bugil|telanjang)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # PER JAM/PER MALAM + BEFORE angka/juta -> boost
            ContextRule(
                trigger_pattern=r"\b(per\s*jam|per\s*malam|perjam|permalam)\b",
                context_before=[r"\b(\d+|juta|rb|ribu|jt)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # HOTEL/KAMAR + AFTER "ketemu", "meet" -> boost
            ContextRule(
                trigger_pattern=r"\b(hotel|kamar|kosan|apartemen)\b",
                context_after=[r"\b(ketemu|meet|ngopi|jalan)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # TRANSFER/BAYAR + AFTER "foto", "video", "nude" -> boost
            ContextRule(
                trigger_pattern=r"\b(transfer|bayar|kirim|kasih)\b",
                context_after=[r"\b(foto|video|nude|bugil|telanjang)\b"],
                weight_adjust=0.3,
                should_flag=True
            ),
            # PINDAH/LANJUT + AFTER platform -> boost
            ContextRule(
                trigger_pattern=r"\b(pindah|lanjut|move)\b",
                context_after=[r"\b(wa|telegram|line|whatsapp|ig|instagram)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # MINTa/Boleh + AFTER "nomor", "wa", "kontak" -> boost
            ContextRule(
                trigger_pattern=r"\b(minta|boleh|kasih|drop)\b",
                context_after=[r"\b(nomor|wa|kontak|telegram|line|ig)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # KETEMU/MEET + AFTER "yuk", "ayo" -> boost
            ContextRule(
                trigger_pattern=r"\b(ketemu|meet|ngopi|jalan)\b",
                context_after=[r"\b(yuk|ayo|bareng|sama)\b"],
                weight_adjust=0.15,
                should_flag=True
            ),
            # BAYAR/TRANSFER + AFTER "dulu", "sekarang", "nanti" -> boost
            ContextRule(
                trigger_pattern=r"\b(bayar|transfer|kirim|kasih)\b",
                context_after=[r"\b(dulu|sekarang|nanti|besok|hari\s*ini)\b"],
                weight_adjust=0.15,
                should_flag=True
            ),
            # SEX/NGENTOT + AFTER "bareng", "sama", "dengan" -> boost
            ContextRule(
                trigger_pattern=r"\b(sex|seks|ngentot|entot|ml)\b",
                context_after=[r"\b(bareng|sama|dengan|kamu|lu|elo)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
            # NUDE/BUGIL + AFTER "dong", "ya", "sini" -> boost (request)
            ContextRule(
                trigger_pattern=r"\b(nude|bugil|telanjang)\b",
                context_after=[r"\b(dong|ya|sini|nih|aja)\b"],
                weight_adjust=0.15,
                should_flag=True
            ),
            # KALAU/JIKA + BEFORE "mau", "pengen" + AFTER sexual/money -> boost (conditional)
            ContextRule(
                trigger_pattern=r"\b(mau|pengen|ingin)\b",
                context_before=[r"\b(kalau|kalo|jika|if)\b"],
                context_after=[r"\b(sex|seks|ngentot|foto|video|nude|bayar|transfer|uang|juta)\b"],
                weight_adjust=0.25,
                should_flag=True
            ),
            # TOLONG/BANTU + BEFORE "kirim", "send" + AFTER "nude", "foto" -> boost
            ContextRule(
                trigger_pattern=r"\b(kirim|send|share|minta|kasih)\b",
                context_before=[r"\b(tolong|bantu|please)\b"],
                context_after=[r"\b(nude|bugil|telanjang|foto|video)\b"],
                weight_adjust=0.2,
                should_flag=True
            ),
        ]
    
    def check_context(self, text: str, normalized_text: str, matched_text: str, position: Tuple[int, int]) -> Dict:
        """
        Check context untuk matched pattern
        
        Args:
            text: Original text
            normalized_text: Normalized text
            matched_pattern: Pattern yang match
            position: (start, end) position dari match
        
        Returns:
            Dict dengan:
            - valid: bool (apakah context valid untuk flagging)
            - weight_adjust: float (adjustment untuk weight)
            - reason: str (alasan)
        """
        start, end = position
        
        # Ambil context sebelum dan sesudah (dalam radius tertentu)
        context_window = 50  # karakter sebelum/sesudah
        text_start = max(0, start - context_window)
        text_end = min(len(normalized_text), end + context_window)
        
        context_before = normalized_text[text_start:start].lower()
        context_after = normalized_text[end:text_end].lower()
        full_context = normalized_text[text_start:text_end].lower()
        
        # Check setiap rule
        for rule in self.rules:
            # Check jika trigger pattern match dengan matched_text
            if re.search(rule.trigger_pattern, matched_text, re.I):
                # Check context_before
                if rule.context_before:
                    if not any(re.search(pattern, context_before, re.I) for pattern in rule.context_before):
                        continue  # Context before tidak match, skip rule ini
                
                # Check context_after
                if rule.context_after:
                    if not any(re.search(pattern, context_after, re.I) for pattern in rule.context_after):
                        continue  # Context after tidak match, skip rule ini
                
                # Check exclude_before
                if rule.exclude_before:
                    if any(re.search(pattern, context_before, re.I) for pattern in rule.exclude_before):
                        return {
                            "valid": False,
                            "weight_adjust": rule.weight_adjust,
                            "reason": f"Exclude context before found"
                        }
                
                # Check exclude_after
                if rule.exclude_after:
                    if any(re.search(pattern, context_after, re.I) for pattern in rule.exclude_after):
                        return {
                            "valid": False,
                            "weight_adjust": rule.weight_adjust,
                            "reason": f"Exclude context after found"
                        }
                
                # Semua context check pass
                return {
                    "valid": rule.should_flag,
                    "weight_adjust": rule.weight_adjust,
                    "reason": "Context match"
                }
        
        # Default: no context rule match, allow flagging
        return {
            "valid": True,
            "weight_adjust": 0.0,
            "reason": "No context rule match"
        }

