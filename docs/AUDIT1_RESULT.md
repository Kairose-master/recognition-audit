# Audit 1 result — option order in an LLM-as-judge (arithmetic verification)

Status: **RUN AS PREREGISTERED; UNINFORMATIVE — NO RECOGNIZER READS THE TASK.**

| recognizer | comparative acc. | decision acc. | `S` | `V` | `E` (of 112) | depth-0 closed |
|---|---:|---:|---:|---:|---:|:---:|
| Pythia-70M (control) | 0.54 | 0.22 | 1.00 | 1.00 | 38 | no (705 / 419) |
| Qwen2.5-0.5B | 0.54 | 0.57 | 1.00 | 0.60 | 5 | no (169 / 122) |
| Qwen2.5-1.5B | 0.54 | 0.75 | 1.00 | 1.00 | 11 | no (250 / 150) |

All three recognizers are at chance on the comparative readout, so Gate R
fails for all and `S`, `V` are noise values. A check with the Qwen chat
template on 32 cells gave the same (0.42): the format is not the cause.
The task is: verifying a two-digit arithmetic candidate at a single answer
token is beyond these models.

Prediction failures, recorded: Qwen accuracies were predicted 0.6–0.8 and
above 0.8; observed 0.54 and 0.54. `E` for the control was predicted ≤ 3
and observed 38: with 20 nearly constant bits, identical profiles occur by
degeneracy. Lesson for the tool: report the number of non-constant columns
alongside `E`, and require Gate R before any other statistic is read.

Next: Audit 1b, same design with candidates a small instruction-tuned model
can verify without computing (capital cities).
