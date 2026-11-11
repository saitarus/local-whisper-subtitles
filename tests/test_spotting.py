import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pytest
from spotting import format_ass_time, format_srt_time, adjust_timestamps_with_scenes


def test_format_ass_time():
    assert format_ass_time(0.0) == "0:00:00.00"
    assert format_ass_time(65.5) == "0:01:05.50"
    assert format_ass_time(3661.12) == "1:01:01.12"


def test_format_srt_time():
    assert format_srt_time(0.0) == "00:00:00,000"
    assert format_srt_time(65.5) == "00:01:05,500"
    assert format_srt_time(3661.123) == "01:01:01,123"


def test_adjust_timestamps_basic():
    segments = [
        {'start': 2.0, 'end': 5.0, 'text': 'テスト音声'}
    ]
    scene_cuts = []  # シーンチェンジなし
    fps = 24.0

    adjusted = adjust_timestamps_with_scenes(segments, scene_cuts, fps=fps)
    assert len(adjusted) == 1
    # 1.5フレーム前 (1.5/24 = 0.0625s) 先行開始
    assert adjusted[0]['start'] < 2.0
    # 8フレーム後 (8/24 = 0.3333s) 余韻終了
    assert adjusted[0]['end'] > 5.0
    assert adjusted[0]['text'] == 'テスト音声'


def test_adjust_timestamps_scene_guard():
    # シーンチェンジが 4.9 秒にある場合、終了時刻がカット替わりを跨がないようにガードされるか
    segments = [
        {'start': 2.0, 'end': 4.8, 'text': 'カット前のセリフ'}
    ]
    scene_cuts = [4.9]
    fps = 24.0

    adjusted = adjust_timestamps_with_scenes(segments, scene_cuts, fps=fps)
    # ガードフレーム（2フレーム = 2/24 ≒ 0.083s）により、4.9 - 0.083 = 4.817 以下に抑えられること
    assert adjusted[0]['end'] <= 4.9
