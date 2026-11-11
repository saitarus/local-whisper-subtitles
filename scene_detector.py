# -*- coding: utf-8 -*-
"""
Scene Change Detection via FFmpeg
動画のカット替わり（シーン切り替え）タイミングをフレーム単位で自動検出
"""

import subprocess
from typing import List


def detect_scene_changes(video_path: str, threshold: float = 0.3) -> List[float]:
    """
    FFmpeg の select='gt(scene,threshold)' フィルタを用いてシーンチェンジ秒数を検出する。

    :param video_path: 入力動画ファイルパス
    :param threshold: シーンチェンジ検出感度 (0.0〜1.0、デフォルト 0.3)
    :return: シーンチェンジ発生秒数の昇順リスト
    """
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-filter_complex", f"select='gt(scene,{threshold})',metadata=print",
        "-f", "null", "-"
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True
        )
    except FileNotFoundError:
        print("[Warning] FFmpeg is not installed or not in PATH. Skipping scene detection.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"[Warning] FFmpeg execution failed: {e}")
        return []

    scenes: List[float] = []
    for line in result.stderr.splitlines():
        if "pts_time:" in line:
            parts = line.split("pts_time:")
            if len(parts) > 1:
                val = parts[1].split()[0]
                try:
                    scenes.append(round(float(val), 4))
                except ValueError:
                    pass

    return sorted(list(set(scenes)))
