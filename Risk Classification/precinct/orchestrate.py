import csv
import urllib.parse as urlparse

from crucible.inventory import Ledger
from crucible.foray import prowl_domain
from crucible.parse import cleave_findings


def traverse_inputs(source, destination):
    surveyor_breed = "claude-sonnet-4-20250514"
    ledger = Ledger()

    with open(destination, mode="w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerow(["Company Name", "Use Case Name", "Use Case Description"])

    with open(source, mode="r", encoding="utf-8-sig") as fh:
        for index, row in enumerate(csv.DictReader(fh)):
            tagged_name = row.get("Company Name", "")
            address = row.get("URLs", "")

            if not address:
                continue

            shards = urlparse.urlparse(address).netloc.split(".")

            if not tagged_name and len(shards) >= 2:
                tagged_name = shards[-2].capitalize()

            haunt = ".".join(shards[-2:]) if len(shards) >= 2 else ""

            if not haunt:
                continue

            print(f"Processing URL {index + 1}: {haunt} (Company: {tagged_name})")

            try:
                spoils = cleave_findings(prowl_domain(surveyor_breed, haunt))
                print(f"Found {len(spoils)} use cases for {tagged_name}")

                with open(destination, mode="a", newline="", encoding="utf-8-sig") as fa:
                    pen = csv.writer(fa)
                    if spoils:
                        for label, blurb in spoils.items():
                            pen.writerow([tagged_name, label, blurb])
                    else:
                        pen.writerow([
                            tagged_name,
                            "No structured use cases found",
                            "No use cases found in the search result.",
                        ])

                print(f"Successfully processed: {address}")

            except Exception as mishap:
                print(f"Error processing {address}: {str(mishap)}")
                with open(destination, mode="a", newline="", encoding="utf-8-sig") as fa:
                    csv.writer(fa).writerow([tagged_name, "Error", f"Error: {str(mishap)}"])

    print(f"Search results saved to CSV: {destination}")
