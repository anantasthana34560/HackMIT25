import csv
import os
import argparse


CATEGORIES = [
    "Comedy",
    "Education",
    "Museum",
    "Sightseeing",
    "Adventure",
    "Historic",
    "Relaxing",
]


def categorize_keyword(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["comedy", "improv", "stand-up", "stand up", "laugh"]):
        return "Comedy"
    if any(k in t for k in ["class", "workshop", "lesson", "course", "lecture", "science", "robotics", "stem"]):
        return "Education"
    if any(k in t for k in ["museum", "exhibit", "gallery", "observatory", "planetarium"]):
        return "Museum"
    if any(k in t for k in ["tour", "cruise", "view", "sightseeing", "panoramic", "observatory", "walk", "trail", "boat"]):
        return "Sightseeing"
    if any(k in t for k in ["kayak", "kayaking", "bike", "biking", "hike", "hiking", "adventure", "canoe", "zipline"]):
        return "Adventure"
    if any(k in t for k in ["historic", "history", "historical", "freedom trail", "old state", "colonial", "presidential", "tour of"]):
        return "Historic"
    if any(k in t for k in ["picnic", "tea", "relax", "quiet", "garden", "courtyard"]):
        return "Relaxing"
    return "Sightseeing"


def add_keyword_column(input_csv: str, output_csv: str) -> None:
    with open(input_csv, newline="", encoding="utf-8") as fin, open(output_csv, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        if "Keyword" not in fieldnames:
            fieldnames.append("Keyword")
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            text = row.get("Experience Description") or row.get("Company Name") or " ".join(str(v) for v in row.values())
            row["Keyword"] = categorize_keyword(text)
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Add Keyword category to experiences CSV")
    parser.add_argument("--in", dest="input_csv", required=True)
    parser.add_argument("--out", dest="output_csv", default="")
    parser.add_argument("--inplace", action="store_true")
    args = parser.parse_args()

    input_csv = args.input_csv
    if args.inplace:
        tmp_path = input_csv + ".tmp"
        add_keyword_column(input_csv, tmp_path)
        os.replace(tmp_path, input_csv)
        print(f"Updated {input_csv} with Keyword column")
    else:
        output_csv = args.output_csv or (os.path.splitext(input_csv)[0] + "_with_keywords.csv")
        add_keyword_column(input_csv, output_csv)
        print(f"Wrote {output_csv}")


if __name__ == "__main__":
    main()


