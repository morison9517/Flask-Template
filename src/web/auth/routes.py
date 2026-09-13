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
from web.loginlimit import (
    clear_failures,
    client_ip,
    lock_remaining,
    minutes_to_wait,
    record_failure,
    remaining_attempts,
)
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

        # ▼ ★何度も失敗している相手は、照合する前に追い返す
        #
        #   仕組みは loginlimit.py。パスワードを見る前に止めるのが要点。
        #   ここを照合の後ろに置くと、締め出し中でも1回ずつ試させてしまい、
        #   時間をかければ当てられる状態のままになる。
        ip = client_ip()

        remaining = lock_remaining(ip)
        if remaining is not None:
            minutes = minutes_to_wait(remaining)

            flash(
                "ログインの失敗が続いたため、一時的に制限しています。"
                f"あと約{minutes}分お待ちください。",
                "error",
            )
            # 429 = 「回数が多すぎる」を表す番号。
            return render_template("login.html", title="ログイン", username=username), 429

        user = User.query.filter_by(username=username).first()

        # ★「ユーザー名が違います」と書かない理由
        #   どの名前が実在するかを攻撃者に教えてしまうため、あえてぼかす。
        #   user が None のとき check_password を呼ぶと落ちるので、
        #   「user が居る かつ パスワードが合う」の順に確認する。
        if user is None or not user.check_password(password):
            # 失敗を1回数える。5回目でこのアクセス元は15分締め出される。
            record_failure(ip)

            message = "ユーザー名またはパスワードが正しくありません。"
            status = 200

            # ★今の失敗で締め出しに達したかを、その場で確かめて伝える。
            #
            #   これが無いと、5回目は普通の「違います」だけが出て、
            #   次にもう一度押したときに初めて締め出しを知ることになる。
            #   利用者から見ると「急に入れなくなった」としか分からない。
            reached = lock_remaining(ip)
            if reached is not None:
                minutes = minutes_to_wait(reached)
                message = (
                    "ログインの失敗が続いたため、一時的に制限しました。"
                    f"あと約{minutes}分お待ちください。"
                )
                status = 429
            else:
                # ★残り回数を出す理由は loginlimit.py の remaining_attempts に。
                #   残り2回以下になってから出す(最初から出すと不安にさせるだけ)。
                left = remaining_attempts(ip)
                if 0 < left <= 2:
                    message += f"(あと{left}回失敗すると、しばらくログインできなくなります)"

            flash(message, "error")
            return render_template("login.html", title="ログイン", username=username), status

        # ★成功したら失敗の記録を消す。
        #   これが無いと、正しく入れた後も前の失敗が残り続け、
        #   次に1回打ち間違えただけで締め出される。
        clear_failures(ip)

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
