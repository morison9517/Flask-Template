# =============================================================================
# ログイン・ログアウト・新規登録
#
#   ▼ Flask側の受け取り方
#     GET  = 画面を見に来た  → HTMLを返す
#     POST = 入力を送ってきた → 中身を照合する
#     同じURLでも methods で分岐する。
#
#   ▼ flash("文字")
#     次に表示される画面に一度だけメッセージを出す仕組み。
#     表示場所は base.html に1か所だけ書いてある。
# =============================================================================

from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request
from flask_login import current_user, login_required, login_user, logout_user

from web.auth import auth_bp
from web.extensions import db
from web.models import User


def _safe_redirect_target(target: str | None, fallback: str = "/") -> str:
    """ログイン後の遷移先が安全か確かめる。

    ログイン画面のURLには /auth/login?next=/mypage のように戻り先が付く。
    この next を無条件に信じると、?next=https://偽サイト.com というリンクを
    配られてログイン直後に飛ばされる(オープンリダイレクト)。
    自サイト内("/"始まり)だけを許可する。

    ★行き先が名前(url_for)ではなく "/" なのは、トップページの持ち主が
      デモ → 自分たちのページ と入れ替わるため。場所自体は変わらない。
    """
    if not target:
        return fallback

    # 自サイト内なら /mypage の形なのでドメイン名(netloc)は空になる。
    parts = urlsplit(target)
    if parts.netloc or parts.scheme:
        return fallback
    if not target.startswith("/"):
        return fallback
    return target


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """新しいユーザーを作る。"""

    # current_user = 今アクセスしている人。Flask-Loginが用意する。
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        # request.form.get("username") の "username" は
        # HTML側の <input name="username"> と1対1で対応する。
        # ここがズレると値が届かない(つまずきの定番)。
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        # 問題点をまとめて集めて最後に表示する。
        # 「1個直すと次のエラーが出る」を繰り返させないため。
        errors = []
        if not username:
            errors.append("ユーザー名を入力してください。")
        elif len(username) > 80:
            errors.append("ユーザー名は80文字以内で入力してください。")

        if len(password) < 8:
            errors.append("パスワードは8文字以上で入力してください。")

        if password != password_confirm:
            errors.append("パスワードが一致しません。")

        # filter_by(...) で条件検索、.first() で最初の1件(無ければ None)。
        if username and User.query.filter_by(username=username).first():
            errors.append("そのユーザー名はすでに使われています。")

        if errors:
            for message in errors:
                flash(message, "error")
            # username を渡すので、入力した名前は消えずに残る。
            return render_template("register.html", title="新規登録", username=username)

        user = User(username=username)
        user.set_password(password)

        # db.session はレジのカゴ。
        #   add()    = カゴに入れる(まだ保存されていない)
        #   commit() = レジを通す(ここで初めてDBに書き込まれる)
        # commit 忘れは「保存したのに消えている」の定番原因。
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"ようこそ、{user.username} さん!", "success")
        return redirect("/")

    return render_template("register.html", title="新規登録")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """ユーザー名とパスワードを照合してログインさせる。"""

    if current_user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        # ★「ユーザー名が違います」と書かない理由
        #   どの名前が実在するかを攻撃者に教えてしまうため、あえてぼかす。
        #   user が None のとき check_password を呼ぶと落ちるので、
        #   「user が居る かつ パスワードが合う」の順に確認する。
        if user is None or not user.check_password(password):
            flash("ユーザー名またはパスワードが正しくありません。", "error")
            return render_template("login.html", title="ログイン", username=username)

        # login_user() がブラウザに「あなたは○番の人」というメモを持たせる。
        # remember=True でブラウザを閉じてもログイン状態が続く(デモ時に便利)。
        login_user(user, remember=True)
        flash("ログインしました。", "success")

        # ログイン必須ページから飛ばされて来た人は元の場所に戻す。
        next_page = request.args.get("next")
        return redirect(_safe_redirect_target(next_page))

    return render_template("login.html", title="ログイン")


# ★@login_required を付けると「ログイン中の人だけ通す」ドアになる。
#   未ログインの人は extensions.py で指定したログイン画面へ自動で案内される。
#   会員専用ページを作りたいときは、この1行を足すだけ。
@auth_bp.post("/logout")
@login_required
def logout():
    """ログアウトする。

    GETではなくPOSTにしている理由:GETでログアウトできると
    <img src="/auth/logout"> と書かれただけで勝手にログアウトさせられる。
    「状態を変える操作はPOST」が基本ルール。
    """
    logout_user()
    flash("ログアウトしました。", "success")
    return redirect("/")
