# EU AI Act Risk Classification Tool

A two-pass utility built around large language models. The first pass canvases a website for AI use cases. The second pass weighs the resulting use cases against the EU AI Act risk tiers.

## Invocation

The tool is driven by a single entry point and dispatches between two routines based on the first positional argument.

```bash
python main.py <routine> -i <input.csv> -o <output.csv>
```

`<routine>` accepts one of:

- `search`  - canvases the supplied domains and emits structured use cases.
- `classify` - assigns a risk tier to every use case in the input file.

### Common flags

| Flag | Long form | Required | Notes |
|------|-----------|----------|-------|
| `-i` | `--input-file`  | yes | path to the CSV that feeds the routine |
| `-o` | `--output-file` | yes | path the routine will write into       |
| `-m` | `--models`      | no  | one or more of: `chatgpt`, `claude`, `deepseek`, `gemini`, `mistral` (only used by `classify`; defaults to `claude`) |

### `search` routine

Reads a CSV with columns `Company Name` and `URLs`. The surveyor model is fixed at `claude-sonnet-4-20250514`. Output rows have `Company Name`, `Use Case Name`, `Use Case Description`.

```bash
python main.py search -i companies.csv -o use_cases.csv
```

### `classify` routine

Reads a CSV with columns `Company Name`, `Use Case Name`, `Use Case Description`. Each row is sent to every selected model. Their answers are pooled, the tier with the most votes wins, and ties resolve in favour of the lower-risk tier. The reason text from the most verbose model wins the “Chosen Model” slot.

```bash
# default — claude only
python main.py classify -i use_cases.csv -o classifications.csv

# ensemble
python main.py classify -i use_cases.csv -o classifications.csv -m chatgpt claude gemini

# full panel
python main.py classify -i use_cases.csv -o classifications.csv -m chatgpt claude deepseek gemini mistral
```

Output columns:

`Company Name`, `Use Case Name`, `Use Case Description`, `Risk Classification`, `Reason`, `Model Distribution`, `Chosen Model`, `Token Cost ($)`

## Tier vocabulary

The classifier emits exactly one of:

- `Prohibited AI system`
- `High-risk AI system under Annex I`
- `High-risk AI system under Annex III`
- `High-risk AI system with transparency obligations`
- `System with transparency obligations`
- `Low-risk AI system`
- `Uncertain`

## Environment

The tool reads its credentials from a `.env` file at the repository root:

- `ANTHROPIC_KEY`
- `OpenAI_KEY`
- `DEEPSEEK_KEY`
- `GEMINI_KEY`
- `MISTRAL_KEY`

## End-to-end example

```bash
python main.py search   -i companies.csv  -o use_cases.csv
python main.py classify -i use_cases.csv  -o classifications.csv
```

Or chained:

```bash
python main.py search -i companies.csv -o use_cases.csv && \
python main.py classify -i use_cases.csv -o classifications.csv
```

## Acknowledgment
The Bavarian AI Act Accelerator is a two-year project funded by the Bavarian State Ministry of Digital Affairs to support SMEs, start-ups, and the public sector in Bavaria in complying with the EU AI Act. Under the leadership of the appliedAI Institute for Europe and in collaboration with Ludwig Maximilian University, the Technical University of Munich, and the Technical University of Nuremberg, training, resources, and events are being offered. The project objectives include reducing compliance costs, shortening the time to compliance, and strengthening AI innovation. To achieve these objectives, the project is divided into five work packages: project management, research, education, tools and infrastructure, and community.
