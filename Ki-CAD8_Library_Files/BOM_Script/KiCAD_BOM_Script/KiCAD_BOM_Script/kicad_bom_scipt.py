import csv
import sys
import kicad_netlist_reader
from collections import defaultdict

# Check if a netlist file is provided
if len(sys.argv) < 2:
    print("Usage: generate_bom.py <netlist.xml>")
    sys.exit(1)

# Read netlist from KiCAD
netlist = kicad_netlist_reader.netlist(sys.argv[1])

# Define output CSV filename
output_file = "bom_output.csv"

# Define BOM fields
BOM_FIELDS = [
    "Item Number", "Quantity", "Reference Designator", "Manufacturer",
    "Man. Part Num", "Distributor", "Dist. Part Num",
    "Description", "Package", "Part Type", "Notes"
]

# Dictionary to store grouped components
bom_dict = defaultdict(lambda: {
    "Quantity": 0,
    "Reference Designator": [],
    "Manufacturer": "",
    "Man. Part Num": "",
    "Distributor": "",
    "Dist. Part Num": "",
    "Description": "",
    "Package": "",
    "Part Type": "",
    "Notes": ""
})

# Process components and group by Man. Part Num
for component in netlist.components:
    mfg_part = component.getField("Man. Part Num").strip()

    if not mfg_part:
        print(f"Warning: Component {component.getRef()} is missing a Man. Part Num.")
        continue  # Skip parts without a Manufacturer Part Number

    bom_dict[mfg_part]["Quantity"] += 1
    bom_dict[mfg_part]["Reference Designator"].append(component.getRef())
    bom_dict[mfg_part]["Manufacturer"] = component.getField("Manufacturer")
    bom_dict[mfg_part]["Man. Part Num"] = mfg_part
    bom_dict[mfg_part]["Distributor"] = component.getField("Distributor")
    bom_dict[mfg_part]["Dist. Part Num"] = component.getField("Dist. Part Num")
    bom_dict[mfg_part]["Description"] = component.getField("Description")
    bom_dict[mfg_part]["Package"] = component.getFootprint()
    bom_dict[mfg_part]["Part Type"] = component.getField("Part Type")
    bom_dict[mfg_part]["Notes"] = component.getField("Notes")

# Convert the dictionary to a list and format Reference Designators
bom_list = []
item_number = 1

for part_number, data in sorted(bom_dict.items()):
    bom_list.append({
        "Item Number": item_number,
        "Quantity": data["Quantity"],
        "Reference Designator": ", ".join(sorted(data["Reference Designator"])),
        "Manufacturer": data["Manufacturer"],
        "Man. Part Num": data["Man. Part Num"],
        "Distributor": data["Distributor"],
        "Dist. Part Num": data["Dist. Part Num"],
        "Description": data["Description"],
        "Package": data["Package"],
        "Part Type": data["Part Type"],
        "Notes": data["Notes"]
    })
    item_number += 1

# Write to CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=BOM_FIELDS)
    writer.writeheader()
    writer.writerows(bom_list)

print(f"BOM successfully generated: {output_file}")
