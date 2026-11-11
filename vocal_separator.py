# -*- coding: utf-8 -*-
"""
Vocal Separation via Demucs (torchaudio HDEMUCS)
動画・音声から BGM や SE を除去し、セリフ（ボーカル音声）のみを抽出
"""

import os
from typing import Optional


def separate_vocals(
    input_wav: str,
    output_vocal_wav: str,
    chunk_seconds: int = 30
) -> bool:
    """
    Demucs (HDEMUCS_HIGH_MUSDB_PLUS) を用いてセリフ（ボーカル）を分離する。
    PyTorch / torchaudio がインストールされていない場合はスキップ。
    """
    try:
        import torch
        import torchaudio
        from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS
        from pydub import AudioSegment
        import numpy as np
    except ImportError:
        print("[Notice] torchaudio / pydub is not installed. Skipping vocal separation.")
        return False

    device = "cuda" if torch.cuda.is_available() else "cpu"
    bundle = HDEMUCS_HIGH_MUSDB_PLUS
    model = bundle.get_model()
    model.to(device)

    # 音声の読み込み
    sound = AudioSegment.from_file(input_wav)
    samples = np.frombuffer(sound.raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    waveform = torch.from_numpy(samples).view(-1, sound.channels).t()

    ref_sr = bundle.sample_rate
    if sound.frame_rate != ref_sr:
        waveform = torchaudio.functional.resample(waveform, sound.frame_rate, ref_sr)

    # チャンクごとに処理してGPU/CPUメモリ枯渇を防止
    chunk_size = chunk_seconds * ref_sr
    num_frames = waveform.shape[1]
    vocal_chunks = []

    for i in range(0, num_frames, chunk_size):
        chunk = waveform[:, i:i+chunk_size]
        actual_len = chunk.shape[1]
        if actual_len < ref_sr:
            pad_len = ref_sr - actual_len
            chunk = torch.nn.functional.pad(chunk, (0, pad_len))

        chunk = chunk.to(device)
        with torch.no_grad():
            sources = model(chunk.unsqueeze(0))
            # 3: Vocals
            vocals_chunk = sources[0, 3].cpu()

        if actual_len < ref_sr:
            vocals_chunk = vocals_chunk[:, :actual_len]
        elif i + chunk_size > num_frames:
            vocals_chunk = vocals_chunk[:, :(num_frames - i)]

        vocal_chunks.append(vocals_chunk)

    vocals = torch.cat(vocal_chunks, dim=1)
    out_samples = (vocals.t().numpy() * 32767.0).astype(np.int16)
    out_sound = AudioSegment(
        out_samples.tobytes(),
        frame_rate=ref_sr,
        sample_width=2,
        channels=vocals.shape[0]
    )
    out_sound.export(output_vocal_wav, format="wav")
    return True
