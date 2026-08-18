# =============================================================================
# routes.py = 画面(HTML)を返す受付
#
#   ブラウザ「/ をください」 → ここ → 「index.html をどうぞ」
#
#   ▼ Blueprint = 受付カウンターの島
#     全URLを1ファイルに書くと巨大になり、6人で編集したとき必ず衝突する。
#     島に分けておけば別ファイルを触るので衝突しない。
#         routes.py → 画面を返す島(main)
#         api.py    → データだけ返す島(api)
#         auth/     → ログインの島(auth)
# =============================================================================

from flask import Blueprint, render_template
from sqlalchemy import text

from web.extensions import db

# "main" が島の名前。画面から url_for("main.index") と呼ぶときに使う。
# URLを直書きせず名前で呼ぶと、後からURLを変えても呼び出し側を直さずに済む。
main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    """トップページ。

    render_template("index.html") = templates/index.html を読んで完成HTMLを返す。
    2つ目以降の引数はHTML側への差し込み情報で、HTML内の {{ title }} に入る。
    """
    db_status, db_message = _check_db()

    return render_template(
        "index.html",
        title="ホーム",
        db_status=db_status,
        db_message=db_message,
    )


def _check_db() -> tuple[str, str]:
    """DBに繋がるか実際に試す。

    「SELECT 1」という最小の質問を投げ、返事が来るかで判定している。

    try/except で囲む理由:DBが起動しきっていないだけでトップページが
    エラー画面になると原因が分かりにくい。画面は出しつつ「DBだけ未接続」と
    伝えたほうが切り分けが速い。
    """
    try:
        db.session.execute(text("SELECT 1"))
        return "ok", ""
    except Exception as exc:
        # DBのエラー文は数百文字になることがあるので先頭120文字だけ表示する。
        return "ng", str(exc)[:120]


@main_bp.get("/health")
def health():
    """動作確認用。辞書を返すとFlaskが自動でJSONに変換する。

    AWSやNginxが「アプリが生きているか」を定期的に確認しに来る先。
    開発中も「画面が出ない…アプリ自体は動いてる?」の切り分けに使える。
    """
    return {"status": "ok"}
