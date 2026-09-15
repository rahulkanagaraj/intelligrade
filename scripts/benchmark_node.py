"""CLI benchmark utility for measuring Dell Ollama node latency and throughput."""

import argparse
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_config, update_config
from src.ollama_client import client

BENCHMARK_PROMPTS = [
    ("Short (Remember)", "What is the boiling point of pure water at 1 atm?"),
    ("Medium (Apply)", "Calculate the kinetic energy of a 1200kg vehicle traveling at 25 m/s."),
    ("Complex (Analyze)", "Compare and contrast synchronous and asynchronous replication in distributed databases under partition failure conditions."),
    ("Extensive (Create)", "Design an air-gapped, zero-trust cryptographic protocol for inter-institutional examination grading validation."),
]


def run_benchmark(force_mock: bool = False, iterations: int = 1):
    cfg = get_config()
    mode_str = "OFFLINE MOCK ENGINE" if force_mock or cfg.mock_mode else f"LIVE OLLAMA NODE ({cfg.ollama_server_url})"
    
    print("=" * 70)
    print(f"  INTELLIGRADE LATENCY & PEDAGOGICAL BENCHMARK")
    print(f"  Target: {mode_str}")
    print(f"  Model:  {cfg.model_name}")
    print("=" * 70)

    if not force_mock and not cfg.mock_mode:
        print("Pinging Ollama node...")
        online, msg, models = client.check_health()
        if online:
            print(f"✅ Node online: {msg}")
        else:
            print(f"❌ Warning: Node offline ({msg}). Falling back to mock engine.")
            force_mock = True

    latencies = []
    print("\nRunning benchmark battery:")
    print(f"{'Tier':<22} | {'Bloom Level':<12} | {'Difficulty':<10} | {'Latency':<10}")
    print("-" * 65)

    for label, prompt in BENCHMARK_PROMPTS:
        prompt_latencies = []
        last_res = None
        for _ in range(iterations):
            t0 = time.time()
            res = client.evaluate_question(prompt, force_mock=force_mock)
            elapsed = time.time() - t0
            prompt_latencies.append(elapsed)
            last_res = res

        avg_lat = sum(prompt_latencies) / len(prompt_latencies)
        latencies.append(avg_lat)
        print(f"{label:<22} | {last_res.blooms_level.value:<12} | {last_res.difficulty_score:<10.1f} | {avg_lat:<8.2f}s")

    print("-" * 65)
    print(f"Average Round-Trip Latency: {sum(latencies)/len(latencies):.2f}s")
    print(f"Min Latency: {min(latencies):.2f}s | Max Latency: {max(latencies):.2f}s")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Benchmark IntelliGrade latency.")
    parser.add_argument("--url", type=str, help="Override Ollama server URL")
    parser.add_argument("--model", type=str, help="Override model name")
    parser.add_argument("--mock", action="store_true", help="Force offline mock mode")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations per prompt")
    args = parser.parse_args()

    if args.url:
        update_config(ollama_server_url=args.url)
    if args.model:
        update_config(model_name=args.model)

    run_benchmark(force_mock=args.mock, iterations=args.iterations)


if __name__ == "__main__":
    main()
