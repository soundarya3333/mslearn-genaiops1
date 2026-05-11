# Trail Guide Agent - Monitoring & Tracing Results (Lab 06)

**Date:** 2026-05-05
**Environment:** fresh (rg-fresh)
**Repository:** https://github.com/soundarya3333/mslearn-genaiops1
**Model:** gpt-4.1
**Region:** Korea Central

---

## Overview

This lab measures runtime behavior across 4 prompt versions using:
- **Application Insights**: Cloud telemetry collection
- **Log Analytics**: Trace tree queries
- **Distributed Tracing**: Per-test span trees with token/latency attributes

---

## Token Usage Comparison (All 4 Versions, 5 Test Prompts Each)

| Version | Total Tokens | Prompt Tokens | Completion Tokens | vs v3 |
|---------|-------------|---------------|-------------------|-------|
| **v1** | 1,330 | 344 | 986 | -62% |
| **v2** | 3,290 | 554 | 2,736 | -3% |
| **v3** | 3,409 | 834 | 2,575 | baseline |
| **v4** | 2,795 | 444 | 2,351 | **-18%** |

---

## Token Breakdown Per Test

### Day Hike Gear
| Version | Total | Prompt | Completion | Duration |
|---------|-------|--------|------------|----------|
| v1 | 242 | 67 | 175 | 7.95s |
| v2 | 568 | 109 | 459 | 4.18s |
| v3 | 625 | 165 | 460 | 4.27s |
| v4 | 490 | 87 | 403 | 4.14s |

### Overnight Camping
| Version | Total | Prompt | Completion | Duration |
|---------|-------|--------|------------|----------|
| v1 | 279 | 63 | 216 | 2.40s |
| v2 | 775 | 105 | 670 | 6.02s |
| v3 | 749 | 161 | 588 | 5.42s |
| v4 | 582 | 83 | 499 | 4.41s |

### Three-Day Backpacking
| Version | Total | Prompt | Completion | Duration |
|---------|-------|--------|------------|----------|
| v1 | 327 | 75 | 252 | 2.54s |
| v2 | 737 | 117 | 620 | 5.56s |
| v3 | 779 | 173 | 606 | 5.75s |
| v4 | 604 | 95 | 509 | 4.52s |

### Trail Difficulty
| Version | Total | Prompt | Completion | Duration |
|---------|-------|--------|------------|----------|
| v1 | 199 | 72 | 127 | 2.39s |
| v2 | 570 | 114 | 456 | 4.10s |
| v3 | 531 | 170 | 361 | 3.54s |
| v4 | 574 | 92 | 482 | 4.49s |

### Winter Hiking
| Version | Total | Prompt | Completion | Duration |
|---------|-------|--------|------------|----------|
| v1 | 283 | 67 | 216 | 2.42s |
| v2 | 640 | 109 | 531 | 4.89s |
| v3 | 725 | 165 | 560 | 5.00s |
| v4 | 545 | 87 | 458 | 4.61s |

---

## Trace Trees from Application Insights

### v1 - Basic Instructions
```
trail_guide_v1  [17704ms]
├── v1_day-hike-gear  [7954ms | tokens: 242 (↑67 ↓175)]
│   └── chat gpt-4.1  [7954ms]
│       ├── GET  [340ms]
│       └── GET /metadata/identity/oauth2/token  [356ms]
├── v1_overnight-camping  [2398ms | tokens: 279 (↑63 ↓216)]
│   └── chat gpt-4.1  [2398ms]
├── v1_three-day-backpacking  [2542ms | tokens: 327 (↑75 ↓252)]
│   └── chat gpt-4.1  [2542ms]
├── v1_trail-difficulty  [2387ms | tokens: 199 (↑72 ↓127)]
│   └── chat gpt-4.1  [2387ms]
└── v1_winter-hiking  [2423ms | tokens: 283 (↑67 ↓216)]
    └── chat gpt-4.1  [2423ms]
```

### v2 - Enhanced Instructions
```
trail_guide_v2  [24752ms]
├── v2_day-hike-gear  [4178ms | tokens: 568 (↑109 ↓459)]
│   └── chat gpt-4.1  [4178ms]
├── v2_overnight-camping  [6022ms | tokens: 775 (↑105 ↓670)]
│   └── chat gpt-4.1  [6022ms]
├── v2_three-day-backpacking  [5561ms | tokens: 737 (↑117 ↓620)]
│   └── chat gpt-4.1  [5561ms]
├── v2_trail-difficulty  [4100ms | tokens: 570 (↑114 ↓456)]
│   └── chat gpt-4.1  [4100ms]
└── v2_winter-hiking  [4892ms | tokens: 640 (↑109 ↓531)]
    └── chat gpt-4.1  [4892ms]
```

### v3 - Production Prompt
```
trail_guide_v3  [23973ms]
├── v3_day-hike-gear  [4265ms | tokens: 625 (↑165 ↓460)]
│   └── chat gpt-4.1  [4265ms]
├── v3_overnight-camping  [5425ms | tokens: 749 (↑161 ↓588)]
│   └── chat gpt-4.1  [5425ms]
├── v3_three-day-backpacking  [5745ms | tokens: 779 (↑173 ↓606)]
│   └── chat gpt-4.1  [5745ms]
├── v3_trail-difficulty  [3536ms | tokens: 531 (↑170 ↓361)]
│   └── chat gpt-4.1  [3536ms]
└── v3_winter-hiking  [5002ms | tokens: 725 (↑165 ↓560)]
    └── chat gpt-4.1  [5002ms]
```

### v4 - Optimized Concise (WINNER)
```
trail_guide_v4_optimized_concise  [22172ms]
├── v4_optimized_concise_day-hike-gear  [4138ms | tokens: 490 (↑87 ↓403)]
│   └── chat gpt-4.1  [4138ms]
├── v4_optimized_concise_overnight-camping  [4411ms | tokens: 582 (↑83 ↓499)]
│   └── chat gpt-4.1  [4411ms]
├── v4_optimized_concise_three-day-backpacking  [4516ms | tokens: 604 (↑95 ↓509)]
│   └── chat gpt-4.1  [4516ms]
├── v4_optimized_concise_trail-difficulty  [4492ms | tokens: 574 (↑92 ↓482)]
│   └── chat gpt-4.1  [4490ms]
└── v4_optimized_concise_winter-hiking  [4614ms | tokens: 545 (↑87 ↓458)]
    └── chat gpt-4.1  [4614ms]
```

---

## Span Structure Explained

Each trace has 3 levels:

1. **Root span** (`trail_guide_v{n}`) - Covers entire version run (all 5 tests)
2. **Test child span** (`v{n}_{test-name}`) - Individual test with token/duration attributes
3. **LLM call span** (`chat gpt-4.1`) - Auto-instrumented OpenAI call, shows auth time + inference time

---

## Key Findings

### Token Efficiency (vs v3 baseline)
| Version | Token Reduction | Prompt Token Reduction | Completion Token Reduction |
|---------|----------------|------------------------|----------------------------|
| v1 | **-62%** | -59% | -63% |
| v2 | -3% | -34% | +6% |
| v3 | baseline | baseline | baseline |
| **v4** | **-18%** | **-47%** | **-9%** |

### Latency Comparison
| Version | Total Duration | Avg per Test | vs v3 |
|---------|----------------|--------------|-------|
| v1 | 17.7s | 3.5s | -27% |
| v2 | 24.8s | 5.0s | +3% |
| v3 | 24.0s | 4.8s | baseline |
| **v4** | **22.2s** | **4.4s** | **-7%** |

### Analysis
1. **v1 is most token-efficient but least detailed** - Shortest responses, may lack safety depth
2. **v2 is slightly worse than v3** - More tokens, similar quality
3. **v3 is verbose** - High prompt tokens from overly detailed instructions
4. **v4 is optimal** - 47% fewer prompt tokens, maintains completion quality, 7% faster

### Cost Implications
- **v4 saves 18% total tokens** vs v3
- **v4 saves 47% on input (prompt) tokens** - These are charged at different rates
- Lower prompt tokens = lower cost per query
- v4 maintains response quality while being more efficient

---

## Viewing in Azure Portal

### Application Insights
```
https://portal.azure.com/#@c05c9769-327d-4469-ac18-171724d77c7d/resource/subscriptions/d2866a86-ebf5-4148-8685-edb0d904e99b/resourceGroups/rg-fresh/providers/microsoft.insights%2Fcomponents/appi-46p3ahg36iyrs
```

### Log Analytics (Trace Data)
```
https://portal.azure.com/#@c05c9769-327d-4469-ac18-171724d77c7d/resource/subscriptions/d2866a86-ebf5-4148-8685-edb0d904e99b/resourceGroups/rg-fresh/providers/microsoft.operationalinsights%2Fworkspaces/logs-46p3ahg36iyrs
```

### Query to see all spans
```kql
AppDependencies
| where Name startswith "trail_guide_"
| where TimeGenerated > ago(6h)
| project Name, DurationMs, Properties
| order by TimeGenerated desc
```

---

## Scripts Used

| Script | Purpose |
|--------|---------|
| `src/tests/run_monitoring.py` | Runs 5 test prompts against each version with OpenTelemetry tracing |
| `src/tests/check_traces.py` | Queries Log Analytics to display trace tree |

---

## Conclusion

**v4_optimized_concise** is the optimal production prompt:

| Metric | v3 | v4 | Improvement |
|--------|----|----|-------------|
| Total Tokens | 3,409 | 2,795 | **-18%** |
| Prompt Tokens | 834 | 444 | **-47%** |
| Avg Duration | 4.8s | 4.4s | **-7%** |
| Response Quality | High | Maintained | Same |

The optimized prompt achieves significant cost savings (especially on input tokens) while maintaining response quality. **Deploy v4 to production.**

---

## Cleanup

To delete resources and stop billing:
```bash
az group delete -n rg-fresh --yes
```