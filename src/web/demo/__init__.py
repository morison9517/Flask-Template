# =============================================================================
# demo/ = 動作確認用のデモページ一式(自分たちのプロダクトには含まれません)
#
# ▼ ★このフォルダの決まり
#
#   1. 開発モード(FLASK_ENV=development)のときだけ取り付けられる。
#      本番では取り付けないので、消し忘れても本番には出ない。
#
#   2. トップページ("/")は、routes.py にまだ "/" が無いときだけ引き受ける。
#      自分たちのトップページを書いた瞬間に、デモは自動で出なくなる。
#      → 開発を始めるときに「デモを消す作業」は不要。
#
#   3. いつでも見たいときは /__demo で開ける(開発モードのときだけ)。
#      DBに繋がっているかの確認に使える。
#
#   ★DjangoやRailsの「セットアップ完了ページ」と同じ仕組みです。
#     あちらも、自分でトップページを作ると自動で出なくなります。
#
# ▼ 本当に不要になったら
#
#   このフォルダごと削除して、app.py の「デモ」の3行を消すだけで終わりです。
# =============================================================================

from flask import Blueprint, Flask

# template_folder を指定すると、この島は自分のフォルダのHTMLを使う。
# デモのHTMLが src/web/templates/ に混ざらないので、あとで消しやすい。
demo_bp = Blueprint("demo", __name__, template_folder="templates")


def register_demo(app: Flask) -> None:
    """デモを取り付ける。app.py から、開発モードのときだけ呼ばれる。"""

    # /__demo は常に開けるようにしておく(自分たちのトップページを作った後も
    # 「DBに繋がっているか」をここで確認できる)。
    app.register_blueprint(demo_bp)

    # ★トップページが空いているときだけ、デモが "/" を引き受ける。
    #   routes.py に "/" を書いた後は、この条件が外れてデモは出なくなる。
    if not _has_top_page(app):
        from web.demo.routes import index

        app.add_url_rule("/", endpoint="demo_top", view_func=index)


def _has_top_page(app: Flask) -> bool:
    """自分たちのトップページ("/")が既に登録されているか調べる。"""
    return any(rule.rule == "/" for rule in app.url_map.iter_rules())


# ★この import が最後にある理由
#   routes.py は上で作った demo_bp を使うので、先に demo_bp が存在していないと
#   エラーになる。表札を立ててからマニュアルを配る、という順番。
from web.demo import routes  # noqa: E402, F401
