import argparse
import sys
from app import stamp_files_in_dir, stamp_pdfs_in_dir
from app.common import create_exhibit_stamp

def main():
    parser = argparse.ArgumentParser(
        description="Automatically stamp numbered or lettered PDFs, DOCX documents, and images with exhibit labels."
    )
    parser.add_argument(
        "--position",
        choices=["top-right", "top-left", "bottom-right", "bottom-left"],
        default="bottom-right",
        help="Where to place the stamp on the page (default: bottom-right)",
    )
    parser.add_argument(
        "--color",
        default="black",
        help="Text color. Use common names (black, red, blue) or hex codes like #FF0000 (default: black)",
    )
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Apply the stamp to every single page of the document/PDF instead of just the first page",
    )
    parser.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Directory containing the files to stamp (default: current directory or launch GUI if unspecified)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )

    args = parser.parse_args()

    # Launch GUI if explicitly requested or if no arguments provided
    if args.gui or (len(sys.argv) == 1 and args.dir is None):
        try:
            from gui import launch_gui
            launch_gui()
            return
        except ImportError:
            pass

    target_dir = args.dir if args.dir else "."
    stamp_files_in_dir(target_dir, position=args.position, color=args.color, all_pages=args.all_pages)

if __name__ == "__main__":
    main()
