# IntelliGrade Classifier 🎓

[![CI](https://github.com/your-username/intelligrade-classifier/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/intelligrade-classifier/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Privacy: Air-Gapped](https://img.shields.io/badge/Privacy-100%25%20Air--Gapped-green.svg)](#privacy--compliance)
[![Pedagogy: Bloom's Taxonomy](https://img.shields.io/badge/Pedagogy-Revised%20Bloom's-orange.svg)](#pedagogical-framework)

> **Air-gapped, privacy-first pedagogical examination evaluation pipeline mapping questions against Revised Bloom's Taxonomy, calibrating objective difficulty (1.0–10.0), and auditing curricular balance.**

Built for the **INTELLIX AI Hackathon (Education & Knowledge Track)**.

---

## 🎯 Key Problems Solved

1. **Subjective Assessment**: Academic exam questions are traditionally scored using subjective human intuition, leading to imbalanced evaluations and poor alignment with pedagogical standards. IntelliGrade provides objective, psychometrically calibrated auditing.
2. **Administrative Bottleneck**: Manually auditing and mapping hundreds of examination questions to pedagogical frameworks consumes valuable faculty and administrative hours.
3. **Cloud Privacy & Compliance Breach**: Public cloud LLM APIs (OpenAI, Anthropic, Gemini) cannot be used for confidential, unreleased examination papers due to strict institutional governance and data-leakage risks (FERPA, GDPR).

---

## 🏗️ Air-Gapped LAN Architecture

IntelliGrade operates strictly over a private, air-gapped institutional Local Area Network (LAN):

```
┌────────────────────────────────────────────────────────────────────────┐
│                      AIR-GAPPED INSTITUTIONAL LAN                      │
│                                                                        │
│    [ Dedicated Compute Node ]               [ Orchestration Node ]     │
│       Dell Host Server (Linux/Win)             HP OmniBook (Win 11)    │
│    ┌──────────────────────────────┐         ┌────────────────────────┐ │
│    │        Ollama Daemon         │         │   Streamlit Frontend   │ │
│    │     Model: llama3:8b         │         │   (Interactive UI)     │ │
│    │                              │         └───────────┬────────────┘ │
│    │   PORT 11434 (LAN Subnet)    │◄────────────────────┤              │
│    └──────────────────────────────┘      HTTP POST      ▼              │
│                   ▲                 (stream: false)  src/ollama_client │
│                   │                                 (JSON Repair & RT) │
│                   │                                     │              │
│                   │                         Fallback    ▼              │
│                   │                         ┌────────────────────────┐ │
│                   │                         │  Offline Mock Engine   │ │
│                   │                         │  (Linguistic Rules)    │ │
│                   │                         └────────────────────────┘ │
└───────────────────┼─────────────────────────────────────┼──────────────┘
                    X                                     X
    =============================================================
              PUBLIC CLOUD / INTERNET (STRICTLY BLOCKED)
    =============================================================
```

- **Local LLM Node**: Dedicated Dell compute server running Ollama (`llama3:8b`) on the private subnet.
- **Orchestration Client**: HP OmniBook running Python 3.14, Streamlit frontend, and a resilient requests pipeline.
- **Offline Mock Engine**: High-fidelity linguistic rule engine guaranteeing 100% functionality even during LAN outages or hardware servicing.

---

## 📁 Repository Structure

```
intelligrade-classifier/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated testing pipeline (Python 3.10-3.12)
├── data/
│   └── sample_questions.csv       # Benchmark questions across STEM & humanities
├── docs/
│   ├── ARCHITECTURE.md            # In-depth topology, threat matrix & latency
│   └── PEDAGOGICAL_RUBRIC.md      # Psychometric rubric for Bloom's & Difficulty
├── scripts/
│   ├── benchmark_node.py          # CLI latency & throughput benchmark utility
│   ├── run_app.bat                # 1-click Windows Command Prompt launcher
│   └── run_app.ps1                # 1-click PowerShell launcher
├── src/
│   ├── __init__.py
│   ├── config.py                  # Dynamic runtime configuration loader
│   ├── mock_engine.py             # Heuristic rule-based offline classifier
│   ├── models.py                  # Pydantic schemas for Bloom's & evaluations
│   ├── ollama_client.py           # Resilient HTTP client with retry backoff
│   ├── parser.py                  # Multi-stage JSON repair & markdown stripping
│   ├── prompts.py                 # Calibrated psychometric system prompts
│   └── ui_components.py           # Custom CSS, Plotly gauges, radar charts & HTML dossier
├── tests/
│   ├── __init__.py
│   ├── test_client.py             # Tests for client retries, mock engine, and health
│   └── test_parser.py             # Tests for malformed JSON repair and recovery
├── .env.example                   # Environment variable template
├── .gitignore                     # Protection for private secrets & caches
├── app.py                         # Interactive Streamlit audit dashboard
├── LICENSE                        # MIT License
├── README.md                      # Project documentation
└── requirements.txt               # Dependencies
```

---

## ✨ Features & Pedagogical Capabilities

### 1. Single Question Audit & Cognitive Metrics
- **Revised Bloom's Taxonomy Placement**: Instant classification into one of the 6 cognitive process dimensions:
  `Remember (L1)` ➔ `Understand (L2)` ➔ `Apply (L3)` ➔ `Analyze (L4)` ➔ `Evaluate (L5)` ➔ `Create (L6)`.
- **Plotly Difficulty Speedometer**: Objective difficulty score from **1.0 to 10.0** with color-coded difficulty tiers.
- **Action Verbs & Domain Extraction**: Highlights explicit cognitive triggers (`calculate`, `design`, `critique`).
- **Pedagogical Reasoning & Improvement Suggestions**: Actionable advice to rebalance cognitive load.
- **🚀 Cognitive Elevator**: Provides dynamic rewordings of the question for higher Bloom tiers.

### 2. Batch Assessment Pipeline
- **Dual Input Modes**: Drag-and-drop CSV files or paste multiline question batches.
- **Exam Paper Balance Health Index (0–100%)**: Curricular alignment score evaluating if the exam is over-indexed on rote recall or properly diversified.
- **Cognitive Radar Profile**: 6-axis spider chart comparing the exam's distribution against ideal pedagogical benchmarks.
- **Difficulty Spread Histogram & Tier Donut Chart**: Instant visual inspection of exam distribution.
- **Export Options**: Export full audit data as **CSV**, **JSON**, or a print-ready **Standalone HTML Quality Assurance Dossier**.

### 3. Air-Gap Security & Diagnostics
- Real-time LAN host ping diagnostic and model list inspection.
- Instant toggle between Live Ollama Node and Offline Mock Simulation mode.
- Strict payload constraints (`format: json`, `stream: false`, temperature: `0.1`).

---

## 🚀 Quick Start Guide

### 1. Installation
```powershell
# Clone the repository
git clone https://github.com/your-username/intelligrade-classifier.git
cd intelligrade-classifier

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. Configuration
Copy `.env.example` to `.env` and set your local Ollama node details:
```ini
OLLAMA_SERVER_URL=http://<DELL_IP>:11434/api/generate
MODEL_NAME=llama3:8b
MOCK_MODE=false
AUTO_MOCK_FALLBACK=true
REQUEST_TIMEOUT=30
MAX_RETRIES=3
BACKOFF_FACTOR=1.5
```

### 3. Launch the Dashboard
Using python:
```powershell
python -m streamlit run app.py
```
Or double-click `scripts/run_app.bat` on Windows.

### 4. Run Test Suite
```powershell
python -m pytest tests/ -v
```

### 5. Benchmark Node Latency
```powershell
python scripts/benchmark_node.py
```

---

## 🛡️ Privacy & Compliance
- **Zero Cloud Telemetry**: Raw exam questions and classifications never traverse external network boundaries.
- **FERPA & Institutional Governance**: Keeps unreleased examination drafts secure on-premises.

---

## 📜 License
Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
