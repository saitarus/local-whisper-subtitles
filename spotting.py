# -*- coding: utf-8 -*-
"""
Subtitle Spotting & Frame Alignment Module
放送・映像業界の字幕ガイドライン（23.976fps/24fps/29.97fps対応）に準拠した
タイムコード補正およびシーンチェンジ（カット替わり）跨ぎ防止アルゴリズム
"""

from typing import List, Dict, Any


def format_ass_time(seconds: float) -> str:
    """ASS形式のタイムスタンプ (H:MM:SS.cs) に変換"""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    cs = int(round((s - int(s)) * 100))
    if cs == 100:
        cs = 99
    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"


def format_srt_time(seconds: float) -> str:
    """SRT形式のタイムスタンプ (HH:MM:SS,mmm) に変換"""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def adjust_timestamps_with_scenes(
    segments: List[Dict[str, Any]],
    scene_cuts: List[float],
    fps: float = 23.976,
    lead_frames: float = 1.5,
    lag_frames: float = 8.0,
    cut_guard_frames: float = 2.0
) -> List[Dict[str, Any]]:
    """
    シーンチェンジ（カット替わり）を考慮して字幕の開始・終了時刻を微調整する。

    :param segments: [{'start': float, 'end': float, 'text': str}]
    :param scene_cuts: カット替わりの秒数リスト [1.25, 4.80, ...]
    :param fps: フレームレート (デフォルト: 23.976 fps)
    :param lead_frames: 音声開始前の先行表示フレーム数 (1.5フレーム ≒ 約62.5ms)
    :param lag_frames: 音声終了後の余韻表示フレーム数 (8フレーム ≒ 約333ms)
    :param cut_guard_frames: カット替わり前後の進入防止フレーム数 (2フレーム ≒ 約83ms)
    """
    frame_dur = 1.0 / fps
    lead_sec = lead_frames * frame_dur
    lag_sec = lag_frames * frame_dur
    guard_sec = cut_guard_frames * frame_dur
    transition_threshold = 5.0 * frame_dur

    adjusted: List[Dict[str, Any]] = []

    for seg in segments:
        start = float(seg['start'])
        end = float(seg['end'])
        text = str(seg.get('text', '')).strip()

        adj_start = max(0.0, start - lead_sec)
        adj_end = end + lag_sec

        for cut in scene_cuts:
            # 1. 音声がカット変わり手前にあり、余韻でカットを跨ぐ場合はカット前で終了
            if start < cut and adj_end > cut - guard_sec:
                adj_end = max(adj_start + (frame_dur * 4), cut - guard_sec)

            # 2. カット変わり前5フレーム以内に音声の始まりがある場合
            if cut - transition_threshold <= start < cut:
                adj_start = cut + (3.0 * frame_dur)

            # 3. カット変わり後5フレーム以内に音声の終わりがある場合
            if cut < end <= cut + transition_threshold:
                adj_end = cut - (3.0 * frame_dur)

            # 4. カット切り替え前後のガードフレーム進入防止
            if cut - guard_sec <= adj_start <= cut + guard_sec:
                adj_start = cut - guard_sec if adj_start < cut else cut + guard_sec

            if cut - guard_sec <= adj_end <= cut + guard_sec:
                adj_end = cut - guard_sec if adj_end < cut else cut + guard_sec

        if adj_end < adj_start:
            adj_end = adj_start + (frame_dur * 6)  # 最低表示時間保証

        adjusted.append({
            'start': adj_start,
            'end': adj_end,
            'text': text,
            'start_ass': format_ass_time(adj_start),
            'end_ass': format_ass_time(adj_end),
            'start_srt': format_srt_time(adj_start),
            'end_srt': format_srt_time(adj_end)
        })

    return adjusted
