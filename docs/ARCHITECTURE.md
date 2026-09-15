# System Architecture & Network Topology

## 1. High-Level Concept
**IntelliGrade** is an air-gapped pedagogical audit pipeline designed to classify, calibrate, and critique academic examination papers without routing confidential exam content through public cloud LLMs (OpenAI, Anthropic, Gemini).

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

---

## 2. Component Specifications

### A. Dedicated Compute Node (Dell Server)
- **Role**: High-throughput cognitive evaluation engine.
- **Service**: Ollama daemon exposed exclusively to the institutional subnet (`0.0.0.0:11434` or `<DELL_IP>:11434`).
- **Target Model**: `llama3:8b` (quantized 4-bit / 8-bit for rapid inference with deterministic temperature 0.1).
- **Zero-Cloud Contract**: No external outbound connections, no external telemetry or metrics collection.

### B. Orchestration Client (HP OmniBook)
- **Role**: User interface, question parsing, batch file ingest, and statistical aggregation.
- **Runtime**: Python 3.14 + Streamlit 1.62.
- **Resilience Engine**:
  - `OllamaClient`: Implements exponential backoff retries (factor 1.5x) and 30s connection timeout.
  - `parse_evaluation_response`: Cleans markdown fences (` ```json ... ``` `), isolates JSON substrings via regex delimiters, strips illegal trailing commas, and provides heuristic recovery.
  - `MockPedagogicalEngine`: Built-in rule-based classifier based on 100+ Bloom's cognitive action verbs and grammatical syntax. Serves as automatic fallback if the Dell server goes offline.

---

## 3. Threat Model & Privacy Governance

| Threat Vector | Cloud API Vulnerability | IntelliGrade Air-Gapped Solution |
|---|---|---|
| **Pre-Release Exam Leakage** | Questions sent to third-party cloud data centers could be retained in server logs or training data. | Data packets never traverse the institutional router/firewall. Operates entirely over local physical/LAN switch. |
| **FERPA / GDPR Compliance** | Transferring academic assessment materials to cloud providers often requires formal vendor auditing. | 100% On-Premises. Zero third-party vendor involvement. |
| **Internet Outage / Exam Jamming** | Loss of external internet connectivity halts examination paper auditing. | High-fidelity offline mock engine enables continuous auditing even with zero connectivity. |
