from __future__ import annotations


def run_hf(cells: list[dict], model_id: str, revision: str = "main", dtype: str = "float32") -> list[dict]:
    """One forward pass per prompt with a local Hugging Face causal LM.
    Candidates must be single tokens; the adapter refuses otherwise."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, dtype=getattr(torch, dtype))
    model.eval()
    cache = {}

    def tid(s):
        if s not in cache:
            ids = tok(s, add_special_tokens=False)["input_ids"]
            if len(ids) != 1:
                raise SystemExit(f"candidate {s!r} is not a single token: {ids}")
            cache[s] = ids[0]
        return cache[s]

    out = []
    with torch.inference_mode():
        for c in cells:
            ids = tok(c["prompt"], add_special_tokens=False, return_tensors="pt")["input_ids"]
            logits = model(input_ids=ids).logits[0, -1].float()
            p, n = tid(c["candidates"]["pos"]), tid(c["candidates"]["neg"])
            out.append({**{k: c[k] for k in c if k != "prompt"}, "observation": [float(logits[p]), float(logits[n])]})
    return out
