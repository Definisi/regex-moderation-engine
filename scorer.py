# scorer.py
# Core scoring engine for regex moderation

from typing import Dict, List
from normalize import normalize_text
from rules import PatternRule, build_sexual_rules, build_modus_rules, build_harassment_rules, build_scam_rules
from context_checker import ContextChecker

def clamp(n: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, n))

def logistic_score(total_weight: float, k: float = 1.25) -> int:
    """Convert accumulated weights into 0..100 score using a squashing curve."""
    if total_weight <= 0:
        return 0
    score = 100.0 * (total_weight / (total_weight + k))
    return int(round(clamp(score)))

class RegexModerationScorer:
    def __init__(self) -> None:
        self.labels: Dict[str, Dict] = {
            "sexual": {
                "threshold": 60,
                "rules": build_sexual_rules(),
            },
            "modus": {
                "threshold": 60,
                "rules": build_modus_rules(),
            },
            "harassment": {
                "threshold": 65,
                "rules": build_harassment_rules(),
            },
            "scam": {
                "threshold": 65,
                "rules": build_scam_rules(),
            },
        }
        self.context_checker = ContextChecker()

    def score(self, text: str) -> Dict:
        raw = text or ""
        t = normalize_text(raw)

        result: Dict[str, Dict] = {}
        for label, cfg in self.labels.items():
            rules: List[PatternRule] = cfg["rules"]
            threshold: int = cfg["threshold"]

            total_w = 0.0
            hits: List[Dict] = []

            for rule in rules:
                m = list(rule.regex.finditer(t))
                if not m:
                    continue

                count = len(m)
                base_contrib = rule.weight * (1.0 + min(0.5, 0.15 * (count - 1)))
                
                # Context checking untuk setiap match
                context_adjusted_contrib = 0.0
                valid_matches = 0
                for mm in m:
                    matched_text = t[mm.start():mm.end()]
                    context_result = self.context_checker.check_context(
                        raw, t, matched_text, (mm.start(), mm.end())
                    )
                    
                    if context_result["valid"]:
                        match_contrib = rule.weight * (1.0 + context_result["weight_adjust"])
                        context_adjusted_contrib += match_contrib
                        valid_matches += 1
                    else:
                        # Context exclude found, reduce weight significantly atau skip
                        match_contrib = rule.weight * (1.0 + context_result["weight_adjust"])
                        # Jika weight_adjust sangat negatif, skip match ini
                        if context_result["weight_adjust"] <= -0.8:
                            continue  # Skip match ini completely
                        context_adjusted_contrib += max(0, match_contrib)  # Jangan negatif
                
                # Use context-adjusted contribution if we have valid matches
                if valid_matches > 0:
                    contrib = context_adjusted_contrib
                else:
                    contrib = base_contrib
                
                total_w += contrib

                spans = [(mm.start(), mm.end()) for mm in m[:3]]
                hits.append({
                    "rule": rule.name,
                    "count": count,
                    "valid_matches": valid_matches,
                    "weight": rule.weight,
                    "contrib": round(contrib, 3),
                    "spans": spans,
                })

            score = logistic_score(total_w, k=1.25)
            flagged = score >= threshold

            result[label] = {
                "score": score,
                "threshold": threshold,
                "flag": flagged,
                "weight_sum": round(total_w, 3),
                "hits": hits,
            }

        risk = max(v["score"] for v in result.values()) if result else 0
        result["overall"] = {"risk_score": risk}

        return {
            "input": raw,
            "normalized": t,
            "labels": result,
        }

