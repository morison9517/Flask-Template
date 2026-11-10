# =============================================================================
# assets.py = CSS・JS・画像のURLに「版の印」を付ける仕掛け
#
#     url_for('static', filename='css/style.css')
#         →  /static/css/style.css?v=3f9a2c1b
#
#   ▼ 何のためのものか
#
#     ブラウザは一度読んだCSSやJSを手元に取っておき、次からはサーバーに聞かずに
#     それを使う(本番では30日間)。速くなる代わりに、直して出し直しても
#     利用者の画面は古いままになる。
#     そこでURLの後ろにファイルの中身から作った印を付ける。中身が変われば印が変わり、
#     ブラウザは「別のファイルだ」と判断して取り直す。変わらなければ手元の分を使い続ける。
#
#   ▼ 使い方
#
#     HTMLではいつも通り url_for('static', filename='...') と書くだけ。印は自動で付く。
#
#     ★"/static/..." と直接書いても表示はされるが、印が付かないので
#       直したのに古いまま、が起きる。
#     ★CSSの中の url(...) で読む画像には印が付かない。差し替えるときはファイル名を変える。
#
#   ▼ 消したいとき
#
#     このファイルを消し、app.py の _register_assets(app) の1行を消す。
# =============================================================================
import hashlib
from pathlib import Path

from flask import Flask

# 一度作った印を覚えておく棚(ファイル名 → 印)。
_versions: dict[str, str] = {}


def register_asset_version(app: Flask) -> None:
    """url_for('static', ...) が作るURLに、版の印を自動で足す。"""

    # url_defaults = 「url_for がURLを作る直前に、毎回呼んでほしい関数」の登録。
    @app.url_defaults
    def add_version(endpoint: str, values: dict) -> None:
        # CSS・JS・画像のURL以外には何もしない。
        if endpoint != "static" or "filename" not in values:
            return

        version = _version(app, values["filename"])

        # ★ファイルが無いときは印を付けずに通す(エラーにしない)。
        #   そのファイルだけ404になり、ブラウザの開発者ツールで気づける。
        if version:
            values.setdefault("v", version)


def _version(app: Flask, filename: str) -> str:
    """ファイルの中身から8文字の印を作る。"""
    # ★本番では1回作ったら使い回す(ファイルは出し直すまで変わらないため)。
    #   開発中は毎回作り直す。そうしないと、保存しても古い印のままになる。
    #
    # ★「起動した時刻」を印にしない理由
    #   本番ではアプリが3つ同時に動く(gunicorn)。起動時刻は3つで微妙にずれるので、
    #   ページを開くたびに印が変わり、手元に取っておく意味が無くなる。
    #   中身から作れば、3つとも必ず同じ印になる。
    cache = not app.debug

    if cache and filename in _versions:
        return _versions[filename]

    static_dir = Path(app.static_folder).resolve()
    path = (static_dir / filename).resolve()

    # ★置き場所の外を指していたら相手にしない("../" で外を読ませないため)。
    if not path.is_relative_to(static_dir) or not path.is_file():
        return ""

    # sha256 = 中身が1文字でも違えば、まったく別の値になる計算。
    version = hashlib.sha256(path.read_bytes()).hexdigest()[:8]

    if cache:
        _versions[filename] = version
    return version
