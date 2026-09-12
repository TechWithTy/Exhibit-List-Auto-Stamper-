import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.stamp_video import process_video, create_video_cover_pdf_stream

class TestStampVideo(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_dummy_video(self, filename):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "wb") as f:
            f.write(b"0" * 1024 * 50)  # Dummy binary data (50KB)
        return filepath

    def test_create_video_cover_pdf_stream(self):
        video_path = self._create_dummy_video("1_surveillance.mp4")
        stream = create_video_cover_pdf_stream(video_path, exhibit_num="1")
        self.assertIsNotNone(stream)
        self.assertGreater(len(stream.getvalue()), 0)

    def test_process_video(self):
        video_path = self._create_dummy_video("101_dashcam.mov")
        writer = process_video(video_path, exhibit_num="101", position="bottom-right", color="navy")
        self.assertIsNotNone(writer)
        self.assertEqual(len(writer.pages), 1)

if __name__ == "__main__":
    unittest.main()
