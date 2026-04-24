# Pixel Action

Python + [Pyxel](https://github.com/kitao/pyxel) でつくる見下ろし型ドット絵アクションゲーム。192×128 / 60fps / 16色。

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 起動

```powershell
python main.py
```

初回起動時に `assets.pyxres` が自動生成される（スプライト・タイルマップ・SFX/BGM を Python 側から書き出し）。以降はそのファイルをロードする。`pyxel edit assets.pyxres` で後からドット絵やサウンドを差し替え可能。

## 操作

| 操作 | キー |
|------|------|
| 移動 | 矢印キー / WASD |
| 攻撃 | Z |
| 決定 | Space / Enter |
| ポーズ / 戻る | Esc |
| 終了 | Q（Pyxel 既定） |

## ゲーム内容

- **2 ステージ構成** — ステージ端のドアを通ると隣のステージへ遷移。HP とスコアを引き継ぐ。
- **敵（スライム）** — 一定距離内でプレイヤーを追跡。接触で 1 ダメージ。攻撃で撃破 +100 スコア。
- **プレイヤー** — HP 3 / 被弾で短時間無敵（点滅）/ 近接攻撃は前方にヒットボックスを展開。
- **カメラ追従** — プレイヤー中心でワールド境界にクランプ。敵撃破時は画面シェイク。
- **HUD** — ステージ番号・スコア・HP ハート。
- **ポーズ / ゲームオーバー** — Esc でポーズメニュー（RESUME / TITLE）。HP 0 でゲームオーバー画面（RETRY / TITLE）。
- **効果音 / BGM** — タイトル以外で BGM ループ。攻撃・被弾・撃破・決定に SFX。

## アーキテクチャ

詳細は [CLAUDE.md](./CLAUDE.md) を参照。要点:

- **シーンスタック** (`game/scene.py`) — `Title` / `Play` / `Pause`（透過オーバーレイ）/ `GameOver` を保留キュー付きで遷移
- **入力抽象化** (`game/input_handler.py`) — アクション名 → キー定数の辞書 (`config.KEYBINDS`) 経由でクエリ
- **ワールドと衝突** (`game/world.py` / `game/player.py`) — `pyxel.tilemaps` ベースのタイル衝突 + 軸分離 AABB
- **ステージとカメラ** (`game/stage.py` / `game/camera.py`) — シード再現可能なマップ生成、ワールド境界クランプ
- **アセット** (`game/assets.py`) — `.pyxres` の自動生成・再生成判定（stale 検出）

## 開発コマンド

```powershell
python -m compileall -q game main.py     # 構文チェック（Pyxel 不要）
python -c "from game.app import Game"    # インポートグラフの健全性チェック
```

テスト・Lint・CI は未導入。衝突ロジックなどヘッドレス検証したい処理は `pyxel.init` を呼ばないモジュール (`World` に `tilemap` を DI / `Player._move_axis` / `InputHandler` / `Camera` / `Stage` / `Particle`) を `python -c` から叩く。
