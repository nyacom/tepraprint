#!/bin/env python3

# PPD用の用紙サイズを生成するスクリプト

# テープの長さ5mm単位でPPDの用紙サイズを生成する

# *DefaultPageSize: P-12
# *PageSize P-4x10/P-4x10mm: "<</PageSize [34 11]>>setpagedevice"
# *PageSize P-6x10/P-6x10mm: "<</PageSize [34 17]>>setpagedevice"
# *PageSize P-9x10/P-9x10mm: "<</PageSize [34 26]>>setpagedevice"
# *PageSize P-12x10/P-12x10mm: "<</PageSize [34 34]>>setpagedevice"
# *PageSize P-18x10/P-18x10mm: "<</PageSize [34 51]>>setpagedevice"
# *PageSize P-24x10/P-24x10mm: "<</PageSize [34 68]>>setpagedevice"
# *PageSize P-36x10/P-36x10mm: "<</PageSize [34 102]>>setpagedevice"
# *PageSize P-48x10/P-48x10mm: "<</PageSize [34 136]>>setpagedevice"
# *PageSize P-50x10/P-50x10mm: "<</PageSize [34 142]>>setpagedevice"
# *PageSize P-100x10/P-100x10mm: "<</PageSize [34 283]>>setpagedevice"
# 
# *% Note: とりあえず12mmで設定してある
# *DefaultImageableArea: P-12
# *ImageableArea P-4/P-4mm: "0 0 34 11"
# *ImageableArea P-6/P-6mm: "0 0 34 17"
# *ImageableArea P-9/P-9mm: "0 0 34 26"
# *ImageableArea P-12/P-12mm: "0 0 34 34"
# *ImageableArea P-18/P-18mm: "0 0 34 51"
# *ImageableArea P-24/P-24mm: "0 0 34 68"
# *ImageableArea P-36/P-36mm: "0 0 34 102"
# *ImageableArea P-48/P-48mm: "0 0 34 136"
# *ImageableArea P-50/P-50mm: "0 0 34 142"
# *ImageableArea P-100/P-100mm: "0 0 34 283" 
# 
# *DefaultPaperDimension: 12mm
# *PaperDimension P-4/P-4mm: "34 11"
# *PaperDimension P-6/P-6mm: "34 17"
# *PaperDimension P-9/P-9mm: "34 26"
# *PaperDimension P-12/P-12mm: "34 34"
# *PaperDimension P-18/P-18mm: "34 51"
# *PaperDimension P-24/P-24mm: "34 68"
# *PaperDimension P-36/P-36mm: "34 102"
# *PaperDimension P-48/P-48mm: "34 136"
# *PaperDimension P-50/P-50mm: "34 142"
# *PaperDimension P-100/P-100mm: "34 283" 



TAPE_WIDTH = [4, 6, 9, 12, 18, 24, 36]  # テープ幅 (mm)
TAPE_LENGTH = range(10, 505, 5)  # テープ長さ (mm)
#TAPE_LENGTH = range(10, 15, 5)  # テープ長さ (mm)

# PageSizeの生成
print(f"*DefaultPageSize: P-12x40")
for tw in TAPE_WIDTH:
    for length in TAPE_LENGTH:
        hp = int(tw / 25.4 * 72)
        wp = int(length / 25.4 * 72)
        print(f"*PageSize P-{tw}x{length}/P-{tw}x{length}mm: \"<</PageSize [{wp} {hp}]>> setpagedevice\"")

print("\n")
# ImageableAreaの生成
print(f"*DefaultImageableArea: P-12x40")
for tw in TAPE_WIDTH:
    for length in TAPE_LENGTH:
        hp = int(tw / 25.4 * 72)
        wp = int(length / 25.4 * 72)
        print(f"*ImageableArea P-{tw}x{length}/P-{tw}x{length}mm: \"0 0 {wp} {hp}\"")

print("\n")
# PaperDimensionの生成
print(f"*DefaultPaperDimension: P-12x40")
for tw in TAPE_WIDTH:
    for length in TAPE_LENGTH:
        hp = int(tw / 25.4 * 72)
        wp = int(length / 25.4 * 72)
        print(f"*PaperDimension P-{tw}x{length}/P-{tw}x{length}mm: \"{wp} {hp}\"")

print("\n")
