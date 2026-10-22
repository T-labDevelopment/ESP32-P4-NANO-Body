# ESP32-P4-NANO筐体 Rev.D（2026-10-23）

**現行のRJ45/USB-A共通開口修正候補。実物の嵌合は未検証。**
既存Rev.A～Rev.Cは履歴として保存し、変更しない。

## ユーザー指定の変更内容

RJ45/USB-A側の共通開口（+Y面）の左右の余白配置をRev.Cから反転し、**反転後の広い側の壁に向けて5.0mm開口を拡張**する。
筐体の天面を上に、外側から+Y面を見る（CADの+Xが正面視左、-Xが右）。

| 項目 | Rev.C | 左右反転時点 | Rev.D |
|---|---:|---:|---:|
| 開口CAD X0 | -23.0mm | -1.8mm | **-6.8mm** |
| 開口CAD X1 | +1.8mm | +23.0mm | **+23.0mm** |
| 開口幅 | 24.8mm | 24.8mm | **29.8mm** |
| 正面視左の残り壁幅 | 35.2mm | 14.0mm | **14.0mm** |
| 正面視右の残り壁幅 | 14.0mm | 35.2mm | **30.2mm** |

残り壁幅は74.0mmの矩形外形を基準とする水平距離であり、角丸部分やネジ柱の局所的な肉厚は含まない。

**変更しない部分**：外形74×62×31.5mm、一般側壁2mm、USB-A/RJ45側壁厚1.8mm、天面2.8mm、底蓋3.2mm、四隅4点M3固定、基板上下挟み込み、反対面のUSB-C開口、PETG/Bambu Lab A1の造形前提、前面開口の上下位置。

## 設計・検証

- CadQuery 2.8.0を使用し、`../rev-b/generate_enclosure.py` の安定した機械構造を読み込んで、開口位置・幅のみを上書きする。
- Rev.Cの写真から推定したUSB-A/RJ45端子直方体は正確な端子位置を示さないため、Rev.Dの組立モデルから取り除いた。基板そのものは回転・反転させない。
- スクリプトで幅29.8mm、左右余白14.0/30.2mm、前側ネジボスの水平位置との非重複を検査する。
- 最初に `ESP32_P4_NANO_RevD_front_coupon_upper.stl` と `ESP32_P4_NANO_RevD_front_coupon_bottom.stl` を印刷し、実際のUSB-A/RJ45位置、プラグ挿入深さ、RJ45ラッチ解除・端子との干渉を検証する。
- 現物で未確認のため、**問題が解消済みとは表記しない**。

## 再生成

```sh
python -m pip install -r rev-d/requirements.txt
python rev-d/generate_enclosure.py
```

生成されるSTL/STEPはGitHub ActionsによりGit管理する。
メーカー基板資料：https://docs.waveshare.com/ESP32-P4-NANO
