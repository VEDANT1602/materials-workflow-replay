# Recovering an archived classifier result

This supplement reproduces the finite-catalog analysis and masked record-linkage experiment for the accompanying paper. OpenML supplies the archived evaluations. The authors of the original runs trained the classifiers. The study software groups their public metrics and performs two checks against public out-of-fold predictions.

## Recreate the tables

The historical snapshot is `catalog.csv`. Each row has a task ID, dataset name, run ID, flow ID and the three original score values. The score remains in the units supplied by OpenML. Run pages use https://www.openml.org/r/RUN_ID. The task links are listed in references.md. The 21 API requests, page sizes and raw response hashes are in `api_sources.csv`. The first page of an unversioned public API may change. Use the supplied snapshot to reproduce the reported numbers. To request a new snapshot, work in a copy and run `python get_catalog.py --cache ../openml_cache`.

Use Python 3.12 with the versions in `requirements.txt`. Starting in this directory:

```sh
python prepare_cases.py --prompt-dir prompts --key-dir ../machine-test-keys
python analyze.py --key ../machine-test-keys/scoring_key.json --responses qwen_answers.csv smol_answers.csv
python flow_sensitivity.py
python positive_control.py --key-dir ../machine-test-keys --scores diagnostic/qwen_answers.csv diagnostic/smol_answers.csv
python aggregate_predictions.py --cache ../prediction-cache
python verify.py
```

Network access is required only to fetch source data or model weights. Reproduce the bulk numerical analysis offline from catalog.csv and the saved model outputs. The source of the archived scalar is `area_under_roc_curve`. A tolerance of ±0.01 refers to the midpoint of the feasible AUC interval and every candidate run in the specified task and catalog. The mean absolute error column for a median guess is a descriptive catalog quantity and uses the entire compatible set, including the original record.

## Re-run the two model families

Model provenance files alongside each answer table identify the public repository, exact model revision, file name, SHA-256, tokenizer, case counts, start/end times and runtime version. The study used CPU-only inference, two threads and Q4_K_M GGUF checkpoints. With a C++ toolchain and the Python inference dependencies, obtain the checkpoints as follows. Working-directory examples assume a POSIX shell.

```sh
mkdir -p ../weights
curl -fL https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/9217f5db79a29953eb74d5343926648285ec7e67/qwen2.5-0.5b-instruct-q4_k_m.gguf -o ../weights/qwen.gguf
curl -fL https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/resolve/09816acd5d99df7be770d85ea30822623dab342c/SmolLM2-135M-Instruct-Q4_K_M.gguf -o ../weights/smol.gguf
python respond.py --prompts prompts/prompt_cases.json --model Qwen2.5-0.5B-Instruct --weights ../weights/qwen.gguf --out qwen_answers.csv
python respond.py --prompts prompts/prompt_cases.json --model SmolLM2-135M-Instruct --weights ../weights/smol.gguf --out smol_answers.csv
python respond.py --prompts diagnostic/prompts.json --model Qwen2.5-0.5B-Instruct --weights ../weights/qwen.gguf --out diagnostic/qwen_answers.csv
python respond.py --prompts diagnostic/prompts.json --model SmolLM2-135M-Instruct --weights ../weights/smol.gguf --out diagnostic/smol_answers.csv
```

Then re-run the scoring commands. Regeneration will create fresh execution timestamps. Floating-point logits can vary with CPU, build and batching. Both labels are single tokens for these checkpoints. The forced choice compares only those two logits, with ties resolved to A. The runner has no answer-key argument or access to a remote model. It uses no prior answers. Each distinct query is evaluated from empty context, with exact duplicate text mapped back to all corresponding records. The primary experiment contains 112 pairs, 224 records and 86 distinct rendered prompts. The positive control contains 49 disjoint pairs, each queried with each candidate as target, giving 98 records and 58 distinct prompts.

`PROTOCOL.md` is the locally frozen design. `AMENDMENTS.md` explains the unavailable task. `EXECUTION.md` preserves the reason for replacing token-prefix reuse, and `initial-execution/` retains the preliminary unmodified outputs. `DIAGNOSTIC.md` describes the separate, post hoc positive control. The response files identify the separately trained Qwen and SmolLM2 families. The earlier same-family pilot is excluded from all reported counts. These are local provenance records, not a public preregistration.

## Numeric and literal rounding

Catalog buckets use decimal nearest rounding with ties to even. Signed zero is collapsed to numeric zero. Under literal string matching, treating “-0.0” and “0.0” as different symbols would add one coarse two-field guarantee and one unique run, both on credit-g. That gives 1,111 and 44 instead of the reported 1,110 and 43. The frozen responder text preserves what was originally displayed. Zero primary query records and four positive-control records contain “-0.0”. In both trials the number of distinguishable pairs is identical under numeric and literal comparison.

## Human follow-up

No human result is reported. `human-participant/` describes two distinct tasks and provides blank forms. The live, unadministered participant files and answer keys are held by the coordinator, outside the public supplement. The 28 paired lookup cases exclude every run used in the machine trials. The second task contains eight additional anonymized real prediction files, with no run shared across the two tasks. A participant reconstructs the original AUC by writing executable code. One group receives full aggregation instructions on all eight runs. A second group receives only the AUC endpoint on all eight. This between-reader design avoids teaching the missing convention through a complete example. Assign only one form of each task to any individual and do not include the answer keys, study outputs or this coordinator README in participant packets. Controls such as study information, consent and review appropriate to the future recruitment setting belong to that future study. No participant was recruited for this work. Register the intended sampling and analysis before collecting new evidence.

The matching coordinator keys for these exact forms are supplied separately to the author. Use `human_packet.py score --form X --response completed.csv --key human-key.csv --out linkage.csv` for the first task. Use `human_rerun.py score --form X --response rerun.csv --key rerun-key.csv --out rerun-scores.csv` for the second. The rerun scorer separates six-decimal agreement from accuracy within 0.01. Inspect each returned program and match its output to the submitted values before counting a completed human reanalysis. Once assignments have been unblinded, the coordinator can choose to release the source mapping and adjudicated outputs according to the agreed participant terms.

## Attribution

Research scripts in this supplement are distributed under the MIT license. The historical run metrics and transformed prediction records are attributed to OpenML and the benchmark contributors and remain under their source terms. They are excluded from the software license. The original datasets and model weights are not redistributed. Attribution, source links and scope of use are in references.md. The public catalog contains original classifier scores. The private future-participant packet contains anonymized held-out predictions for chess positions and handwritten digits. It contains no individual researchers' contact details or raw participant measurements.
