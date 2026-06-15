import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# Paths
SLIDERSETS_PATH = r"Data\CalienteTools\BodySlide\SliderSets"
REFERENCE_3BA_OSP = r"Data\CalienteTools\BodySlide\SliderSets\3BBB Amazing.osp"

# Words to ignore when generating prefixes
IGNORE_WORDS = {
    # BodySlide tags
    "BD",
    "3BA",
    "CBBE",
    "BHUNP",
    "UNP",
    "UUNP",
    "DLC1",
    "DLC2",

    # Generic words
    "ARMOR",
    "ARMOUR",
    "OUTFIT",
    "ROBES",
    "ROBE",
    "CLOTHES",
    "CLOTHING",
    "BODY",
    "SET",

    # Equipment pieces
    "BOOTS",
    "SHOES",
    "HELMET",
    "HOOD",
    "MASK",
    "GAUNTLETS",
    "GLOVES",
    "BRACERS",
    "BELT",
    "PANTS",
    "SKIRT",
    "TOP",
    "DRESS",

    # Descriptors
    "LIGHT",
    "HEAVY"
}

# ---------------------------------------------------------------------
# Load standard 3BA slider names
# ---------------------------------------------------------------------

tree = ET.parse(REFERENCE_3BA_OSP)
root = tree.getroot()

standard_sliders = {
    slider.get("name")
    for slider in root.iter("Slider")
    if slider.get("name")
}

# ---------------------------------------------------------------------
# Find all OSP files
# ---------------------------------------------------------------------

osp_files = []

for root_dir, _, files in os.walk(SLIDERSETS_PATH):
    for file in files:
        if file.lower().endswith(".osp"):
            full_path = os.path.join(root_dir, file)

            if os.path.abspath(full_path) != os.path.abspath(REFERENCE_3BA_OSP):
                osp_files.append(full_path)

# ---------------------------------------------------------------------
# PASS 1: Collect SliderSet names
# ---------------------------------------------------------------------

sliderset_names = set()

for osp in osp_files:

    try:
        tree = ET.parse(osp)
        root = tree.getroot()

        for sliderset in root.iter("SliderSet"):

            name = sliderset.get("name")

            if name:
                sliderset_names.add(name)

    except Exception as e:
        print(f"Error reading {osp}: {e}")

# ---------------------------------------------------------------------
# Generate deterministic prefixes
# ---------------------------------------------------------------------

prefix_counts = defaultdict(int)
sliderset_prefixes = {}

for sliderset_name in sorted(sliderset_names):

    words = []

    for word in sliderset_name.split():

        cleaned = word.upper()

        # Ignore numbers
        if cleaned.isdigit():
            continue

        # Ignore common words
        if cleaned in IGNORE_WORDS:
            continue

        words.append(word)

    if not words:
        continue

    # Single-word names: Dragonbone -> D
    # Multi-word names: Dark Brotherhood -> DB
    initials = "".join(word[0].upper() for word in words)

    base_prefix = "BD" + initials

    prefix_counts[base_prefix] += 1

    if prefix_counts[base_prefix] == 1:
        prefix = base_prefix
    else:
        prefix = f"{base_prefix}{prefix_counts[base_prefix]}"

    sliderset_prefixes[sliderset_name] = prefix

# ---------------------------------------------------------------------
# PASS 2: Rename sliders
# ---------------------------------------------------------------------

for osp in osp_files:

    tree = ET.parse(osp)
    root = tree.getroot()

    modified = False

    for sliderset in root.iter("SliderSet"):

        sliderset_name = sliderset.get("name")

        if sliderset_name not in sliderset_prefixes:
            continue

        prefix = sliderset_prefixes[sliderset_name]

        duplicate_counts = defaultdict(int)

        for slider in sliderset.iter("Slider"):

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
                new_name = prefix + name
            else:
                new_name = f"{prefix}{duplicate_counts[name]}{name}"

            slider.set("name", new_name)

            print(
                f"{sliderset_name}: "
                f"{name} -> {new_name}"
            )

            modified = True

    if modified:
        tree.write(osp, encoding="utf-8", xml_declaration=True)

print("Done.")
