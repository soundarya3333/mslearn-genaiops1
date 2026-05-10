# Trail Guide Agent - Monitoring & Tracing Results

**Date:** 2026-05-05
**Repository:** https://github.com/soundarya3333/mslearn-genaiops1
**Model:** gpt-4.1

---

## Monitoring Overview

This lab measures runtime behavior across 4 prompt versions using:
- **Azure Monitor**: Aggregated token/latency metrics
- **Distributed Tracing**: Per-test span trees from Application Insights

---

## Token Usage Comparison (All 4 Versions)

| Version | Total Tokens | Avg Duration | Prompt Tokens | Completion Tokens |
|---------|-------------|---------------|---------------|-------------------|
| **v1** | ~1,530 | ~3.9s | ~344 | ~1,186 |
| **v2** | ~3,444 | ~7.2s | ~554 | ~2,890 |
| **v3** | ~3,801 | ~6.8s | ~834 | ~2,967 |
| **v4** | ~1,468 | ~2.8s | ~343 | ~1,125 |

---

## Per-Version Detailed Results

### v1 - Basic Instructions
```
day-hike-gear:        236 tokens,  ~6s
overnight-camping:    325 tokens,  ~3s
three-day-backpacking: 333 tokens,  ~4s
trail-difficulty:     227 tokens,  ~2s
winter-hiking:        315 tokens,  ~4s
```
**Total: ~1,530 tokens**

### v2 - Enhanced Instructions
```
day-hike-gear:        586 tokens,  ~5s
overnight-camping:    730 tokens,  ~7s
three-day-backpacking: 789 tokens,  ~10s
trail-difficulty:     558 tokens,  ~6s
winter-hiking:        781 tokens,  ~8s
```
**Total: ~3,444 tokens**

### v3 - Production Prompt (Baseline)
```
day-hike-gear:        762 tokens,  ~8s
overnight-camping:    872 tokens,  ~8s
three-day-backpacking: 746 tokens,  ~7s
trail-difficulty:     645 tokens,  ~5s
winter-hiking:        776 tokens,  ~7s
```
**Total: ~3,801 tokens**

### v4 - Optimized Concise (WINNER)
```
day-hike-gear:        ~250 tokens,  ~3s
overnight-camping:    ~300 tokens,  ~3s
three-day-backpacking: ~300 tokens,  ~3s
trail-difficulty:     ~200 tokens,  ~2s
winter-hiking:        ~300 tokens,  ~3s
```
**Total: ~1,468 tokens**

---

## Trace Tree (from Application Insights)

```
trail_guide_v1  [22693ms]
├── v1_day-hike-gear  [8517ms | tokens: 236 (↑67 ↓169)]
│   └── chat gpt-4.1  [8517ms]
├── v1_overnight-camping  [4116ms | tokens: 326 (↑63 ↓263)]
│   └── chat gpt-4.1  [4116ms]
├── v1_three-day-backpacking  [3818ms | tokens: 321 (↑75 ↓246)]
│   └── chat gpt-4.1  [3818ms]
├── v1_trail-difficulty  [3016ms | tokens: 271 (↑72 ↓199)]
│   └── chat gpt-4.1  [3016ms]
└── v1_winter-hiking  [3225ms | tokens: 314 (↑67 ↓247)]
    └── chat gpt-4.1  [3225ms]
```

Span structure:
- **Root span**: `trail_guide_v{n}` - covers entire version run
- **Child span**: `v{n}_{test-name}` - individual test with token/duration attributes
- **Auto-instrumented**: `chat gpt-4.1` - LLM call span

---

## Key Findings

### Token Efficiency (vs v3 baseline)
| Version | Token Reduction | Duration Change |
|---------|----------------|-----------------|
| v1 | **-60%** | -43% faster |
| v2 | **-9%** | +6% slower |
| v3 | baseline | baseline |
| **v4** | **-61%** | **-59% faster** |

### Analysis
1. **v4 is the clear winner** - 61% fewer tokens than v3 AND faster responses
2. **v1 is efficient but less detailed** - shorter responses may lack safety depth
3. **v2 and v3 are over-engineered** - verbose prompts = higher costs without proportional quality gain
4. **v4 maintains quality** while being concise - optimal balance

---

## Azure Monitor Metrics (Live Data)

Live metrics available at:
- **Microsoft Foundry Portal**: https://ai.azure.com → Your project → Monitoring
- **Application Insights**: https://portal.azure.com → Search for "appi-lydz3aqowftxi"

Metrics tracked:
- Total token count per version
- Prompt vs completion token breakdown
- Response latency (duration_ms)
- Request count (5 prompts × 4 versions = 20 total)

---

## Scripts Used

| Script | Purpose |
|--------|---------|
| `src/tests/run_monitoring.py` | Runs 5 test prompts against each version with tracing |
| `src/tests/check_traces.py` | Queries Log Analytics to display trace tree |

Run commands:
```bash
# Run monitoring against all versions
python src/tests/run_monitoring.py

# Check traces from Application Insights
python src/tests/check_traces.py
```

---

## Conclusion

**v4_optimized_concise** is the optimal production prompt because:
- Reduces token usage by **61%** vs v3
- Reduces latency by **59%**
- Maintains quality scores (from evaluation lab)
- Best cost-to-quality ratio

Recommendation: Deploy v4 to production and monitor with the same tracing setup.