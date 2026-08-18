# =============================================================================
# extensions.py = 共用の道具置き場
#
#   ▼ このファイルを分けている理由(Flask特有のハマりどころ)
#
#   もし app.py で db を作ると、
#       models.py が db を求めて app.py を見に行く
#       app.py が models を求めて models.py を見に行く
#   とお互いを見に行って終わらなくなる(循環インポート)。
#
#   中立な場所に道具を置けば、矢印が一方通行になるので詰まらない。
#       app.py    ──→ extensions.py
#       models.py ──→ extensions.py
#
#   もう1つの理由:db は「アプリ全体でたった1個」を使い回す必要がある。
#   別々に作ると「保存したのに他から見えない」という不具合になる。
# =============================================================================

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# --- DBを操作する道具 ---
# ここでは箱を用意しただけ。接続先は app.py の db.init_app(app) で決まる。
db = SQLAlchemy()

# --- ログイン状態を管理する道具 ---
login_manager = LoginManager()

# ログインしていない人が会員専用ページに来たときの案内先。
# "auth.login" = 「auth という受付の島の login」という指定。
login_manager.login_view = "auth.login"
login_manager.login_message = "このページを見るにはログインが必要です。"
login_manager.login_message_category = "warning"

# --- 成りすまし防止(CSRF対策) ---
# ログイン中に別サイトの罠を踏むと、あなたの名前で勝手に送信されてしまう。
# フォームに「使い捨ての整理券」を埋め込み、無い依頼は受け付けないことで防ぐ。
# 開発側の作業は、フォームに {{ csrf_token() }} を1行入れるだけ。
csrf = CSRFProtect()
