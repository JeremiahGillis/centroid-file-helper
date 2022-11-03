#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 1/20/22

@author: Jeremiah Gillis
@contact: jeremiah@embeddedbytes.io

The purpose of this code is to assign part numbers in place of values in the KiCAD
centroid file. The part numbers are pulled from the BOM. This is useful when
automatically assigning parts in OpenPnP through the "Import KiCAD .pos Files".
Assign Parts and Use only Value as PartId options need to be checked when importing
into OpenPnP.

This script expects two arguments to be passed, the BOM and the Centroid File.
IE: replace_value_with_part_number.py BOM.csv Centroid.pos
"""

import sys
import csv

data_bom = []
fieldnames_bom = []

try:
    with open(sys.argv[1], encoding="utf8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames_bom = reader.fieldnames
        for row in reader:
            data_bom.append(row)
except:
    print("File \"" + sys.argv[1] + "\" not found.")
    quit()

data_pos = []
fieldnames_pos = []

try:
    with open(sys.argv[2], encoding="utf8", newline="") as csvfile:
        rows = (line.split() for line in csvfile)
        for row in rows:
            if '#' in row[0]:
                row.pop(0)
                if 'Ref' in row[0]:
                    fieldnames_pos = row
                else:
                    continue

            data_pos.append(row)
except:
    print("File \"" + sys.argv[2] + "\" not found.")
    quit()

# Find Ref and Val index
ref_index_pos = None
val_index_pos = None

for index, val in enumerate(fieldnames_pos):
    if val == 'Ref':
        ref_index_pos = index
    elif val == 'Val':
        val_index_pos = index

if ref_index_pos == None or val_index_pos == None:
    print("Ref or Val not found in the centroid file.")
    quit()

# Replace Val in the centroid file with part number from BOM
items_changed = 0

for row_pos in data_pos:
    for row_bom in data_bom:
        for item in row_bom['Designators'].split(','): # Must iterate in case multiple designators are in one field
            if item.strip() == row_pos[ref_index_pos]:
                if row_pos[val_index_pos] != row_bom['Part Number']:
                    row_pos[val_index_pos] = row_bom['Part Number']
                    items_changed += 1

print("Number of values changed: ", items_changed)

# Create a new centroid file with the modified values
if ".\\" in sys.argv[2]:
    original_filename = sys.argv[2].split(".\\")[1]
else:
    original_filename = sys.argv[2]
filename = original_filename.split('.')[0] + '_PartId.' + original_filename.split('.')[1]

# Create CSV which will be detected correctly during OpenPnP import
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\t')
    data_pos[0].insert(0, '#')
    writer.writerows(data_pos)