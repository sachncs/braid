# Verbalizer guide

`braid` ships five verbalizers. They all expose `render(context: dict) -> str`
and are registered under the `verbalizer` category.

## eventsignal (default)

The GenRec paper's flagship verbalizer. Event-signal truncation with rich
metadata, template-rendered with a deterministic f-string.

```python
v = braid.registry.create("verbalizer", "eventsignal", budget=20)
prompt = v.render({
    "user": "alice",
    "metadata": {"locale": "us"},
    "history": [
        {"kind": "play", "itemid": 1, "duration": 600},
        {"kind": "thumbup", "itemid": 7, "duration": 0},
    ],
    "candidates": [3, 4, 5],
})
```

## narrative

Paragraph-style: events become a comma-separated story
(*"thumb-up'd item 1, watched item 2 for 300s..."*).

## structuredjson

Emits a JSON object: `{"task": "rank", ...}`.

## compactelbow

Truncates to a precomputed elbow point. Re-tune at runtime via `setelbow(n)`.

## semanticsummary

Compresses history into a taste summary (*"action (5), comedy (3), ..."*).

## Truncation strategies

5 concretes under the `truncation` category:

| Name | Behavior |
|---|---|
| `head` | Most-recent N |
| `signalweighted` | Top-N by signal score |
| `elbow` | Pre-computed elbow point |
| `diversity` | Greedy distinct-item selection |
| `hierarchicalsummary` | Top-N hot + summarized tail |

## Elbow finder CLI

```python
from braid.verbalizer.elbowfinder import run
sweep = run(events, krange=range(5, 105, 5))
# → {5: 5, 10: 10, ..., 100: 100}  (signal-weighted truncation sizes)
```

## Templates

3 concretes under the `template` category: `jinja2`, `fstring`, `mustache`.
All satisfy `idempotent`.

## Token counters

3 concretes under the `tokencounter` category:
- `hfcount` — wraps HF tokenizer.
- `tiktokencount` — wraps tiktoken.
- `approxcount` — heuristic per-character.

`braid-elbow` (the CLI) automates the §5.4 context-length sweep.
