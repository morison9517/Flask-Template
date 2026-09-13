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

from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from web.config import get_config
from web.extensions import csrf, db, login_manager


def create_app(config_class=None) -> Flask:
    """Flaskアプリを組み立てて返す。"""

    # __name__ を渡すと、Flaskが「隣の templates/ と static/ を使う」と判断する。
    app = Flask(__name__)

    # 指定がなければ .env の FLASK_ENV を見て自動で設定を選ぶ。
    app.config.from_object(config_class or get_config())

    # ★JSONで日本語をそのまま読める形で返す設定。
    #   無いと {"title": "\u725b\u4e73"} のような記号の羅列で返る。
    #   JavaScriptは読めるが、開発者ツールで中身を確認するときに読めず
    #   「文字化けした」と勘違いして原因調査が遠回りになる。
    app.json.ensure_ascii = False

    # extensions.py で箱だけ作っておいた道具に、接続先を教える。
    db.init_app(app)
    login_manager.init_app(app)

    # 整理券(CSRFトークン)が必須になる。
    # 「送信ボタンでエラーになる」ときは、まずHTMLに {{ csrf_token() }} が
    # 入っているかを確認する。
    csrf.init_app(app)

    # ★関数の中に書くこと。先頭に書くと models.py が db を探すタイミングと
    #   ぶつかって、お互いを待ち続ける状態になる。
    # ★import するだけでよい。読み込んだ瞬間にSQLAlchemyが表を覚える。
    #   使っていないように見えても消さない。
    from web import models  # noqa: F401

    _register_blueprints(app)
    _register_commands(app)
    _register_media(app)
    _register_errors(app)
    _register_seo(app)
    _trust_proxy(app)

    return app


def _register_errors(app: Flask) -> None:
    """エラー画面(404など)の担当を取り付ける。中身は errors.py。"""
    from web.errors import register_error_pages

    register_error_pages(app)


def _register_seo(app: Flask) -> None:
    """検索結果とSNSでの見え方、/robots.txt、/favicon.ico を取り付ける。

    文言(サイト名・説明文)は config.py、中身は seo.py。
    """
    from web.seo import register_seo

    register_seo(app)


def _trust_proxy(app: Flask) -> None:
    """Nginxが教えてくれる「本当の情報」を信用する設定。

    ★本番では Nginx が前に立つので、Flaskから見た相手が Nginx になる。
      入れないと、HTTPSで来ているのに「HTTPだ」と思い込み、
      フォームの送信が弾かれたりリンクが http:// で作られたりする。

    ★開発中は入れない。Nginxがいないうえ、有効なまま外に晒すと
      利用者が自分でヘッダーを詐称してIPを偽れてしまう。
    """
    if not app.config.get("DEBUG"):
        # x_for=1 / x_proto=1 = 「手前に1台だけ信用できるNginxがいる」という意味。
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


def _register_media(app: Flask) -> None:
    """利用者が上げたファイル(プロフィールアイコンなど)を配る口。

    ★開発モードのときだけ登録する。
      本番ではNginxが配るので、ここは登録しない(compose.prod.yml 参照)。
      Flaskに画像配りをさせると遅いうえ、本番では動かないようにしてある。
    """
    if not app.config.get("DEBUG"):
        return

    @app.get("/media/<path:filename>")
    def media(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


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

    # --- デモ(動作確認用のページ) ---
    # ★必ず最後に取り付ける。
    #   「自分たちのトップページが既にあるか」を見てから動くので、
    #   先に取り付けると判定できない。
    #   開発モードのときだけ。本番では取り付けないので絶対に出ない。
    if app.config.get("DEBUG"):
        from web.demo import register_demo

        register_demo(app)


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
