# Training guide

`braid` runs multi-phase training on the polymorphic spine.

## Phases (5 concretes)

| Phase | What it does |
|---|---|
| `phase1pretrain` | Continued pretraining of the Phase-1 base |
| `rewardproxyphase` | Train the long-term-return reward proxy |
| `rqvaephase` | Train RQ-VAE codebook (optional) |
| `phase2postrain` | Ranking training with the braided loss |
| `distillationphase` | Knowledge distillation from teacher to student |

Each phase exposes `setup()`, `run()`, `observability()`, `metrics()`.

## Optimizers (4 concretes)

`adamw`, `lion`, `adafactor`, `schedulefree`. Each is a factory that
takes `params` and returns a torch optimizer.

## Schedulers (4 concretes)

`cosine`, `linearwarmupcosine`, `wsd`, `constant`. Each is a factory that
takes an optimizer and returns a torch scheduler.

## Checkpoints (4 concretes)

`best`, `latest`, `everyn`, `ema`. Each implements `shouldsave`,
`pathfor`, etc.

## Miners (5 concretes)

`random`, `inbatch`, `checkpointtopk`, `popularityaware`, `contrastive`.

## Curricula (5 concretes)

`linear`, `cosine`, `step`, `adaptive`, `twostage`.

## Batchers (4 concretes)

`padded`, `packed`, `lengthbucketed`, `sortedpadded`.

## Trackers (4 concretes)

`aim`, `mlflow`, `wandb`, `tensorboard`.

## The braided loss

```yaml
loss:
  type: braidedloss
  terms:
    - type: rankingce
      weight: 1.0
    - type: lmax
      weight: 0.1
    - type: diversityentropy
      weight: 0.05
    - type: rewardweighted
      weight: 0.5
```

`braidedloss.compute(outputs, batch)` returns the sum of weighted term
losses. Add new terms via additional concretes under `loss` (e.g.
`loss:contrastive`).

## Reward-weighted training

```yaml
rewards:
  type: compositereward
  members:
    - type: longtermreturn
      weight: 1.0
    - type: diversitybonus
      weight: 0.3
```

`compositereward` registers under `reward:compositereward` despite not
being a "real" reward — composability is a first-class feature.

## Distributed training

Single-node first. FSDP support is wired through
`braid.training.loop.runphase`. Multi-node via Accelerate config.

## Determinism

`make seed` seeds Python, NumPy, and (when torch is installed) PyTorch
+ CUDA. The pipeline records a per-step seed for replay.
