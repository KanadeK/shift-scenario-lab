# Competitor and naming scan

Scan date: 2026-07-19. Searches used GitHub public repository metadata for the exact
name, exact slug, and model-drift simulation terms. `drift-canvas` has active same-slug
repositories, so this project uses the safe alternate slug `shift-scenario-lab`.

| Repository | Stars | Updated | Main focus | Overlap |
| --- | ---: | --- | --- | --- |
| [withfish/drift-canvas](https://github.com/withfish/drift-canvas) | 0 | 2026-04-01 | No description published | Name only |
| [bharathsubbiah/Drift-Canvas](https://github.com/bharathsubbiah/Drift-Canvas) | 0 | 2026-05-18 | No description published | Name only |
| [evidentlyai/evidently](https://github.com/evidentlyai/evidently) | 7,706 | 2026-07-19 | ML and LLM observability | Drift metrics, not pre-deployment scenario economics |
| [NannyML/nannyml](https://github.com/NannyML/nannyml) | 2,145 | 2026-07-08 | Post-deployment data science | Monitoring, not interactive policy sensitivity |
| [deepchecks/deepchecks](https://github.com/deepchecks/deepchecks) | 4,039 | 2026-07-18 | Continuous ML and data validation | Validation checks, not cost-matrix scenario comparison |
| [SeldonIO/alibi-detect](https://github.com/SeldonIO/alibi-detect) | 2,540 | 2026-07-18 | Outlier, adversarial, and drift detection | Detection algorithms, not business-impact simulation |
| [whylabs/whylogs](https://github.com/whylabs/whylogs) | 2,828 | 2026-07-18 | Data and model logging | Profiles and monitoring, not offline counterfactual-like what-if analysis |
| [microsoft/responsible-ai-toolbox](https://github.com/microsoft/responsible-ai-toolbox) | 1,803 | 2026-07-18 | Responsible AI exploration and assessment | Broader assessment UI; no narrow local scenario workflow |
| [online-ml/river](https://github.com/online-ml/river) | 5,881 | 2026-07-18 | Online machine learning | Streaming learning, not scenario analysis |
| [scikit-multiflow/scikit-multiflow](https://github.com/scikit-multiflow/scikit-multiflow) | 798 | 2026-06-30 | Streaming-data ML | Stream algorithms, not threshold and cost experimentation |

## Decision

No sampled active repository is highly isomorphic to the MVP. The deliberate distinction
is a small, local-first workflow for **pre-deployment**, deterministic, cost-sensitive
scenario comparison with group slices. It does not claim to replace drift detection,
production monitoring, fairness audits, or causal inference.

