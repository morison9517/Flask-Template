# =============================================================================
# ログイン関係の受付の島(Blueprint)を作る場所。
# 受付の中身は routes.py にある。
# =============================================================================

from flask import Blueprint

# "auth" が島の名前。画面から url_for("auth.login") と呼べる。
# template_folder を指定していないので、この島も src/web/templates/ を使う。
auth_bp = Blueprint("auth", __name__)


# ★この import が最後にある理由
#   routes.py は上で作った auth_bp を使うので、先に auth_bp が存在していないと
#   エラーになる。表札を立ててからマニュアルを配る、という順番。
#   noqa は「順番のルール違反だが意図的」という ruff への注記。
from web.auth import routes  # noqa: E402, F401
