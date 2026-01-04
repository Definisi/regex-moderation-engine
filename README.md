# Regex Moderation Engine

Regex-only chat moderation scorer dengan semi-LLM context checking system untuk deteksi konten tidak pantas dalam bahasa Indonesia.

## Features

- **Multi-label Detection**: Sexual, Modus (grooming/transactional), Harassment, Scam
- **Context-Aware**: Semi-LLM rule-based context checking untuk mengurangi false positives
- **Obfuscation Handling**: Deteksi kata-kata yang di-obfuscate (s3x, s e x, T.e.l.e, dll)
- **Pure Regex**: Tidak ada dependency ML, ringan dan cepat
- **Comprehensive Rules**: 27 pattern rules + 36 context rules = 63 total rules
- **500+ Test Cases**: Extensive test coverage

## Quick Start

```python
from scorer import RegexModerationScorer

scorer = RegexModerationScorer()
result = scorer.score("kirim nude dong")

print(result["labels"]["sexual"]["score"])  # Score 0-100
print(result["labels"]["sexual"]["flag"])   # True/False
print(result["labels"]["sexual"]["hits"])   # Matched rules
```

## Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/regex-moderation-engine.git
cd regex-moderation-engine

# No dependencies required! Pure Python stdlib
python index.py  # Run test cases
```

## Architecture

```
normalize.py      - Text normalization (leet speak, obfuscation)
rules.py          - Pattern rules (27 rules)
scorer.py         - Scoring engine
context_checker.py - Semi-LLM context checking (36 rules)
index.py          - Main entry point & test cases
DATASET/          - Pattern documentation
```

## Detection Categories

- **Sexual**: Explicit acts, genitals, nudity, suggestive content, adult content
- **Modus**: Platform requests, contact requests, meetup, hotel/room, rates/money
- **Harassment**: Insults, threats, sexual harassment
- **Scam**: Phishing, fraud keywords, suspicious links, impersonation

## Statistics

- Pattern Rules: 27 (11 sexual, 9 modus, 3 harassment, 4 scam)
- Context Rules: 36 (23 boost, 13 exclude)
- Test Cases: 500+
- Thresholds: sexual=60, modus=60, harassment=65, scam=65

## Example Output

```
TEXT: kirim nude dong
NORM: kirim nude dong
- sexual     score= 76 flag=True hits=['nudity', 'request_media', 'context_sexual_request']
- modus      score=  0 flag=False hits=[]
- harassment score=  0 flag=False hits=[]
- scam       score=  0 flag=False hits=[]
overall risk: 76
```

## Dataset

Pattern rules documented in `DATASET/` folder:
- Individual `.txt` files for each pattern category
- Context rules documentation
- Comprehensive summary

## Context Checking

System uses rule-based context checking to improve accuracy:

- **Exclude Rules**: Reduce false positives (e.g., "nude art", "sex education")
- **Boost Rules**: Enhance true positives (e.g., "kirim nude", "mau sex")

## Contributing

1. Add new patterns in `rules.py`
2. Add context rules in `context_checker.py`
3. Add test cases in `index.py`
4. Update documentation in `DATASET/`

## License

MIT License

## Author

Definisi