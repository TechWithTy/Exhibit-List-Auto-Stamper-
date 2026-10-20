import os
import shutil
import tempfile
import unittest
import io
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app import stamp_files_in_dir, stamp_pdfs_in_dir
from app.common import create_exhibit_stamp

class TestExhibitIndexerIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_pdf(self, filename, num_pages=1):
        filepath = os.path.join(self.test_dir, filename)
        writer = PdfWriter()
        for i in range(num_pages):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(100, 700, f"Sample Document Page {i+1}")
            can.save()
            packet.seek(0)
            reader = PdfReader(packet)
            writer.add_page(reader.pages[0])

        with open(filepath, "wb") as f:
            writer.write(f)
        return filepath

    def test_stamp_pdfs_in_dir_success(self):
        self._create_sample_pdf("1_exhibit_one.pdf", num_pages=2)
        self._create_sample_pdf("B_exhibit_two.pdf", num_pages=1)
        self._create_sample_pdf("notes.txt")

        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=self.test_dir,
            position="top-right",
            color="red",
            all_pages=False,
            log_callback=logs.append
        )

        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(output_dir))

        stamped_files = os.listdir(output_dir)
        self.assertEqual(len(stamped_files), 2)
        self.assertIn("Exhibit_1_1_exhibit_one.pdf", stamped_files)
        self.assertIn("Exhibit_B_B_exhibit_two.pdf", stamped_files)

    def test_stamp_pdfs_in_nested_dirs_recursive(self):
        subfolder = os.path.join(self.test_dir, "Subfolder")
        os.makedirs(subfolder)
        sub_pdf = os.path.join(subfolder, "2_nested_doc.pdf")
        writer = PdfWriter()
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 700, "Nested doc")
        can.save()
        packet.seek(0)
        writer.add_page(PdfReader(packet).pages[0])
        with open(sub_pdf, "wb") as f:
            writer.write(f)

        self._create_sample_pdf("1_root_doc.pdf")

        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=self.test_dir,
            recursive=True,
            log_callback=logs.append
        )

        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "Exhibit_1_1_root_doc.pdf")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "Subfolder", "Exhibit_2_2_nested_doc.pdf")))

    def test_extract_exhibit_number_conventions(self):
        from app.common import extract_exhibit_number
        self.assertEqual(extract_exhibit_number("Exhibit_1_Contract.pdf"), "1")
        self.assertEqual(extract_exhibit_number("Exhibit_A_Bank_Statement.docx"), "A")
        self.assertEqual(extract_exhibit_number("exhibit_101_Deposition.pdf"), "101")
        self.assertEqual(extract_exhibit_number("EXHIBIT_12B_Tax_Return.pdf"), "12B")
        self.assertEqual(extract_exhibit_number("Exhibit-5-Photo.jpg"), "5")
        self.assertEqual(extract_exhibit_number("Exhibit 3 Document.pdf"), "3")
        self.assertEqual(extract_exhibit_number("1_Contract.pdf"), "1")
        self.assertEqual(extract_exhibit_number("B_Statement.pdf"), "B")

    def test_stamp_files_exhibit_x_convention(self):
        self._create_sample_pdf("Exhibit_1_Contract.pdf")
        self._create_sample_pdf("Exhibit_A_Statement.pdf")

        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=self.test_dir,
            log_callback=logs.append
        )

        self.assertEqual(count, 2)
        stamped_files = os.listdir(output_dir)
        self.assertIn("Exhibit_1_Contract.pdf", stamped_files)
        self.assertIn("Exhibit_A_Statement.pdf", stamped_files)

    def test_extract_folder_exhibit_number(self):
        from app.common import extract_folder_exhibit_number
        self.assertEqual(extract_folder_exhibit_number("Exhibit_25_Tyrique on 08.31.2026"), "25")
        self.assertEqual(extract_folder_exhibit_number("Exhibit 10 - Police Report"), "10")
        self.assertEqual(extract_folder_exhibit_number("Exhibit_A_Financials"), "A")
        self.assertEqual(extract_folder_exhibit_number("5_Scene Photos"), "5")
        self.assertEqual(extract_folder_exhibit_number("B_Bank Statements"), "B")
        self.assertIsNone(extract_folder_exhibit_number("General Evidence"))
        self.assertIsNone(extract_folder_exhibit_number("."))

    def test_nested_folder_inherits_folder_exhibit_number(self):
        folder_name = "Exhibit_25_Tyrique on 08.31.2026"
        nested_dir = os.path.join(self.test_dir, folder_name)
        os.makedirs(nested_dir)

        # Create files without explicit exhibit numbers in their filenames
        for fname in ["Tyrique on 08.31.2026.pdf", "receipt.pdf"]:
            filepath = os.path.join(nested_dir, fname)
            writer = PdfWriter()
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(100, 700, f"Sample {fname}")
            can.save()
            packet.seek(0)
            writer.add_page(PdfReader(packet).pages[0])
            with open(filepath, "wb") as f:
                writer.write(f)

        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=self.test_dir,
            recursive=True,
            log_callback=logs.append
        )

        self.assertEqual(count, 2)
        # Verify all logs stamped with EXHIBIT 25
        self.assertTrue(any("-> EXHIBIT 25" in line for line in logs))
        out_subfolder = os.path.join(output_dir, folder_name)
        self.assertTrue(os.path.exists(out_subfolder))
        out_files = os.listdir(out_subfolder)
        self.assertIn("Exhibit_25_Tyrique on 08.31.2026.pdf", out_files)
        self.assertIn("Exhibit_25_receipt.pdf", out_files)

    def test_stamp_pdfs_in_dir_nonexistent(self):
        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=os.path.join(self.test_dir, "invalid"),
            log_callback=logs.append
        )
        self.assertEqual(count, 0)
        self.assertIsNone(output_dir)

if __name__ == "__main__":
    unittest.main()
