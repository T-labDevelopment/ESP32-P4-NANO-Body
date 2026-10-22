# ESP32-P4-NANO-Body

Waveshare ESP32-P4-NANO専用の3Dプリント筐体設計データ。

**現行設計: [Rev.D](rev-d/README.md)**（2026-10-23、開口の左右反転＋5mm拡張）  
**旧設計: [Rev.A](rev-a/README.md) / [Rev.B](rev-b/README.md) / [Rev.C](rev-c/README.md)**（履歴として保持）

USB-A・USB-C・RJ45の開口、底蓋からのM3ねじ4点締結、基板の上下挟み込み方式。Rev.Bでは外側へ飛び出さないねじ固定柱を採用し、薄肉の中空・長方形ケースとする。Bambu Lab A1 / PETGを想定。

**状態: 3D CAD試作 / 実機嵌合・コネクター挿抜・熱試験は未検証。**

## CADソースと印刷用データ

- `rev-d/generate_enclosure.py`: 現行の開口位置・寸法を定義するCADソース
- `rev-b/generate_enclosure.py`: 共通の機械構造を定義する継承元CADソース
- `rev-b/render_preview.py`: 外観・平面図プレビュー
- `rev-b/requirements.txt`: 固定した依存バージョン
- `rev-a/`: Rev.A設計と仕様の履歴
- `.github/workflows/generate-cad.yml`: CADモデルからSTL・STEPを再生成するワークフロー

生成時はPython環境とCadQueryの安定版を使用し、出力のSTL・STEPを検証する。現物嵌合の未検証事項は [Rev.D仕様書](rev-d/README.md) に記載。

## 登録元

本CADは当初 [WebTRX-Lanadapter](https://github.com/T-labDevelopment/WebTRX-Lanadapter/tree/main/hardware/enclosure/esp32-p4-nano) 内で開発し、筐体専用の本リポジトリへ独立登録した。既存リポジトリのコミット履歴はそのまま保管し、本リポジトリの履歴は移管時点から新規開始する。過去のソースへのリンクも残す。

## 実機試作時の重要な注意

Rev.Bの実物ではUSB-A/RJ45の共通開口が端子群に対して左側へずれている問題が確認された。**Rev.BのSTLを新規造形しないこと**。Rev.Cでも改善が確認できないため、現行候補を[Rev.D](rev-d/README.md)に更新。開口を左右反転し、広い壁面側へ5mm拡張した。最初に前面試験用2部品を印刷して確認する。Rev.Dも実物未検証であり、解決済みと扱わない。
