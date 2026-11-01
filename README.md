# Support Ticket Triage Workflow

An LLM workflow that reads incoming customer support tickets, extracts structured data, validates it, flags
the tickets a human must handle, and produces a prioritised worklist. All sample tickets are **synthetic**.

## Why a workflow and not an agent?

The steps are fixed and the output must be predictable, so the model is used for one job only (extraction)
and ordinary code does the rest:

```
samples/*.txt -> LLM extraction (JSON) -> schema validation (1 retry) -> rule checks -> sorted worklist
                                                  |                          |
                                      fails twice: send to human     safety/legal risk, refund request,
                                                                     unknown category -> human review
```

Design choices:
- **Schema validation with pydantic**, plus one retry that feeds the validation error back to the model.
- **The model never decides money or risk.** It only reports `refund_requested` and `safety_or_legal_risk`; plain code in `src/schema.py` routes those tickets to a person.
- **Prompt-injection check.** Sample 05 tries to order the model to approve a refund. The ticket text is treated as data, and a refund mention still goes to a human.
- **Failures are visible.** A ticket that cannot be processed is marked high urgency and sent to human review, never dropped.
- **Azure OpenAI**, configured through environment variables; the model value is your deployment name.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env            # add your Azure OpenAI endpoint, key, deployment
python src/triage.py samples
pytest                          # tests use a fake model, no key needed
```

Output: `out/triage.md` (readable worklist, human-review tickets first) and `out/triage.csv`.

## Limitations

Text files only, no persistence, and extraction accuracy depends on the model. There is no accuracy evaluation yet.

## Ideas for next steps

A labelled test set with a measured accuracy, a reply-drafting step that always waits for human approval, and the same flow rebuilt in a no-code tool (see the n8n workflow repo).
