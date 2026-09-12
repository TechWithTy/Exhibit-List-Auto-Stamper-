import os
import shutil
import tempfile
import unittest
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from stamp import create_exhibit_stamp, stamp_pdfs_in_dir

class TestExhibitIndexer(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary directory after tests
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_pdf(self, filename, num_pages=1):
        """Helper method to generate a simple PDF file for testing."""
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

    def test_create_exhibit_stamp_valid(self):
        """Test that create_exhibit_stamp returns a valid PDF PageObject for all positions."""
        positions = ["top-right", "top-left", "bottom-left", "bottom-right"]
        for pos in positions:
            page = create_exhibit_stamp(exhibit_num="1", position=pos, color_hex="#000000")
            self.assertIsNotNone(page)
            self.assertGreater(page.mediabox.width, 0)
            self.assertGreater(page.mediabox.height, 0)

    def test_stamp_pdfs_in_dir_success(self):
        """Test stamping multiple valid PDFs in a directory."""
        self._create_sample_pdf("1_exhibit_one.pdf", num_pages=2)
        self._create_sample_pdf("B_exhibit_two.pdf", num_pages=1)
        self._create_sample_pdf("notes.txt")  # Non-PDF file, should be ignored

        logs = []
        count, output_dir = stamp_pdfs_in_dir(
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

        # Verify page count of stamped PDF
        reader = PdfReader(os.path.join(output_dir, "Exhibit_1_1_exhibit_one.pdf"))
        self.assertEqual(len(reader.pages), 2)

    def test_stamp_pdfs_in_dir_all_pages(self):
        """Test stamping all pages in a multi-page PDF."""
        self._create_sample_pdf("101_multi.pdf", num_pages=3)

        count, output_dir = stamp_pdfs_in_dir(
            input_dir=self.test_dir,
            position="bottom-left",
            color="blue",
            all_pages=True
        )

        self.assertEqual(count, 1)
        stamped_path = os.path.join(output_dir, "Exhibit_101_101_multi.pdf")
        self.assertTrue(os.path.exists(stamped_path))
        reader = PdfReader(stamped_path)
        self.assertEqual(len(reader.pages), 3)

    def test_stamp_pdfs_in_dir_nonexistent_directory(self):
        """Test behavior when passing a non-existent directory path."""
        logs = []
        count, output_dir = stamp_pdfs_in_dir(
            input_dir=os.path.join(self.test_dir, "non_existent_folder"),
            log_callback=logs.append
        )
        self.assertEqual(count, 0)
        self.assertIsNone(output_dir)
        self.assertTrue(any("does not exist" in log for log in logs))

    def test_stamp_pdfs_in_dir_empty_directory(self):
        """Test behavior when directory contains no PDF files."""
        logs = []
        count, output_dir = stamp_pdfs_in_dir(
            input_dir=self.test_dir,
            log_callback=logs.append
        )
        self.assertEqual(count, 0)
        self.assertIsNotNone(output_dir)
        self.assertTrue(any("No PDF files found" in log for log in logs))

    def test_stamp_pdfs_in_dir_invalid_filename_prefix(self):
        """Test skipping files that do not start with alphanumeric exhibit identifiers."""
        self._create_sample_pdf("_invalid_name.pdf")
        logs = []
        count, output_dir = stamp_pdfs_in_dir(
            input_dir=self.test_dir,
            log_callback=logs.append
        )
        self.assertEqual(count, 0)
        self.assertTrue(any("Skipped" in log for log in logs))

if __name__ == "__main__":
    unittest.main()
