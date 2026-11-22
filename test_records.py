"""核对本地设备资料的关联。"""
import unittest
from pathlib import Path
from records import load


class DeviceRecordsTest(unittest.TestCase):
    def test_设备资料关联(self):
        data = load(Path(__file__).with_name("device_records.json"))
        assert all(len(s) == 5 for sections in data['coefficients'].values() for s in sections)
        assert all(e[3] in data['firmware'] for e in data['events'] if e[0] == 'switch')

    def test_回放采样与事件引用(self):
        from tempfile import TemporaryDirectory
        from generate_capture import SAMPLE, generate

        with TemporaryDirectory() as directory:
            root = Path(directory)
            data = generate(root, frames=4096)
            for channel in data['channels']:
                self.assertEqual((root / (channel + '.pcm')).stat().st_size, 4096 * SAMPLE.size)
            self.assertLess(data['warmup'] + data['overlap'], data['playback_window'])
            for event in data['events']:
                if event['type'] == 'silence':
                    self.assertIn([event['start'], event['stop']], data['missing'][event['channel']])
                else:
                    self.assertIn(event['group'], data['groups'])
                    self.assertLessEqual(event['frame'], data['frames'])
