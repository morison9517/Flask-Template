# =============================================================================
# config.py = 設定を1か所に集める場所
#
#   .env(金庫) ──読む──> config.py ──渡す──> app.py
#
#   コード内に直接パスワードやDB住所を書くと、変更時に全ファイルを探し回るうえ、
#   GitHubに秘密を上げてしまう。
# =============================================================================

import os
from pathlib import Path

from dotenv import load_dotenv

# このファイルは <プロジェクト>/src/web/config.py なので、親を3回たどると入口。
# こう書いておけば、どこから起動しても .env を見つけられる。
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def _env_bool(key: str, default: bool = False) -> bool:
    """.env の "true"/"false" という文字を、Pythonの True/False に変換する。

    .env に書けるのは文字だけなので、"false" をそのまま使うと
    「中身のある文字 = True」と判定されてしまう。その事故を防ぐ。
    """
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    """全モード共通の設定。"""

    # ★プロダクト名が決まったらここを変える。
    #   全ページのタイトルとヘッダーに反映される(base.html から読んでいる)。
    #   HTMLに直書きすると、名前を変えるときに探し回ることになる。
    SITE_NAME = "Flask Template Demo"

    # ★検索結果でタイトルの下に出る2行。SNSに貼ったときの説明文にもなる。
    #   120文字前後に収めること。長いと検索結果で途中から切られる。
    #   ページごとに変えたいときは、render_template に description="..." を渡す。
    SITE_DESCRIPTION = (
        "FlaskのWebアプリ開発テンプレート。docker compose up だけで開発環境が立ち上がります。"
    )

    # SNSに貼ったときに出るサムネイル画像。
    #
    # ★空のときは画像用のタグを出さない。画像が無いのにタグだけ出すと、
    #   SNS側が「画像が取れない」と判断してカードが小さいまま表示される。
    # 用意するとき: 1200x630 の画像を static/images/ogp.png に置き、
    #               ここを "/static/images/ogp.png" にする。
    OGP_IMAGE = ""

    # ログイン状態をブラウザに預けるときの割り印。
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # DBの住所+鍵。読み方:
    #   mysql+pymysql://ユーザー:パスワード@住所:ポート/DB名?文字コード
    # utf8mb4 は絵文字も扱える指定(utf8 だと絵文字でエラーになる)。
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{os.getenv('DB_USER', 'hack_user')}:"
        f"{os.getenv('DB_PASSWORD', 'hack_password')}@"
        f"{os.getenv('DB_HOST', 'db')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 'hack_app')}"
        "?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DBとの回線は放置されると切られる。切れた回線に気づかず話しかけると
    # 「突然エラー」になるので、使う前に生存確認する。
    # 「しばらく放置したら動かなくなった」を防ぐ設定。
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # false にすると、ログイン関連の受付を登録しない。
    AUTH_ENABLED = _env_bool("AUTH_ENABLED", True)

    TEMPLATES_AUTO_RELOAD = True

    # アップロード上限16MB。上限が無いと巨大ファイルでサーバーが落ちる。
    # ★Nginx側(docker/nginx/prod.conf)の client_max_body_size と同じ値にすること。
    #   片方だけ大きくしても意味がなく、「なぜか大きい画像だけ失敗する」になる。
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # 利用者が上げたファイルの保存先。
    #
    # ★static と分ける理由: static は自分たちが用意したものでGitに入れる。
    #   media は利用者が上げたもので、消したら戻らない。
    #   だから本番では media だけを箱の外の保管庫に置く。
    UPLOAD_FOLDER = str(BASE_DIR / "media")


class DevConfig(Config):
    """開発モード。"""

    DEBUG = True  # エラーの原因を詳しく表示 + 保存で自動再起動


class ProdConfig(Config):
    """本番モード。"""

    DEBUG = False  # エラーの中身を外部に見せない(攻撃の材料になる)

    SESSION_COOKIE_HTTPONLY = True  # JavaScriptから読めないようにする
    SESSION_COOKIE_SAMESITE = "Lax"  # 他サイトから勝手に使われるのを防ぐ

    # ▼ ★本番でいちばんハマる設定
    #
    #   True = HTTPSのときだけログイン状態を持ち歩く。本番は True が正解。
    #
    #   ★HTTPのまま True にすると、ログインは成功しているのに次のページで
    #     必ずログイン画面に戻される。エラーも出ないので原因が分からない。
    #     練習中だけ .env に FLASK_SECURE_COOKIES=False と書いて切る。
    SESSION_COOKIE_SECURE = _env_bool("FLASK_SECURE_COOKIES", True)


CONFIG_MAP = {
    "development": DevConfig,
    "production": ProdConfig,
}


def get_config():
    """.env の FLASK_ENV を見て、使う設定クラスを返す。"""
    env = os.getenv("FLASK_ENV", "development").strip().lower()
    # 知らない値が書かれていたら安全側(開発モード)に倒す。
    return CONFIG_MAP.get(env, DevConfig)
