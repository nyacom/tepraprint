#!/usr/bin/env python3

#============================================================
# TEPRAPRINT print utility
# nyacom (C) 2024.10
#============================================================
import sys
import pytepra
import argparse

#------------------------------------------------------------
if __name__ == "__main__":

    arg = argparse.ArgumentParser(description="Tepra Printer Control")

    arg.add_argument("--info", action="store_true", help="Get printer information")
    arg.add_argument("-tf", "--feed", action="store_true", help="Feed tape")
    arg.add_argument("-tc", "--cut", action="store_true", help="Cut tape")
    arg.add_argument("--vervose", action="store_true", help="Verbose output")

    arg.add_argument("--dryrun", action="store_true", help="Perform a dry run without printing")
    arg.add_argument("--cutmode", choices=["none", "cut", "half-cut", "job-cut", "job-half-cut"], default="cut", help="Set the tape cut mode")
    arg.add_argument("--tapewidth", type=int, default=0, help="Set the tape width in mm. 0 for auto")
    arg.add_argument("--copies", type=int, default=1, help="Number of copies to print")
    arg.add_argument("--print-length", type=int, default=0, help="Set the print label length in mm. 0 for auto")
    arg.add_argument("--print-margin", type=int, default=0, help="Set the print margin in mm")
    arg.add_argument("--print-contrast", type=int, default=0, help="Set the print contrast (-3 to 3)")
    arg.add_argument("--print-dither", type=int, default=1, help="Enable graphic dithering (0: off, 1: on)")

    arg.add_argument("-i", "--input", type=str, required=False, help="Input file containing data to print. Use '-' for stdin")

    args = arg.parse_args()

    tepra = pytepra.PyTepra()
    tepra.connect()

    # if info flag is set, get printer information and exit
    if args.info:
        # Get printer information
        print("Device   :", tepra.get_device_id())
        print("Media(mm):", tepra.get_tape_width_mm())
        exit(0)

    # Tape feed
    if args.feed:
        tepra.cmd_tape_feed()
        exit(0)

    # Tape cut
    if args.cut:
        tepra.cmd_tape_cut()
        exit(0)

    # Tape width
    if args.tapewidth > 0:
        tepra.tape_width_mm = args.tapewidth
    else:
        tepra.tape_width_mm = tepra.get_tape_width_mm()

    # Read input data
    # if input is '-' read from stdin
    if args.input == '-':
        # Read from stdin
        img_stream = sys.stdin.buffer.read()
        print(img_stream)

    else:
        # Read from input file
        with open(args.input, 'rb') as f:
            img_stream = f.read()

    # Fit image to tape
    img, ih, iw = tepra.fit_image_to_tape(img_stream)

    # Set print length
    if args.print_length > 0:
        tepra.print_length = args.print_length

    else:
        tepra.print_length = int(iw // pytepra.UNIT_MM + tepra.print_start_margin)

    print("DEBUG: Image width:", iw)
    print("DEBUG: Image height", ih)
    print("DEBUG: Print margin:", tepra.print_start_margin)
    print("DEBUG: Print length:", tepra.print_length)

    # Set print margin
    tepra.print_start_margin = args.print_margin

    # Set cut mode
    if args.cutmode == "none":
        tepra.tape_cut_mode = pytepra.Tape_cut_mode.NONE

    elif args.cutmode == "cut":
        tepra.tape_cut_mode = pytepra.Tape_cut_mode.CUT

    elif args.cutmode == "half-cut":
        tepra.tape_cut_mode = pytepra.Tape_cut_mode.HALF_CUT

    elif args.cutmode == "job-cut":
        tepra.tape_cut_mode = pytepra.Tape_cut_mode.JOB_CUT

    elif args.cutmode == "job-half-cut":
        tepra.tape_cut_mode = pytepra.Tape_cut_mode.JOB_HALF_CUT

    # Set contrast
    tepra.print_contrast = args.print_contrast

    # Set dithering
    if args.print_dither == 0:
        tepra.print_dither = False
    else:
        tepra.print_dither = True

    # Print graphic
    tepra.print_graphic(data=tepra.image2byte(img), copies=args.copies)
