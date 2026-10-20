# Exhibit Indexer & Document Stamper

An automated tool designed to stamp legal exhibit labels (e.g., `EXHIBIT 1`, `EXHIBIT A`, `EXHIBIT 101`) onto documents and media files. It automatically parses exhibit identifiers directly from filenames, formats the exhibit bounding boxes, and exports stamped PDFs into an output directory.

Supports **PDF files**, **Word documents (`.docx`, `.doc`)**, **Images (`.png`, `.jpg`, `.jpeg`, `.bmp`)**, and **Videos (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`)**.

Includes both an intuitive **Desktop GUI** and a feature-rich **Command-Line Interface (CLI)**.

---

## Features

- **Multi-Format Support**: Processes **PDFs**, **Word Documents**, **Image files**, and **Video files** (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`).
- **Video Cover Sheet Generator**: Generates a stamped **Video Exhibit Cover Sheet PDF** with file metadata (Duration, Resolution, Size) and frame previews.
- **Automated Exhibit Numbering**: Automatically extracts digits or letters at the start of filenames (e.g., `1_Contract.pdf` -> `EXHIBIT 1`, `10_Video.mp4` -> `EXHIBIT 10`).
- **Desktop GUI Application**: Built with Python's standard `tkinter` framework — no extra GUI framework installation required.
- **Flexible Stamp Placement**: Support for standard corner positions (`bottom-right`, `bottom-left`, `top-right`, `top-left`).
- **Color Customization**: Choose from preset text colors (`black`, `red`, `blue`, `navy`) or pick any custom Hex color (e.g., `#D32F2F`).
- **Single or Multi-Page Mode**: Stamp only the first page (default) or apply the exhibit stamp to all pages in every document.
- **Automated Test Suite**: Unit tests covering stamp creation, file format conversion, and batch processing logic.

---

## File Naming Conventions

The tool automatically extracts the exhibit label from the **beginning of each filename**. It supports both explicit `Exhibit_{x}_...` prefixes and direct `{x}_...` prefixes (matching numbers or letters before spaces, underscores, or hyphens).

### Examples & Expected Outputs:

| Original Filename | File Type | Extracted Label | Printed Stamp Text | Generated Output Filename |
| :--- | :--- | :--- | :--- | :--- |
| `Exhibit_1_Contract.pdf` | PDF | `1` | **`EXHIBIT 1`** | `Exhibit_1_Contract.pdf` |
| `Exhibit_B_Bank_Statement.docx` | DOCX | `B` | **`EXHIBIT B`** | `Exhibit_B_Bank_Statement.pdf` |
| `1_Contract.pdf` | PDF | `1` | **`EXHIBIT 1`** | `Exhibit_1_1_Contract.pdf` |
| `101_Deposition_Transcript.pdf` | PDF | `101` | **`EXHIBIT 101`** | `Exhibit_101_101_Deposition_Transcript.pdf` |
| `A_Bank_Statement.docx` | DOCX | `A` | **`EXHIBIT A`** | `Exhibit_A_A_Bank_Statement.pdf` |
| `5_Scene_Photo.png` | Image | `5` | **`EXHIBIT 5`** | `Exhibit_5_5_Scene_Photo.pdf` |
| `12A_Tax_Return.pdf` | PDF | `12A` | **`EXHIBIT 12A`** | `Exhibit_12A_12A_Tax_Return.pdf` |

> [!TIP]
> - **Folder-Level Exhibit Numbering**: If documents are organized inside exhibit folders (e.g., `Exhibit_25_Tyrique on 08.31.2026/` or `Exhibit_A_Medical/`), all documents inside automatically inherit the folder's exhibit identifier (**`EXHIBIT 25`**, **`EXHIBIT A`**), regardless of individual file names.
> - Filenames in root folders **can start with `Exhibit_{x}_`** or directly with **alphanumeric characters** (`0-9` or `A-Z`).
> - Files starting with symbols or underscores (e.g., `_notes.pdf` or `.document.pdf`) will be skipped automatically.

---

## Installation

### 1. Requirements
- Python 3.8+

### 2. Install Required Dependencies
Install the required manipulation & image processing libraries via `pip`:

```powershell
pip install pypdf reportlab pillow
```

*(Optional for native MS Word conversion on Windows: `pip install docx2pdf`)*

---

## Usage

### Option A: Launch Graphical User Interface (GUI)

You can launch the desktop GUI using either of the following commands:

```powershell
python gui.py
```
*or*
```powershell
python stamp.py
```

---

### Option B: Command-Line Interface (CLI)

Run `stamp.py` with command-line flags for automated or headless batch processing:

```powershell
# Basic usage (stamps all supported files in current directory with default bottom-right black stamp)
python stamp.py

# Specify target directory
python stamp.py --dir "C:\Users\username\Documents\Exhibits"

# Scan folder including all nested subfolders (recursive)
python stamp.py --dir "D:\Court Docs\Exhibit List" --recursive

# Customize position, color, and stamp all pages
python stamp.py --dir "./my_files" --position top-right --color red --all-pages -r
```

---

## Running Unit Tests

Run the automated test suite with Python's built-in `unittest` runner:

```powershell
# Run all unit test suites
python -m unittest discover -s tests -v
```

---

## Repository Structure

```
exhibit_indexer/
├── app/
│   ├── __init__.py        # Package entry point & batch dispatcher
│   ├── common.py          # Shared stamp geometry & color utility functions
│   ├── stamp_pdf.py       # PDF document stamping module
│   ├── stamp_img.py       # Image conversion & stamping module (.png, .jpg, .bmp)
│   ├── stamp_doc.py       # Word document conversion & stamping module (.docx)
│   └── stamp_video.py     # Video evidence cover sheet stamping module (.mp4, .mov)
├── tests/
│   ├── test_stamp_pdf.py   # Unit tests for PDF stamping
│   ├── test_stamp_img.py   # Unit tests for image conversion & stamping
│   ├── test_stamp_doc.py   # Unit tests for Word document processing
│   ├── test_stamp_video.py # Unit tests for Video cover sheet processing
│   └── test_stamp.py       # Integration test suite
├── stamp.py               # CLI entry point
├── gui.py                 # Tkinter desktop GUI application
├── README.md              # Repository documentation
└── .gitignore             # Git ignore configuration
```

