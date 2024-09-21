import unittest
import os
import tempfile
from pybluetooth import hello_world, generate_music, play_audio
from pybluetooth.cli import main
from unittest.mock import patch
import sys

class TestPyBluetooth(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(hello_world(), "Hello, Bluetooth and Audio World!")

    def test_generate_and_play_music(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            generate_music(temp_filename)
            self.assertTrue(os.path.exists(temp_filename))
            self.assertGreater(os.path.getsize(temp_filename), 0)

            # 注意：这个测试不会实际播放音频，因为那需要音频设备
            # 我们只是确保函数不会抛出异常
            play_audio(temp_filename)
        finally:
            os.unlink(temp_filename)

    @patch('sys.argv', ['btool', '-s'])
    @patch('pybluetooth.cli.ble_scan')
    def test_btool_scan(self, mock_ble_scan):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 0)
        mock_ble_scan.assert_called_once()

if __name__ == '__main__':
    unittest.main()
