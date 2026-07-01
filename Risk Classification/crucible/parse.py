import re
import itertools


_BANNERS = (
    "AI Use Case",
    "Use Case Description",
    "Risk Classification",
    "Reason",
    "Requires Additional Information",
    "What additional Information",
)


def permute_label(banner):
    pieces = banner.split(" ")
    bag = set()
    for stitching in itertools.product(("", "-", " "), repeat=len(pieces) - 1):
        spelled = pieces[0]
        for joiner, piece in zip(stitching, pieces[1:]):
            spelled += joiner + piece
        bag.add(spelled)
    return bag


_DISGUISES = {banner: permute_label(banner) for banner in _BANNERS}


def dissect_records(parable, raw):
    canvas = raw

    for canonical, masks in _DISGUISES.items():
        for mask in masks:
            if mask == canonical:
                continue
            canvas = re.sub(
                rf"^[ \t]*{re.escape(mask)}\s*:",
                f"{canonical}:",
                canvas,
                flags=re.MULTILINE,
            )

    slabs = re.split(r"########END OF USE CASE########", canvas.strip())
    cleaver = re.compile(
        rf"^[ \t]*({'|'.join(re.escape(b) for b in _BANNERS)})\s*:",
        flags=re.MULTILINE,
    )

    harvest = []

    for slab in slabs:
        slab = slab.strip()
        if not re.search(r"^AI Use Case:", slab, flags=re.MULTILINE):
            continue

        bits = cleaver.split(slab)

        record = {
            "AI Use Case": parable["crest"],
            "Use Case Description": parable["gist"],
            "Risk Classification": "",
            "Reason": "",
            "Requires Additional Information": "No",
            "What additional Information": "",
        }

        for j in range(1, len(bits), 2):
            label = bits[j].strip()
            value = bits[j + 1].strip()
            if label in record:
                record[label] = value

        if record["Requires Additional Information"].lower() == "no":
            record["What additional Information"] = ""

        harvest.append(record)

    return harvest


def cleave_findings(haul):
    morsels = re.split(r"\n###### (.+)", haul)
    return {
        morsels[i].strip(): morsels[i + 1].strip()
        for i in range(1, len(morsels), 2)
    }
