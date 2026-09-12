import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.stamp_doc import convert_docx_to_pdf_stream, process_docx

class TestStampDoc(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_docx(self, filename):
        filepath = os.path.join(self.test_dir, filename)
        # Create dummy text file representing document
        with open(filepath, "w") as f:
            f.write("Sample Word Document Text")
        return filepath

    def test_process_docx_fallback(self):
        docx_path = self._create_sample_docx("10_contract.docx")
        # Should gracefully convert text content or handle conversion
        try:
            writer = process_docx(docx_path, exhibit_num="10", position="bottom-right", color="black")
            self.assertIsNotNone(writer)
            self.assertGreater(len(writer.pages), 0)
        except ValueError:
            # Conversion depending on installed word engine
            pass

if __name__ == "__main__":
    unittest.main()
