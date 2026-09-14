import csv
import os
import re


def process_csv_dataset(
    identifiers_file="folder_identifiers.csv",
    scanned_file="scanned_jpeg_files.csv",
    output_file="mapped_jpeg_paths.csv",
    base_dest_dir="./organized_folders",
):
    if not os.path.exists(identifiers_file) or not os.path.exists(scanned_file):
        print(
            "Error: Make sure both 'folder_identifiers.csv' and"
            " 'scanned_jpeg_files.csv' are in the working directory."
        )
        return

    # 1. Load valid folder IDs from folder_identifiers.csv
    valid_folders = set()
    with open(identifiers_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            valid_folders.add(row["folder_identifier"].strip())

    print(f"Loaded {len(valid_folders)} folder identifiers.")

    # Regex pattern to extract folder ID from filename (e.g. MS-011_1_1_1_1_J_0001.jpg)
    pattern = re.compile(r"^(MS-011_\d+_\d+_\d+_\d+)_J_\d{4}\.jpg$")

    matched_count = 0
    unmatched_count = 0

    # 2. Map scanned JPEG entries to folder paths
    with (
        open(scanned_file, mode="r", encoding="utf-8") as infile,
        open(
            output_file, mode="w", newline="", encoding="utf-8"
        ) as outfile,
    ):

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["target_path", "match_status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            filename = row["jpeg_filename"].strip()
            match = pattern.match(filename)

            if match:
                extracted_id = match.group(1)

                if extracted_id in valid_folders:
                    row["target_path"] = os.path.join(
                        base_dest_dir, extracted_id, filename
                    )
                    row["match_status"] = "MATCHED"
                    matched_count += 1
                else:
                    row["target_path"] = ""
                    row["match_status"] = "UNREGISTERED_FOLDER_ID"
                    unmatched_count += 1
            else:
                row["target_path"] = ""
                row["match_status"] = "INVALID_FILENAME_PATTERN"
                unmatched_count += 1

            writer.writerow(row)

    print(
        f"Done! Processed {matched_count + unmatched_count} entries:"
        f"\n - Matched: {matched_count}"
        f"\n - Unmatched/Invalid: {unmatched_count}"
    )
    print(f"Output saved to '{output_file}'.")


if __name__ == "__main__":
    process_csv_dataset()