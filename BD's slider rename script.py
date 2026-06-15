import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# Path to BodySlide's SliderSets folder
SLIDERSETS_PATH = r"Data\CalienteTools\BodySlide\SliderSets"

# Reference 3BA .osp
REFERENCE_3BA_OSP = r"Data\CalienteTools\BodySlide\SliderSets\3BBB Amazing.osp"

# Load all standard 3BA slider names
tree = ET.parse(REFERENCE_3BA_OSP)
root = tree.getroot()

standard_sliders = {
    slider.get("name")
    for slider in root.iter("Slider")
    if slider.get("name")
}

# Collect all .osp files except the reference
osp_files = []

for root_dir, _, files in os.walk(SLIDERSETS_PATH):
    for file in files:
        if file.lower().endswith(".osp"):
            full_path = os.path.join(root_dir, file)
            if os.path.abspath(full_path) != os.path.abspath(REFERENCE_3BA_OSP):
                osp_files.append(full_path)

# Assign prefixes
letter_counts = defaultdict(int)
prefixes = {}

for osp in sorted(osp_files):
    filename = os.path.splitext(os.path.basename(osp))[0]
    first_letter = filename[0].upper()

    letter_counts[first_letter] += 1

    if letter_counts[first_letter] == 1:
        prefix = f"BD{first_letter}"
    else:
        prefix = f"BD{first_letter}{letter_counts[first_letter]}"

    prefixes[osp] = prefix

# Rename sliders
for osp in osp_files:
    tree = ET.parse(osp)
    root = tree.getroot()

    duplicate_counts = defaultdict(int)
    modified = False

    for slider in root.iter("Slider"):
        name = slider.get("name")

        if not name:
            continue

        # Skip standard 3BA sliders
        if name in standard_sliders:
            continue

        # Skip already processed sliders
        if name.startswith("BD"):
            continue

        duplicate_counts[name] += 1

        if duplicate_counts[name] == 1:
            new_name = prefixes[osp] + name
        else:
            new_name = (
                prefixes[osp]
                + str(duplicate_counts[name])
                + name
            )

        slider.set("name", new_name)
        print(f"{os.path.basename(osp)}: {name} -> {new_name}")

        modified = True

    if modified:
        tree.write(osp, encoding="utf-8", xml_declaration=True)

print("Done.")