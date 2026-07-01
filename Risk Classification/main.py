import csv
import argparse

from dotenv import load_dotenv

from crucible.index import VERDICTS, ROSTER
from crucible.inventory import Ledger
from crucible.parse import dissect_records
from precinct.annotate import Composer, preamble
from precinct.orchestrate import traverse_inputs
from outpost.cabinet import coax_oracle


load_dotenv()


def judge_records(source, destination, picked):
    panel = [(ROSTER[k][0], k, ROSTER[k][1]) for k in picked if k in ROSTER]
    if not panel:
        raise ValueError("No valid models specified")

    print(f"Using {len(panel)} models: {[seat[2] for seat in panel]}")

    ledger = Ledger()
    composer = Composer()

    with open(destination, mode="w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerow([
            "Company Name", "Use Case Name", "Use Case Description",
            "Risk Classification", "Reason", "Model Distribution",
            "Chosen Model", "Token Cost ($)",
        ])

    with open(source, mode="r", encoding="utf-8-sig") as fh:
        for index, row in enumerate(csv.DictReader(fh)):
            tagged_name = row.get("Company Name", "")
            label = row.get("Use Case Name", "")
            blurb = row.get("Use Case Description", "")

            print(f"Processing row {index + 1}: {tagged_name} - {label}")

            parable = {"crest": label, "gist": blurb}
            stitched = f"AI Use Case: {label}\nUse Case Description: {blurb}"
            petition = composer.bind(preamble, stitched)

            chorus = []
            for breed, banner, billing in panel:
                try:
                    chorus.append(coax_oracle(banner, breed, petition, ledger))
                except Exception as mishap:
                    print(f"Error with {billing}: {str(mishap)}")
                    chorus.append(f"Error: {str(mishap)}")

            harvest = dissect_records(parable, "".join(chorus))

            tally_box, picks = {}, []
            for record in harvest:
                verdict = record["Risk Classification"]
                if verdict not in VERDICTS:
                    record["Risk Classification"] = verdict = "Uncertain"
                tally_box[verdict] = tally_box.get(verdict, 0) + 1
                picks.append(verdict)

            ceiling = max(tally_box.values())
            contenders = [v for v, n in tally_box.items() if n == ceiling]
            if len(contenders) > 1:
                contenders.sort(
                    key=lambda x: VERDICTS.index(x) if x in VERDICTS else -1,
                    reverse=True,
                )
            crown = contenders[0]

            voters = [seat[2] for seat in panel]
            distribution = "\n".join(f"{m}: {p}" for m, p in zip(voters, picks))

            survivors = [r for r in harvest if r["Risk Classification"] == crown]
            chosen = max(survivors, key=lambda x: len(x["Reason"]))
            picked_voter = voters[harvest.index(chosen)]

            with open(destination, mode="a", newline="", encoding="utf-8-sig") as fa:
                csv.writer(fa).writerow([
                    tagged_name,
                    label,
                    blurb,
                    crown,
                    chosen["Reason"],
                    distribution,
                    picked_voter,
                    ledger.balance(),
                ])

            ledger.wipe()

    print(f"Classification complete. Results saved to: {destination}")


def main():
    parser = argparse.ArgumentParser(
        description="EU AI Act Risk Classification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py search -i companies.csv -o use_cases.csv
  python main.py classify -i use_cases.csv -o classifications.csv
  python main.py classify -i use_cases.csv -o classifications.csv -m chatgpt claude

Input CSV Formats:
  Search:   Company Name, URLs (or URL)
  Classify: Company Name, Use Case Name, Use Case Description

Available Models: chatgpt, claude, deepseek, gemini, mistral
""",
    )

    parser.add_argument(
        "command",
        choices=["search", "classify"],
        help="Command to run: 'search' for URL searching or 'classify' for risk classification",
    )

    parser.add_argument("--input-file", "-i", type=str, required=True,
                        help="Input CSV file path")
    parser.add_argument("--output-file", "-o", type=str, required=True,
                        help="Output CSV file path")

    parser.add_argument(
        "--models", "-m", type=str, nargs="+",
        choices=["chatgpt", "claude", "deepseek", "gemini", "mistral"],
        default=["claude"],
        metavar="MODEL",
        help="Select one or more models for classification (default: claude)",
    )

    flags = parser.parse_args()

    if flags.command == "search":
        print("Running search workflow...")
        print(f"Input CSV: {flags.input_file}")
        print(f"Output CSV: {flags.output_file}")
        traverse_inputs(flags.input_file, flags.output_file)
    else:
        print("Running classification workflow...")
        print(f"Input CSV: {flags.input_file}")
        print(f"Output CSV: {flags.output_file}")
        print(f"Using models: {', '.join(flags.models)}")
        judge_records(flags.input_file, flags.output_file, flags.models)


if __name__ == "__main__":
    main()
