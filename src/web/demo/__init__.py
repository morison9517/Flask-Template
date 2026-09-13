# =============================================================================
# demo/ = 動作確認用のデモページ一式(プロダクトには含まれません)
#
# ▼ このフォルダの決まり
#
#   ・開発モードのときだけ取り付ける。本番には出ず、デモ用の表も作られない。
#   ・トップページ("/")は routes.py に "/" が無いときだけ引き受ける。
#     自分たちのトップページを書いた瞬間に自動で出なくなる(消す作業は不要)。
#   ・いつでも /__demo で開ける。DBに繋がっているかの確認に使える。
#   ・★画面は1枚完結。base.html も style.css も使わない。
#     「セットアップが動いているか」を見せる計器なので、共通のファイルを
#     作り替えても壊れないようにしてある。書き方の見本にはしないこと
#     (見本は templates/login.html)。
#
# ▼ 不要になったら、このフォルダと app.py の「デモ」の3行を消すだけ。
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
#   routes.py と api.py は上で作った demo_bp を使うので、先に demo_bp が
#   存在していないとエラーになる。表札を立ててからマニュアルを配る、という順番。
#
#   models.py もここで読み込まれる(api.py 経由)。
#   ★読み込まれて初めてSQLAlchemyが「todos という表がある」と覚える。
#     本番ではこのフォルダを一切読み込まないので、todos は作られない。
from web.demo import api, routes  # noqa: E402, F401
