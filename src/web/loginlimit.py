# =============================================================================
# loginlimit.py = ログインを何度も失敗した相手を、しばらく締め出す仕掛け
#
#   パスワードは試し放題だといつか当たる(総当たり)。1回ずつは正しい手順なので、
#   パスワードの中身では防げない。「短い時間に何度も失敗している」回数で止める。
#
#   ★公開するサイトのログイン画面は必ず機械に試される。
#     公開した翌日のログに、知らないIPからの試行が並ぶ。
#
#   ▼ 決めごと(下の定数で変えられる)
#
#     5回続けて失敗すると、そのアクセス元は15分間ログインできない。
#     1回でも成功すれば帳消し。最後の失敗から15分経つと記録も消える。
#
#   ▼ 記録の置き場所は models.py の LoginAttempt(DBの表)
#
#     ★アプリの中の変数ではなくDBに置いてある。理由はそちらに書いてある。
#     ★表を追加したので、初回だけ次のコマンドが要る:
#         docker compose exec web flask init-db
#
#   ▼ 消したいとき
#
#     このファイルと models.py の LoginAttempt を消し、
#     auth/routes.py の login() から呼び出しを外す。
# =============================================================================

import math
from datetime import datetime, timedelta

from flask import current_app, request

from web.extensions import db
from web.models import LoginAttempt

# ★ここを変えれば厳しさが変わる。
#
# MAX_ATTEMPTS  … 3回まで下げると、打ち間違いで普通の利用者が締め出される。
# LOCK_DURATION … 長くしすぎないこと。総当たりは「1分間に何回試せるか」で
#                 成否が決まるので15分でも十分に割に合わなくなる。
# ATTEMPT_WINDOW… これが無いと、何日も前の1回の失敗が残り続け、
#                 久しぶりに来て4回間違えただけで締め出される。
MAX_ATTEMPTS = 5
LOCK_DURATION = timedelta(minutes=15)
ATTEMPT_WINDOW = timedelta(minutes=15)


def client_ip() -> str:
    """アクセス元のIPを取る。

    ★本番でNginxの向こうの本当の相手を読む設定(ProxyFix)は app.py にある。
      そのためここは request.remote_addr を読むだけでよい。
    """
    return request.remote_addr or "unknown"


def lock_remaining(ip: str) -> timedelta | None:
    """あと何分締め出されているか。None なら締め出されていない。"""
    attempt = _find(ip)
    if attempt is None:
        return None

    # ★まだ締め出していない(失敗を数えている途中)。
    #   ここを飛ばすと、数えている途中の記録まで下で消してしまい、
    #   回数が5に届かず締め出しが一度も働かなくなる。
    if attempt.locked_until is None:
        return None

    remaining = attempt.locked_until - datetime.now()
    if remaining.total_seconds() <= 0:
        db.session.delete(attempt)
        db.session.commit()
        return None

    return remaining


def record_failure(ip: str) -> None:
    """失敗を1回数える。5回目で締め出す。"""
    _sweep_old()

    attempt = _find(ip)
    if attempt is None:
        attempt = LoginAttempt(ip=ip, count=0)
        db.session.add(attempt)

    attempt.count += 1
    attempt.last_failure_at = datetime.now()

    if attempt.count >= MAX_ATTEMPTS:
        # ★秒未満を捨てる。DBの時刻の列は秒までしか持てず、秒未満は
        #   四捨五入される。切り上がると残り時間が15分を超え、
        #   画面に「あと約16分」と出る。
        attempt.locked_until = (datetime.now() + LOCK_DURATION).replace(microsecond=0)

        # ★締め出したことはログに残す。これが無いと「ログインできない」と
        #   言われたときに、締め出したのか設定が壊れたのか切り分けられない。
        current_app.logger.warning(
            "[login] %s を %s 締め出しました(%d回失敗)", ip, LOCK_DURATION, attempt.count
        )

    db.session.commit()


def clear_failures(ip: str) -> None:
    """失敗の記録を消す。ログイン成功時に呼ぶ。"""
    attempt = _find(ip)
    if attempt is not None:
        db.session.delete(attempt)
        db.session.commit()


def remaining_attempts(ip: str) -> int:
    """あと何回間違えたら締め出されるか。画面表示用。

    ★回数を教えてよい。機械は表示されなくても総当たりを続けるので隠しても
      効果が無く、普通の利用者には「次で締め出される」と分かるほうが親切。
    """
    attempt = _find(ip)
    if attempt is None:
        return MAX_ATTEMPTS

    return max(MAX_ATTEMPTS - attempt.count, 0)


def minutes_to_wait(remaining: timedelta) -> int:
    """残り時間を「あと約◯分」に直す。

    ★切り上げること。切り捨てると残り30秒で「あと約0分」と出て、
      待っても入れないので壊れているように見える。必ず1分以上を返す。
    """
    return max(1, math.ceil(remaining.total_seconds() / 60))


def _find(ip: str) -> LoginAttempt | None:
    return LoginAttempt.query.filter_by(ip=ip).first()


def _sweep_old() -> None:
    """古くなった記録を捨てる。

    ★捨てないと、IPを変えながら試された分だけ表が際限なく大きくなる。
      締め出し中のものは明けるまで残す。
    """
    now = datetime.now()

    LoginAttempt.query.filter(
        LoginAttempt.last_failure_at < now - ATTEMPT_WINDOW,
        db.or_(
            LoginAttempt.locked_until.is_(None),
            LoginAttempt.locked_until < now,
        ),
    ).delete(synchronize_session=False)

    db.session.commit()
