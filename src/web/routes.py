# =============================================================================
# routes.py = 画面(HTML)を返す受付
#
#   ブラウザ「/ をください」 → ここ → 「index.html をどうぞ」
#
#   ▼ Blueprint = 受付カウンターの島
#
#     全URLを1ファイルに書くと巨大になり、みんなで編集すると必ず衝突する。
#     島に分けておけば別ファイルを触るので衝突しない。
#         routes.py → 画面を返す島(main)
#         api.py    → データだけ返す島(api)
#         auth/     → ログインの島(auth)
#
#   ▼ ★トップページはまだ空いている
#
#     今 "/" を開くとデモページが出るのは、まだ誰も "/" を作っていないから。
#     下の見本のコメントを外せば自分たちの画面に入れ替わる。
#     デモを消す作業は要らない(仕組みは demo/__init__.py)。
# =============================================================================

from flask import Blueprint

# "main" が島の名前。画面から url_for("main.○○") と呼ぶときに使う。
# URLを直書きせず名前で呼ぶと、後からURLを変えても呼び出し側を直さずに済む。
main_bp = Blueprint("main", __name__)


# ★ここから書きはじめる(コメントを外して、HTMLを1枚 templates/ に置く)
#
#   @main_bp.get("/")
#   def index():
#       return render_template("index.html", title="ホーム")
#
#   render_template を使うときは import に足すこと:
#       from flask import Blueprint, render_template


@main_bp.get("/health")
def health():
    """動作確認用。辞書を返すとFlaskが自動でJSONに変換する。

    AWSやNginxが「アプリが生きているか」を確認しに来る先。
    開発中も「画面が出ない…アプリ自体は動いてる?」の切り分けに使える。
    """
    return {"status": "ok"}
