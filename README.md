# Exhibit Indexer & PDF Stamper

An automated tool designed to stamp legal exhibit labels (e.g., `EXHIBIT 1`, `EXHIBIT A`, `EXHIBIT 101`) onto PDF documents. It parses exhibit identifiers directly from PDF filenames, generates styled exhibit bounding boxes, and exports stamped PDFs into an output directory.

Includes both an intuitive **Desktop GUI** and a feature-rich **Command-Line Interface (CLI)**.

---

## Features

- **Automated Exhibit Numbering**: Automatically extracts digits or letters at the start of filenames (e.g., `1_Contract.pdf` -> `EXHIBIT 1`, `B_Deposition.pdf` -> `EXHIBIT B`).
- **Desktop GUI Application**: Built with Python's standard `tkinter` framework — no extra GUI framework installation required.
- **Flexible Stamp Placement**: Support for standard corner positions (`bottom-right`, `bottom-left`, `top-right`, `top-left`).
- **Color Customization**: Choose from preset text colors (`black`, `red`, `blue`, `navy`) or pick any custom Hex color (e.g., `#D32F2F`).
- **Single or Multi-Page Mode**: Stamp only the first page (default) or apply the exhibit stamp to all pages in every document.
- **Automated Test Suite**: Unit tests covering stamp creation, file parsing, and batch processing logic.

---

## File Naming Conventions

The tool automatically extracts the exhibit label from the **beginning of each PDF filename** (matching numbers or letters before spaces, underscores, or hyphens).

### Examples & Expected Outputs:

| Original Filename | Extracted Label | Printed Stamp Text | Generated Output Filename |
| :--- | :--- | :--- | :--- |
| `1_Contract.pdf` | `1` | **`EXHIBIT 1`** | `Exhibit_1_1_Contract.pdf` |
| `101_Deposition_Transcript.pdf` | `101` | **`EXHIBIT 101`** | `Exhibit_101_101_Deposition_Transcript.pdf` |
| `A_Bank_Statement.pdf` | `A` | **`EXHIBIT A`** | `Exhibit_A_A_Bank_Statement.pdf` |
| `EXB_Medical_Records.pdf` | `EXB` | **`EXHIBIT EXB`** | `Exhibit_EXB_EXB_Medical_Records.pdf` |
| `12A_Tax_Return.pdf` | `12A` | **`EXHIBIT 12A`** | `Exhibit_12A_12A_Tax_Return.pdf` |

> [!TIP]
> - Filenames **must start with alphanumeric characters** (numbers `0-9` or letters `A-Z`).
> - Files starting with symbols or underscores (e.g., `_notes.pdf` or `.document.pdf`) will be skipped automatically.

---


## Installation

### 1. Requirements
- Python 3.8+

### 2. Install Required Dependencies
Install the required PDF manipulation libraries via `pip`:

```powershell
pip install pypdf reportlab
```

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

#### GUI Controls:
1. **Browse...**: Select the folder containing your PDF exhibits.
2. **Stamp Position**: Select where to place the exhibit label on each page.
3. **Text Color**: Select a color preset or use the color picker for a custom Hex code.
4. **Apply to all pages**: Check to stamp every page (leave unchecked to stamp page 1 only).
5. **Stamp Exhibits**: Click to process all matching PDFs.
6. **Open Output Folder**: Open the `stamped_exhibits` directory in File Explorer when complete.

---

### Option B: Command-Line Interface (CLI)

Run `stamp.py` with command-line flags for automated or headless batch processing:

```powershell
# Basic usage (stamps all PDFs in current directory with default bottom-right black stamp)
python stamp.py

# Specify target directory
python stamp.py --dir "C:\Users\username\Documents\Exhibits"

# Customize position, color, and stamp all pages
python stamp.py --dir "./my_pdfs" --position top-right --color red --all-pages
```

#### CLI Options Reference:
| Flag | Description | Default |
| :--- | :--- | :--- |
| `--dir`, `-d` | Target folder containing PDFs to stamp | Current directory |
| `--position` | Position (`bottom-right`, `bottom-left`, `top-right`, `top-left`) | `bottom-right` |
| `--color` | Color name (`black`, `red`, `blue`, `navy`) or Hex code (e.g. `#FF0000`) | `black` |
| `--all-pages` | Apply stamp to every page in each PDF | `False` (Page 1 only) |
| `--gui` | Force launch the Graphical User Interface | `False` |

---

## Running Unit Tests

Run the automated test suite with Python's built-in `unittest` runner:

```powershell
python -m unittest test_stamp.py -v
```

---

## Repository Structure

```
exhibit_indexer/
├── stamp.py        # Core PDF processing logic and CLI handler
├── gui.py          # Tkinter desktop GUI application
├── test_stamp.py   # Unit test suite (unittest)
└── README.md       # Repository documentation
```
