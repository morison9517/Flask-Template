# =============================================================================
# app.py = 全部をつなげてアプリを起動する場所
#
#   ▼ create_app() という関数にする理由(Flaskの定番の書き方)
#     これは「お店の組み立て手順書」。手順書にしておくと、同じ構成で
#     開発用・本番用・テスト用のアプリを作り分けられる。
#     現物を1つだけ作ってしまうと、設定を変えるにはコードを書き換えるしかない。
#
#   ▼ このファイルは基本的に触らない
#     機能を足すときに触るのは routes.py / api.py / models.py。
#     ここを触るのは「新しい島(Blueprint)を増やしたとき」だけ。
# =============================================================================

from flask import Flask

from web.config import get_config
from web.extensions import csrf, db, login_manager


def create_app(config_class=None) -> Flask:
    """Flaskアプリを組み立てて返す。"""

    # __name__ を渡すと、Flaskが「隣の templates/ と static/ を使う」と判断する。
    app = Flask(__name__)

    # 指定がなければ .env の FLASK_ENV を見て自動で設定を選ぶ。
    app.config.from_object(config_class or get_config())

    # extensions.py で箱だけ作っておいた道具に、接続先を教える。
    db.init_app(app)
    login_manager.init_app(app)

    # 整理券(CSRFトークン)が必須になる。
    # 「送信ボタンでエラーになる」ときは、まずHTMLに {{ csrf_token() }} が
    # 入っているかを確認する。
    csrf.init_app(app)

    # ★この import を関数の中に書く理由
    #   先頭に書くと、models.py が db を探すタイミングとぶつかって
    #   お互いを待ち続ける状態になる。ここなら db の準備が済んでいて安全。
    #
    # ★import するだけでいい理由
    #   読み込んだ瞬間にSQLAlchemyが「User と Todo という表がある」と覚える。
    #   覚えさせないと create_all() が作る表を見つけられない。
    #   使っていないように見えても消さない。
    from web import models  # noqa: F401

    _register_blueprints(app)
    _register_commands(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """受付の島(Blueprint)を取り付ける。

    ★新しい島を作ったら、ここに2行足す。
    """
    # --- 画面を返す島 ---
    from web.routes import main_bp

    app.register_blueprint(main_bp)

    # --- データ(JSON)を返す島 ---
    # ★次のステップで api.py を作ったら、下の2行のコメントを外す。
    # from web.api import api_bp
    # app.register_blueprint(api_bp, url_prefix="/api")

    # --- ログインの島 ---
    # url_prefix="/auth" を付けると、auth/ 内の "/login" が
    # 実際には "/auth/login" になる。
    # AUTH_ENABLED が false なら取り付けない(消さずにOFFにできる)。
    if app.config.get("AUTH_ENABLED"):
        from web.auth import auth_bp

        app.register_blueprint(auth_bp, url_prefix="/auth")


def _register_commands(app: Flask) -> None:
    """ターミナルから使えるコマンドを登録する(実行方法は docs/SETUP.md)。"""

    @app.cli.command("init-db")
    def init_db() -> None:
        """models.py の設計図どおりにDBに表を作る。

        初回起動時と、models.py にクラスを足したときに使う。
        既にある表は作り直さないので、データは消えない。
        """
        db.create_all()
        print("DBに表を作りました(既にある表はそのままです)")

    @app.cli.command("drop-db")
    def drop_db() -> None:
        """DBの表を全部消す。★中のデータも全部消える★

        列の型を変えた場合(String(80)→String(200)など)、既にある表の形は
        自動で変わらない。そういうときに全部捨てて作り直すために使う。
        """
        db.drop_all()
        print("DBの表を全部消しました")


# 上の手順書を実行して、アプリの現物を1つ作る。
# この app という変数を、Flaskの起動コマンドや本番のサーバーが探す。
app = create_app()


# python app.py と直接実行したときだけ動く非常口。
# 普段は docker compose up で起動するのでここは通らない。
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
