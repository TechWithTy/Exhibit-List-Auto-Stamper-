import os
import threading
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from app import stamp_files_in_dir as stamp_pdfs_in_dir

class ExhibitIndexerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Exhibit Indexer - PDF Stamping Tool")
        self.root.geometry("640x560")
        self.root.minsize(580, 500)

        # Apply a clean TTK Theme
        self.style = ttk.Style()
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        elif "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title / Description Header
        header_label = ttk.Label(
            main_frame,
            text="Exhibit Indexer & PDF Stamper",
            font=("Segoe UI", 16, "bold")
        )
        header_label.pack(anchor=tk.W, pady=(0, 2))

        subtitle_label = ttk.Label(
            main_frame,
            text="Automatically stamp exhibit labels onto numbered/lettered PDFs, Word Docs, Images, and Videos.",
            font=("Segoe UI", 9),
            foreground="#555555"
        )
        subtitle_label.pack(anchor=tk.W, pady=(0, 15))

        # 1. Directory Selection Group
        dir_frame = ttk.LabelFrame(main_frame, text=" Select Document Directory (PDFs, DOCX, Images, Videos) ", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 12))

        self.dir_var = tk.StringVar(value=os.getcwd())
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, font=("Segoe UI", 9))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)

        # 2. Options Group
        options_frame = ttk.LabelFrame(main_frame, text=" Stamp Settings ", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 12))

        # Grid configuration
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)

        # Row 0: Position & Color Presets
        ttk.Label(options_frame, text="Stamp Position:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.pos_var = tk.StringVar(value="bottom-right")
        pos_combo = ttk.Combobox(
            options_frame,
            textvariable=self.pos_var,
            values=["bottom-right", "bottom-left", "top-right", "top-left"],
            state="readonly"
        )
        pos_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(options_frame, text="Text Color:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.color_var = tk.StringVar(value="black")
        color_combo = ttk.Combobox(
            options_frame,
            textvariable=self.color_var,
            values=["black", "red", "blue", "navy", "custom"],
            state="readonly"
        )
        color_combo.grid(row=0, column=3, sticky=tk.EW, pady=5)
        color_combo.bind("<<ComboboxSelected>>", self.on_color_change)

        # Row 1: Custom Hex Input & Color Picker
        self.hex_label = ttk.Label(options_frame, text="Hex Color Code:")
        self.hex_var = tk.StringVar(value="#000000")
        self.hex_entry = ttk.Entry(options_frame, textvariable=self.hex_var, width=12)
        self.picker_btn = ttk.Button(options_frame, text="Pick Color", command=self.pick_color)

        # Initially hidden unless custom color chosen
        self.toggle_custom_color_widgets(False)

        # Row 2: Options / Checkboxes
        self.all_pages_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Apply stamp to all pages", variable=self.all_pages_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include nested subfolders", variable=self.recursive_var).grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))

        # 3. Execution Control & Progress
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.run_btn = ttk.Button(control_frame, text="⚡ Stamp Exhibits", command=self.start_stamping)
        self.run_btn.pack(side=tk.LEFT, ipadx=10, ipady=4)

        self.open_folder_btn = ttk.Button(control_frame, text="📁 Open Output Folder", command=self.open_output_folder, state=tk.DISABLED)
        self.open_folder_btn.pack(side=tk.RIGHT)

        self.last_output_dir = None

        # 4. Activity Log Display
        log_frame = ttk.LabelFrame(main_frame, text=" Activity Log ", padding="8")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#F9F9F9", fg="#222222", height=10)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log("Ready. Select a PDF folder and click 'Stamp Exhibits' to start.")

    def browse_directory(self):
        folder = filedialog.askdirectory(initialdir=self.dir_var.get())
        if folder:
            self.dir_var.set(folder)

    def on_color_change(self, event=None):
        choice = self.color_var.get()
        if choice == "custom":
            self.toggle_custom_color_widgets(True)
        else:
            self.toggle_custom_color_widgets(False)

    def toggle_custom_color_widgets(self, show):
        if show:
            self.hex_label.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(0, 5))
            self.hex_entry.grid(row=1, column=3, sticky=tk.W, pady=5)
            self.picker_btn.grid(row=1, column=3, sticky=tk.E, pady=5)
        else:
            self.hex_label.grid_remove()
            self.hex_entry.grid_remove()
            self.picker_btn.grid_remove()

    def pick_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color", initialcolor=self.hex_var.get())
        if color_code and color_code[1]:
            self.hex_var.set(color_code[1])

    def log(self, message):
        self.root.after(0, self._append_log, message)

    def _append_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_stamping(self):
        target_dir = self.dir_var.get().strip()
        if not target_dir or not os.path.isdir(target_dir):
            messagebox.showerror("Error", "Please select a valid directory containing PDF files.")
            return

        color_choice = self.color_var.get()
        color = self.hex_var.get().strip() if color_choice == "custom" else color_choice
        position = self.pos_var.get()
        all_pages = self.all_pages_var.get()
        recursive = self.recursive_var.get()

        self.run_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.log(f"Starting exhibit stamping process...")
        self.log(f"Directory: {target_dir}")
        self.log(f"Position: {position} | Color: {color} | All Pages: {all_pages} | Recursive: {recursive}")
        self.log("-" * 55)

        # Run stamping in a separate thread so GUI doesn't freeze
        threading.Thread(
            target=self._run_stamping_thread,
            args=(target_dir, position, color, all_pages, recursive),
            daemon=True
        ).start()

    def _run_stamping_thread(self, target_dir, position, color, all_pages, recursive):
        try:
            count, output_dir = stamp_pdfs_in_dir(
                input_dir=target_dir,
                position=position,
                color=color,
                all_pages=all_pages,
                recursive=recursive,
                log_callback=self.log
            )
            self.last_output_dir = output_dir
            if count > 0 and output_dir and os.path.exists(output_dir):
                self.root.after(0, lambda: self.open_folder_btn.config(state=tk.NORMAL))
                messagebox.showinfo("Success", f"Successfully stamped {count} exhibit PDF(s)!\nSaved in:\n{output_dir}")
            elif count == 0:
                messagebox.showwarning("Warning", "No matching PDF files were stamped.")
        except Exception as e:
            self.log(f"Fatal Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while stamping: {str(e)}")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))

    def open_output_folder(self):
        if self.last_output_dir and os.path.exists(self.last_output_dir):
            if sys.platform == "win32":
                os.startfile(self.last_output_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_output_dir])
            else:
                subprocess.Popen(["xdg-open", self.last_output_dir])

def launch_gui():
    root = tk.Tk()
    app = ExhibitIndexerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
