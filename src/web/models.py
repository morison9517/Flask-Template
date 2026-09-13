# =============================================================================
# models.py = データの形(DBの表)を決める場所
#
#   1つのクラス = DBの1つの表。1行 = 1件のデータ。
#       class User  →  users 表
#
#   この設計図があるおかげで、SQLを書かずに
#       User.query.all()      → 全件取得
#       db.session.add(user)  → 1件追加
#   と書ける。
# =============================================================================

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from web.extensions import db, login_manager


class User(UserMixin, db.Model):
    """ユーザー1人分。

    UserMixin は Flask-Login が「ログイン中か」を判定するために必要な
    お決まりの機能セット。中身は気にしなくてよい。
    """

    __tablename__ = "users"

    # primary_key = この番号で1行を必ず特定できる印。自動で1,2,3…と振られる。
    id = db.Column(db.Integer, primary_key=True)

    # MySQLでは文字の最大長を決める必要があるので String(80) と書く。
    # index=True = この項目で検索が多いので目次を作る。
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)

    email = db.Column(db.String(255), unique=True, nullable=True, index=True)

    # ★パスワードそのものは保存しない。元に戻せない形(ハッシュ)にして保存する。
    #   DBが盗まれてもパスワードは復元できない。変換後は長くなるので255文字。
    password_hash = db.Column(db.String(255), nullable=False)

    # server_default=db.func.now() = 保存時にDB側が現在時刻を入れてくれる。
    # アプリ側で入れ忘れる事故がなくなる。
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    def set_password(self, password: str) -> None:
        """生のパスワードを、戻せない形に変換して保存する。"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """入力されたパスワードが正しいか確かめる。"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """JavaScriptに渡せる形(JSONにできる辞書)に変換する。

        ★password_hash は絶対に含めない。画面に秘密が流れ出る。
        """
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username}>"


# =============================================================================
# LoginAttempt = ログインの失敗を数えておく表
#
#   数え方と締め出しの判断は loginlimit.py。ここは置き場所の形だけ。
#
#   ▼ ★なぜアプリの中の変数ではなくDBに置くのか
#
#     本番では gunicorn が3つのプロセスでアプリを動かす(Dockerfile の
#     --workers 3)。変数に数えるとプロセスごとに別々に数えるので、
#     「5回まで」のつもりが実質15回になる。
#     ★見た目は動いているのに効いていない、という最悪の形になる。
# =============================================================================
class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)

    # ★「アカウントごと」ではなく「アクセス元ごと」に数える。
    #   アカウントごとだと、他人がわざと5回間違えるだけで本人が締め出される。
    #
    # String(45) … IPv6 のいちばん長い形が45文字。足りないと保存に失敗する。
    ip = db.Column(db.String(45), unique=True, nullable=False)

    # 続けて失敗した回数。1回でも成功したら記録ごと消える。
    count = db.Column(db.Integer, nullable=False, default=0)

    # 最後に失敗した時刻。古い記録を捨てる判断に使う。
    last_failure_at = db.Column(db.DateTime, nullable=False)

    # この時刻まで締め出す。
    #
    # ★nullable=True が必要。「失敗を数えている途中」を表すため。
    #   空にできないと未設定を時刻で表すしかなくなり、必ず
    #   「もう過ぎている」と判定されて締め出しが働かない。
    locked_until = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<LoginAttempt {self.ip}: {self.count}回>"


# =============================================================================
# ★ここから書きはじめる
#
#   class Post(db.Model):
#       __tablename__ = "posts"
#
#       id = db.Column(db.Integer, primary_key=True)
#       title = db.Column(db.String(200), nullable=False)
#       created_at = db.Column(db.DateTime, server_default=db.func.now())
#
#       # nullable=True にすると持ち主なしでも保存できる
#       # (ログイン機能をOFFにしても動く)。
#       # ondelete=CASCADE = ユーザーが消えたら投稿も一緒に消す。
#       user_id = db.Column(
#           db.Integer,
#           db.ForeignKey("users.id", ondelete="CASCADE"),
#           nullable=True,
#       )
#
#       # post.user で作者、user.posts で一覧が取れるようになる。
#       user = db.relationship(
#           "User", backref=db.backref("posts", cascade="all, delete")
#       )
# =============================================================================


# ブラウザには「あなたは3番の人」というメモだけが保存されている。
# その番号から実際のユーザーを取ってくるのがこの関数。
# ページを開くたびにFlask-Loginが自動で呼ぶ(自分から呼ぶことはない)。
@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
