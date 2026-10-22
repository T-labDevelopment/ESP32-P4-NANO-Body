# Rev.A — 初期試作設計

本ディレクトリは初期設計Rev.Aの記録です。**最新設計は [Rev.B](../rev-b/README.md)** です。

- 基板：Waveshare ESP32-P4-NANO（公称50×50mm）
- 外形：側壁矩形58.8×58.8mm、四隅のねじ耳を含む最大70.6×70.6mm、高さ27.6mm
- USB-AとRJ45を共通開口、USB-Cを反対面に独立開口
- 上下分割、底蓋をM3低頭ネジ4本で固定、基板を上下面から4点保持
- PETG、Bambu Lab A1向け。実機嵌合、プラグ挿抜、熱は未検証
- **Rev.Aは外部へ張り出すネジ耳を持つため、Rev.Bで廃止**

## CAD生成

```sh
python -m pip install -r requirements.txt
python generate_enclosure.py
```

生成されるSTEP/STLはCADソースから再現できます。ピン径・インサート穴径・開口寸法は試作値です。

最初の設計資料：[元プロジェクトのRev.A](https://github.com/T-labDevelopment/WebTRX-Lanadapter/tree/main/hardware/enclosure/esp32-p4-nano)

資料：[Waveshare公式 ESP32-P4-NANO](https://docs.waveshare.com/ESP32-P4-NANO)
