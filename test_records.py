"""核对本地设备资料的关联。"""
import unittest
from pathlib import Path
from records import load


class DeviceRecordsTest(unittest.TestCase):
    def test_设备资料关联(self):
        data = load(Path(__file__).with_name("device_records.json"))
        assert all(len(s) == 5 for sections in data['coefficients'].values() for s in sections)
        assert all(e[3] in data['firmware'] for e in data['events'] if e[0] == 'switch')
