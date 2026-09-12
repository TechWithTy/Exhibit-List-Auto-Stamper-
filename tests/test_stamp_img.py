import io
import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportlab.pdfgen import canvas
from app.stamp_img import process_image, convert_image_to_pdf_stream

class TestStampImage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_image(self, filename):
        filepath = os.path.join(self.test_dir, filename)
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(300, 300))
        can.setFillColorRGB(0.1, 0.5, 0.9)
        can.rect(0, 0, 300, 300, fill=1)
        can.save()
        with open(filepath, "wb") as f:
            f.write(packet.getvalue())
        return filepath

    def test_convert_image_to_pdf_stream(self):
        img_path = self._create_sample_image("1_photo.png")
        stream = convert_image_to_pdf_stream(img_path)
        self.assertIsNotNone(stream)
        self.assertGreater(len(stream.getvalue()), 0)

    def test_process_image(self):
        img_path = self._create_sample_image("A_evidence.jpg")
        writer = process_image(img_path, exhibit_num="A", position="top-left", color="blue")
        self.assertIsNotNone(writer)
        self.assertEqual(len(writer.pages), 1)

if __name__ == "__main__":
    unittest.main()
