"""Robust API client for communicating with local/remote Ollama LLM node."""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple
import requests

from src.config import get_config
from src.mock_engine import mock_engine
from src.models import QuestionEvaluation
from src.parser import parse_evaluation_response
from src.prompts import SYSTEM_PROMPT, build_evaluation_prompt

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local/LAN Ollama node with resilient retries and mock fallback."""

    def __init__(self):
        self.session = requests.Session()

    def check_health(self) -> Tuple[bool, str, List[str]]:
        """
        Probe Ollama server availability and inspect loaded models.
        Returns (is_online, status_message, list_of_models).
        """
        cfg = get_config()
        base_url = cfg.get_base_url()
        tags_url = f"{base_url}/api/tags"

        try:
            resp = self.session.get(tags_url, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                return (
                    True,
                    f"Ollama server online at {base_url} ({len(models)} model(s) installed)",
                    models,
                )
            return (
                False,
                f"Ollama responded with HTTP status {resp.status_code} at {tags_url}",
                [],
            )
        except requests.exceptions.ConnectionError:
            return (
                False,
                f"Connection Refused: Cannot reach Ollama host at {base_url}. Ensure Ollama is running and accessible over LAN.",
                [],
            )
        except requests.exceptions.Timeout:
            return (
                False,
                f"Connection Timed Out: Ollama server at {base_url} did not respond within 4.0s.",
                [],
            )
        except Exception as e:
            return (
                False,
                f"Network Diagnostic Failure: {type(e).__name__} - {str(e)}",
                [],
            )

    def evaluate_question(
        self,
        question_text: str,
        force_mock: Optional[bool] = None,
    ) -> QuestionEvaluation:
        """
        Evaluate single question against Revised Bloom's Taxonomy.
        Enforces payload constraints: stream=False, format=json.
        """
        if not question_text or not question_text.strip():
            return QuestionEvaluation(
                question="",
                blooms_level="Understand",
                blooms_level_index=2,
                difficulty_score=1.0,
                pedagogical_reasoning="Empty or whitespace-only question submitted.",
                improvement_suggestions="Please enter an examination question to evaluate.",
                evaluation_source="client_guard",
                error_message="Question text cannot be blank.",
            )

        cfg = get_config()
        use_mock = force_mock if force_mock is not None else cfg.mock_mode

        if use_mock:
            return mock_engine.evaluate(question_text)

        endpoint = cfg.ollama_server_url
        payload = {
            "model": cfg.model_name,
            "prompt": build_evaluation_prompt(question_text),
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": cfg.num_predict,
                "temperature": cfg.temperature,
            },
        }

        last_error = ""
        for attempt in range(1, cfg.max_retries + 1):
            start_time = time.time()
            try:
                logger.info(
                    f"Sending evaluation request to {endpoint} (attempt {attempt}/{cfg.max_retries})."
                )
                resp = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=cfg.request_timeout,
                    headers={"Content-Type": "application/json"},
                )
                latency = round(time.time() - start_time, 3)

                if resp.status_code == 200:
                    resp_json = resp.json()
                    model_output = resp_json.get("response", "")
                    return parse_evaluation_response(
                        raw_response=model_output,
                        original_question=question_text,
                        latency_seconds=latency,
                        evaluation_source=f"ollama ({cfg.model_name})",
                    )
                else:
                    last_error = (
                        f"Server error HTTP {resp.status_code}: {resp.text[:200]}"
                    )
                    logger.warning(last_error)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as net_err:
                latency = round(time.time() - start_time, 3)
                last_error = f"{type(net_err).__name__}: {str(net_err)}"
                logger.warning(
                    f"Attempt {attempt} failed with network error: {last_error}"
                )

            except Exception as ex:
                latency = round(time.time() - start_time, 3)
                last_error = f"Unexpected error: {str(ex)}"
                logger.error(last_error)

            # Exponential backoff delay if more attempts remain
            if attempt < cfg.max_retries:
                delay = cfg.backoff_factor ** attempt
                time.sleep(delay)

        # All retries exhausted
        if cfg.auto_mock_fallback:
            logger.warning(
                "Ollama endpoint unreachable after all retries. Triggering auto-fallback to offline mock engine."
            )
            fallback_eval = mock_engine.evaluate(question_text)
            fallback_eval.error_message = (
                f"Ollama server unreachable ({last_error}). Evaluated via resilient offline mock engine."
            )
            return fallback_eval

        # Resilient error result without throwing unhandled exception
        return QuestionEvaluation(
            question=question_text,
            blooms_level="Understand",
            blooms_level_index=2,
            difficulty_score=5.0,
            pedagogical_reasoning=f"System failed to contact Ollama endpoint at {endpoint}.",
            improvement_suggestions="Verify Ollama service is active and network route is configured.",
            evaluation_source="failed",
            error_message=last_error,
        )

    def evaluate_batch(
        self,
        questions: List[str],
        force_mock: Optional[bool] = None,
        progress_callback=None,
    ) -> List[QuestionEvaluation]:
        """Process multiple questions iteratively with progress updates."""
        results: List[QuestionEvaluation] = []
        total = len(questions)

        for idx, q in enumerate(questions):
            cleaned_q = q.strip()
            if not cleaned_q:
                continue

            result = self.evaluate_question(cleaned_q, force_mock=force_mock)
            results.append(result)

            if progress_callback:
                progress_callback(idx + 1, total, result)

        return results


# Global singleton client instance
client = OllamaClient()
