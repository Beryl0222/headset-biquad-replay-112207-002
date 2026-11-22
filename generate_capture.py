"""生成双固件回放所需的长录音和现场事件。"""
import argparse
import json
from pathlib import Path
import struct


SAMPLE = struct.Struct('<h')


def generate(root, frames=480000, channels=8):
    """生成实际采样块和带帧号的交付记录。"""
    if frames < 4096 or channels not in (4, 8):
        raise ValueError('回放至少需要 4096 帧和四或八个声道')
    root.mkdir(parents=True, exist_ok=True)
    roles = ['ref-left', 'ref-right', 'out-left', 'out-right']
    if channels == 8:
        roles += ['aux-left', 'aux-right', 'side-left', 'side-right']
    triggers = (1601, 1860, 3073)
    for index, role in enumerate(roles):
        invalid = (1536, 1696) if role == 'ref-right' else (3046, 3080) if role == 'out-right' else ()
        with (root / (role + '.pcm')).open('wb') as raw:
            for frame in range(frames):
                sample = ((frame * (13 + 2 * index) + 7 * index) % 1021) - 510
                if any(0 <= frame - trigger < 8 for trigger in triggers):
                    sample = 511 if index % 2 else -511
                if invalid and invalid[0] <= frame < invalid[1]:
                    sample = 0
                raw.write(SAMPLE.pack(sample))
    channels_by_group = {'cancel': roles[:4], 'side': roles[4:]} if channels == 8 else {'cancel': roles[:4]}
    events = [
        {'type': 'switch', 'group': 'cancel', 'frame': 1601, 'version': 'b', 'proposal': 'trial'},
        {'type': 'data', 'group': 'cancel', 'frame': 1728},
        {'type': 'seal', 'group': 'cancel', 'frame': 1680, 'file': 'played-a'},
        {'type': 'silence', 'channel': 'ref-right', 'start': 1536, 'stop': 1696},
        {'type': 'switch', 'group': 'cancel', 'frame': 1860, 'version': 'b', 'proposal': 'release'},
        {'type': 'data', 'group': 'cancel', 'frame': 2496},
        {'type': 'seal', 'group': 'cancel', 'frame': 2176, 'file': 'played-b'},
        {'type': 'switch', 'group': 'cancel', 'frame': 3073, 'version': 'a', 'proposal': 'rollback'},
        {'type': 'data', 'group': 'cancel', 'frame': 3100},
        {'type': 'silence', 'channel': 'out-right', 'start': 3046, 'stop': 3080},
        {'type': 'reset', 'group': 'cancel', 'frame': 3200},
        {'type': 'data', 'group': 'cancel', 'frame': frames},
    ]
    if channels == 8:
        events[5:5] = [{'type': 'switch', 'group': 'side', 'frame': 1860, 'version': 'b', 'proposal': 'aux'},
                       {'type': 'data', 'group': 'side', 'frame': 2260},
                       {'type': 'seal', 'group': 'side', 'frame': 2130, 'file': 'aux-played'}]
        events.append({'type': 'data', 'group': 'side', 'frame': frames})
    value = {'channels': roles, 'groups': channels_by_group, 'frames': frames,
             'capture_unit': 0.001, 'sample_rate': 16000, 'initial_firmware': 'a',
             'blocks': [53, 197, 384], 'warmup': 128, 'overlap': 192, 'playback_window': 1024,
             'missing': {'ref-right': [[1536, 1696]], 'out-right': [[3046, 3080]]},
             'events': events}
    (root / 'capture.json').write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='生成多声道固件切换记录')
    parser.add_argument('directory', type=Path)
    parser.add_argument('--frames', type=int, default=480000)
    parser.add_argument('--channels', type=int, default=8)
    args = parser.parse_args()
    generate(args.directory, args.frames, args.channels)
