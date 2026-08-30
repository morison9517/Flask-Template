# =============================================================================
# デモページの受付。
#
#   ここは「動いていることを確認するための画面」です。
#   自分たちの画面は src/web/routes.py に書きます。
# =============================================================================

from flask import render_template
from flask_login import current_user
from sqlalchemy import text

from web.demo import demo_bp
from web.extensions import db


@demo_bp.get("/__demo")
def index():
    """デモページ。

    この関数は2か所から使われる:
        /        … routes.py にまだトップページが無いとき(demo/__init__.py が登録)
        /__demo  … いつでも
    """
    db_status, db_message = _check_db()

    return render_template(
        "demo/index.html",
        title="セットアップ確認",
        db_status=db_status,
        db_message=db_message,
        # ★真偽値だけを渡している(利用者そのものは渡さない)。
        #   画面に名前を出すと current_user.username を読むことになり、チームが
        #   Userの項目名を変えた日にデモの表示が欠ける。
        #   「ログイン中か」だけならFlask-Loginの機能なので絶対に壊れない。
        logged_in=current_user.is_authenticated,
    )


def _check_db() -> tuple[str, str]:
    """DBに繋がるか実際に試す。

    「SELECT 1」という最小の質問を投げ、返事が来るかで判定している。

    try/except で囲む理由:DBが起動しきっていないだけでこの画面が
    エラーになると原因が分かりにくい。画面は出しつつ「DBだけ未接続」と
    伝えたほうが切り分けが速い。
    """
    try:
        db.session.execute(text("SELECT 1"))
        return "ok", ""
    except Exception as exc:
        # DBのエラー文は数百文字になることがあるので先頭120文字だけ表示する。
        return "ng", str(exc)[:120]
