# Local Whisper Subtitles 🎬

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/saitarus/local-whisper-subtitles/actions/workflows/ci.yml/badge.svg)](https://github.com/saitarus/local-whisper-subtitles/actions)
[![Subtitle: Broadcast Standard](https://img.shields.io/badge/Subtitles-Broadcast%20Standard-orange.svg)](spotting.py)

**放送・映像ガイドライン準拠のフレーム補正＆シーンチェンジ跨ぎ防止を備えた、高精度 AI 字幕生成 CLI**

A professional AI-powered video subtitle generation toolkit combining Demucs (vocal separation), Whisper (speech recognition), and frame-accurate scene cut alignment.

---

## 🌟 主な特徴 (Features)

1. **放送・映像業界水準のタイムスタンプ補正 (Broadcast Standard Spotting)**
   - 23.976 / 24 / 29.97 fps などのフレームレートに基づき、音声起点・終点の先行／余韻表示（先行1.5フレーム、余韻8フレーム等）を自動計算。
   - カット替わり（シーンチェンジ）を跨ぐ不自然な字幕表示を防ぐガードフレーム進入防止ロジックを搭載。
2. **音源分離による認識精度向上 (Demucs Vocal Separation)**
   - BGM や効果音（SE）が混在する動画から、AI 音源分離（Demucs）を用いてセリフ（ボーカル成分）のみを抽出。
   - 騒音や激しい劇伴のある映像でも誤認識を劇的に低減。
3. **FFmpeg によるシーンチェンジ自動検出**
   - 動画のカット切り替えポイントをフレーム単位で自動検出し、字幕の表示タイミングをカット境界にスナップ。
4. **マルチフォーマット出力**
   - 汎用性の高い **SRT** 形式
   - スタイル装飾・フォント指定が可能な **ASS** (Advanced SubStation Alpha) 形式

---

## 📁 ディレクトリ構成 (Architecture)

```text
local-whisper-subtitles/
├── tests/
│   └── test_spotting.py       # タイムコード計算・シーンガード単体テスト
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI
├── spotting.py                # 放送基準タイムコード補正＆カット跨ぎ防止ロジック
├── scene_detector.py          # FFmpeg シーンチェンジ自動検出
├── vocal_separator.py         # Demucs 音源分離（ボーカル抽出）
├── cli.py                     # 統合 CLI エントリーポイント
├── requirements.txt           # 依存パッケージ
├── .gitignore                 # メディア・成果物除外設定
├── LICENSE                    # MIT ライセンス
└── README.md                  # 本ドキュメント
```

---

## 🚀 クイックスタート (Quick Start)

### 1. 必要要件 (Prerequisites)

- Python 3.10+
- FFmpeg (システム PATH に通っていること)

### 2. インストール

```bash
git clone https://github.com/saitarus/local-whisper-subtitles.git
cd local-whisper-subtitles
pip install -r requirements.txt
```

※ GPU を活用した完全な Whisper / Demucs パイプラインを実行する場合は、PyTorch および stable-ts をインストールしてください：
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install stable-ts pydub
```

### 3. 字幕生成の実行

```bash
# 動画からシーン検出・文字起こし・SRT/ASS字幕生成
python cli.py sample_video.mp4 --model small --fps 23.976 --outdir ./output
```

---

## 📐 字幕スポッティングのアルゴリズム (Spotting Logic)

- **先行表示 (Lead-in)**: 音声開始から 1.5 フレーム前（約 62.5ms）から字幕を表示開始し、人間の認知遅延に対応。
- **余韻表示 (Lag-out)**: 音声終了後 8 フレーム（約 333ms）余韻を残してフェードアウト。
- **シーンガード (Scene Guard)**: カット切り替え前後の 2 フレーム（約 83ms）以内の進入を防止し、画面切り替え時のチラつきを抑制。

---

## 📄 ライセンス (License)

本プロジェクトは [MIT License](LICENSE) のもとで公開されています。
