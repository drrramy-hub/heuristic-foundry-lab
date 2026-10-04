# Heuristic Foundry Lab

An open-source AI-assisted interface inspection toolkit by **Ramy Hammady** for product and UI/UX designers.

**Prototype v0.1.** Upload UI screenshots, describe a task, receive source-linked observations from three AI reviewer roles, and review findings before exporting. It is a heuristic inspection aid, not a substitute for expert review, user testing or accessibility assessment. Live Azure operation and evaluation quality have not been verified in the development environment.

## Quick start

Python 3.11+ required:

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:8082** and select **Explore fictional demo**. No account or model calls are required. The demo is a fixed, labelled example of an invented plan selector, not an analysis of your uploaded files.

## Connect Microsoft Foundry

Deploy an Azure OpenAI model supporting **image inputs, the Responses API and JSON mode**. Model and region availability varies; verify support in the official documentation below. Configure your resource endpoint and actual deployment name, not an assumed model name.

Bash:
```sh
export FOUNDRY_ENDPOINT='https://YOUR-RESOURCE.openai.azure.com/openai/v1'
export FOUNDRY_DEPLOYMENT='YOUR-VISION-MODEL-DEPLOYMENT'
read -s -p 'Azure API key: ' FOUNDRY_API_KEY; echo
export FOUNDRY_API_KEY
python app.py
```

In zsh use `read -s 'FOUNDRY_API_KEY?Azure API key: '; echo` for the key prompt. PowerShell uses `$env:FOUNDRY_ENDPOINT` and `$env:FOUNDRY_DEPLOYMENT`; set the key securely in your local environment. Never commit keys or paste them into chat. `.env.example` documents settings but is not automatically loaded.

Also accepts `https://YOUR-RESOURCE.services.ai.azure.com/openai/v1`. Project-scoped URLs and sovereign clouds are not supported by this prototype. The adapter uses HTTPS REST calls, `api-key`, deployment in `model`, image data URLs in `input_image`, JSON mode and `store: false`. Microsoft recommends Entra ID; this starter uses a local server-side API key. Add identity-based authentication and production security before any hosted deployment.

## Designer workflow

1. Export 1–3 PNG/JPEG interface screenshots from your design tool. Each must be <=2 MB and <=12 megapixels.
2. Remove personal/confidential content. The tool does not automatically anonymise images.
3. Describe the intended audience, task and product context.
4. Confirm permission to transmit the screenshots and context to Azure.
5. Run the three-role review. This makes three sequential model calls, up to 120 seconds each; each has a 5,000 output-token cap. Calls may incur charges. No automatic retries.
6. Verify each observation against its screen ID and location; adjust human severity, record a decision and add notes.
7. Export JSON or Markdown with the original AI findings, human decisions, source hashes, heuristic coverage and follow-up tests. Exported notes are editable, not an authenticated audit trail.

The interface generates a tailored evaluation report rather than code for a new application. No external URLs, Figma APIs or interactive prototypes are visited. Text and images are treated as untrusted evidence; prompt instructions cannot guarantee protection against malicious content.

## Evaluation framework

Mapped to Jakob Nielsen's [10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), using original short paraphrases in the app. These are established rules of thumb, not a certification standard. No NN/g or Microsoft affiliation or endorsement.

| Role | Heuristics covered | Inspection focus |
|---|---|---|
| Interaction reviewer | H1–H4 | State cues, terminology, exit/reversal affordances, consistency |
| Task reviewer | H5–H7 | Mistake prevention, information availability, efficiency |
| Clarity reviewer | H8–H10 | Content priority, visible error guidance, help |

These are **application-orchestrated reviewer roles**, not Foundry Agent Service resources or autonomous browser agents. All use the same configured model in separate calls; three roles do not establish independent human consensus. No synthesis call fabricates an aggregate score. Findings remain attributable to the reviewer; overlapping observations may need human consolidation.

Each heuristic is marked `finding`, `no_visible_issue` or `not_assessable`. Unshown behaviour should be marked not assessable. Model compliance still requires review. Finding severity is provisional: 1 cosmetic, 2 minor, 3 major, 4 suspected critical blocker. Human reviewers can additionally select 0 (not a problem). Confidence labels are model judgements, not calibrated probabilities. There is no overall pass/fail or usability percentage.

## Evidence and limitations

The server validates screen IDs, heuristic assignment, coverage consistency, required fields and severity values. It cannot verify that an AI observation actually appears in an image or is relevant to real users. Source hashes help identify the reviewed files; exports omit the image pixels, so retain your authorised screenshots separately.

Screenshots cannot establish keyboard navigation, assistive technology semantics, responsive behaviour beyond the supplied states, response times, error recovery behaviour or task completion. Visual accessibility concerns can be explored through follow-up testing, but this tool does not measure contrast or certify WCAG conformance. See [evaluation guide](docs/EVALUATION.md).

## Privacy and operation

The server binds only to 127.0.0.1, checks Host and Origin, validates request sizes and image decoding, rejects redirects and restricts Azure endpoint domains. One evaluation runs at a time. UI content and model text use text nodes, not executable HTML. No browsing, tool execution or model-triggered external actions.

Screenshots are held in memory and sent to your Azure resource three times (once per reviewer). The app does not deliberately log or write input/report content to disk; explicit exports contain task context and review notes. `store: false` is not a guarantee of zero Azure retention; service policies and your configuration still apply. Refreshing the page loses review decisions. Do not expose this development server to the internet; it has no multi-user authentication or encrypted persistence.

If a reviewer fails, the report is rejected rather than presented as complete. Earlier calls may still be billable. The UI shows errors without upstream response bodies or credentials. There is no cancellation of an Azure call already submitted.

## Test and contribute

```sh
python -m unittest discover -s tests -v
```

Offline tests cover request shape, image validation, coverage, evidence references, request-origin protection and demo behaviour. They do not test live model quality. See [CONTRIBUTING.md](CONTRIBUTING.md). MIT-licensed; source code is free, Azure use may cost money. No adoption or impact figures are claimed.

## References

- Jakob Nielsen: https://www.nngroup.com/articles/ten-usability-heuristics/
- Microsoft Responses API: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses
- REST reference: https://learn.microsoft.com/en-us/rest/api/aifoundry/azureopenai/responses

Integration documentation checked 4 October 2026. This repository is a starting point requiring real deployment and researcher evaluation.
