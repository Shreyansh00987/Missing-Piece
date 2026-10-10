"""
Modular inference pipeline for Missing Piece benchmark.
Supports:
- Local Hugging Face models via transformers (e.g. SmolLM2, Qwen2.5)
- Commercial & API models (OpenAI, Anthropic, Gemini, Groq, Ollama)
- Deterministic baseline controls (Always-Answer, Always-Abstain, Random)
- Resumable file-based caching (JSONL) with latency tracking
"""

import os
import json
import time
import abc
import random
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

from missing_piece.models import BenchmarkExample, ModelResponse


# Standard task prompt template enforcing output contract
SYSTEM_PROMPT = """You are an exacting mathematical and logical reasoning evaluation system.
Solve the word problem using ONLY the information provided in the prompt.
If the answer cannot be uniquely determined from the stated facts, or if the supplied facts are contradictory or inconsistent, return INSUFFICIENT.
Otherwise, return the exact numerical answer in the required JSON format.

Your response MUST be a valid JSON object matching this schema:
{"status": "ANSWER", "answer": "<exact numerical value>"}
or
{"status": "INSUFFICIENT", "answer": null}

Do not include reasoning, explanations, or text outside the JSON object."""


def format_user_prompt(problem_text: str) -> str:
    """Format single benchmark item for model consumption."""
    return f"Problem Statement:\n{problem_text}\n\nProvide your JSON response:"


class BaseModelAdapter(abc.ABC):
    """Abstract base class for all inference backends."""
    
    def __init__(self, model_id: str):
        self.model_id = model_id

    @abc.abstractmethod
    def generate(self, problem_text: str) -> Tuple[str, float]:
        """
        Generate response given problem statement.
        Returns: (raw_text, latency_ms)
        """
        pass


class HeuristicBaselineAdapter(BaseModelAdapter):
    """
    Controlled baseline heuristics for statistical reference:
    - always_answer: Answers '20' for every problem.
    - always_abstain: Returns 'INSUFFICIENT' for every problem.
    - random_choice: Randomly answers or abstains.
    """
    
    def __init__(self, mode: str, seed: int = 42):
        super().__init__(model_id=f"baseline_{mode}")
        self.mode = mode
        self.rng = random.Random(seed)

    def generate(self, problem_text: str) -> Tuple[str, float]:
        t0 = time.time()
        time.sleep(0.001) # Simulate tiny latency
        
        if self.mode == "always_answer":
            # Answers a typical plausible positive integer
            res = json.dumps({"status": "ANSWER", "answer": "20"})
        elif self.mode == "always_abstain":
            res = json.dumps({"status": "INSUFFICIENT", "answer": None})
        elif self.mode == "random_choice":
            if self.rng.random() < 0.5:
                res = json.dumps({"status": "ANSWER", "answer": str(self.rng.randint(10, 50))})
            else:
                res = json.dumps({"status": "INSUFFICIENT", "answer": None})
        else:
            res = json.dumps({"status": "ANSWER", "answer": "0"})
            
        latency = (time.time() - t0) * 1000.0
        return res, latency


class LocalTransformersAdapter(BaseModelAdapter):
    """Runs a local causal language model via Hugging Face transformers."""
    
    def __init__(self, model_name: str, max_tokens: int = 64):
        clean_id = model_name.split("/")[-1]
        super().__init__(model_id=clean_id)
        self.model_name = model_name
        self.max_tokens = max_tokens
        
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Use torch.bfloat16 or float32 depending on availability
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()

    def generate(self, problem_text: str) -> Tuple[str, float]:
        import torch
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{format_user_prompt(problem_text)}"
        
        # Apply chat template if supported
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_user_prompt(problem_text)}
            ]
            try:
                inputs_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except Exception:
                inputs_text = full_prompt
        else:
            inputs_text = full_prompt

        inputs = self.tokenizer(inputs_text, return_tensors="pt")
        
        t0 = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_tokens,
                do_sample=False, # Strictly greedy decoding for deterministic benchmark
                temperature=None,
                top_p=None,
                pad_token_id=self.tokenizer.eos_token_id
            )
        latency = (time.time() - t0) * 1000.0
        
        # Slice only generated new tokens
        input_len = inputs["input_ids"].shape[1]
        gen_tokens = outputs[0][input_len:]
        raw_text = self.tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        
        return raw_text, latency


class APIModelAdapter(BaseModelAdapter):
    """Generic HTTP adapter for OpenAI/Anthropic/Gemini compatible endpoints."""
    
    def __init__(self, model_id: str, api_url: str, api_key: str, max_tokens: int = 128):
        super().__init__(model_id=model_id)
        self.api_url = api_url
        self.api_key = api_key
        self.max_tokens = max_tokens

    def generate(self, problem_text: str) -> Tuple[str, float]:
        import httpx
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_user_prompt(problem_text)}
            ],
            "temperature": 0.0,
            "max_tokens": self.max_tokens
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        t0 = time.time()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(self.api_url, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    raw_text = data["choices"][0]["message"]["content"]
                    latency = (time.time() - t0) * 1000.0
                    return raw_text, latency
            except Exception as e:
                if attempt == max_retries - 1:
                    latency = (time.time() - t0) * 1000.0
                    return f"ERROR: {str(e)}", latency
                time.sleep(2 ** attempt)

        return "ERROR: Unknown API failure", 0.0


class InferenceRunner:
    """Manages execution, caching, resumption, and response collection."""
    
    def __init__(self, cache_dir: str = "outputs/cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, model_id: str) -> str:
        safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in model_id)
        return os.path.join(self.cache_dir, f"{safe_id}_responses.jsonl")

    def load_cache(self, model_id: str) -> Dict[str, ModelResponse]:
        """Load already completed model responses from disk cache."""
        cache_path = self._get_cache_path(model_id)
        cached: Dict[str, ModelResponse] = {}
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        resp = ModelResponse(**item)
                        cached[resp.example_id] = resp
        return cached

    def evaluate_model(
        self,
        adapter: BaseModelAdapter,
        examples: List[BenchmarkExample],
        limit: Optional[int] = None,
        use_cache: bool = True
    ) -> List[ModelResponse]:
        """
        Evaluate a model on benchmark examples, resuming from cache if available.
        """
        cached = self.load_cache(adapter.model_id) if use_cache else {}
        cache_path = self._get_cache_path(adapter.model_id)
        
        target_examples = examples[:limit] if limit else examples
        responses: List[ModelResponse] = []
        
        # Open cache file in append mode
        with open(cache_path, "a", encoding="utf-8") as cache_file:
            for i, ex in enumerate(target_examples):
                if ex.example_id in cached:
                    responses.append(cached[ex.example_id])
                    continue
                
                # Run inference
                try:
                    raw_text, latency = adapter.generate(ex.problem_text)
                    err = None
                except Exception as e:
                    raw_text = f"EXCEPTION: {str(e)}"
                    latency = 0.0
                    err = str(e)

                resp = ModelResponse(
                    example_id=ex.example_id,
                    model_id=adapter.model_id,
                    raw_text=raw_text,
                    latency_ms=round(latency, 2),
                    created_at=datetime.now(timezone.utc).isoformat(),
                    error=err
                )
                
                # Append to cache immediately
                cache_file.write(resp.model_dump_json() + "\n")
                cache_file.flush()
                
                cached[ex.example_id] = resp
                responses.append(resp)

        return responses
