# =============================================================================
# errors.py = エラー画面(400 / 401 / 403 / 404 / 500)を返す担当
#
#   これが無いと、存在しないURLを開いた人に Flask の素っ気ない「Not Found」だけが
#   返る。ヘッダーもCSSも無い真っ白な画面なので「サイトが壊れた」としか見えない。
#
#   ▼ 使い方
#
#       from flask import abort
#       abort(404)
#
#     ★abort() は return が要らない。呼んだ瞬間にそこで処理が中断される。
#
#   ▼ ★開発中は500のページが出ない(これは正常)
#
#     開発モードでは、Flaskが「どの行で落ちたか」を出す専用の画面を見せる。
#     500のページが実際に出るのは本番(FLASK_ENV=production)のときだけ。
#     見た目を確かめたいときは /__error/500 を開く。
#
#   ▼ 文言を直す・種類を増やす
#
#     下の ERROR_PAGES の表を書き換えるだけ。HTML(error.html)は共通の1枚。
#
#   ▼ 消したいとき
#
#     このファイルと templates/error.html を消し、app.py の
#     _register_errors(app) の1行を消す。
# =============================================================================

from flask import current_app, jsonify, render_template, request

# 文言の表。★直すのはここ。
#
# ★400番台は送ってきた側の問題、500番台はこちら側の問題。
#   この区切りは検索エンジンも見ていて、「ページが無い」ときに200を返すと
#   無いページが検索結果に載り続ける。
#
# ★401 と 403 の違いは「誰か分からない」と「見せられない」。
#   このテンプレートのログイン必須ページは、403ではなくログイン画面へ案内する
#   (Flask-Login がやっている)。そのほうが親切なため。
ERROR_PAGES = {
    400: ("Bad Request", "リクエストの内容に誤りがあります。"),
    401: ("Unauthorized", "このページを表示する権限がありません。"),
    403: ("Forbidden", "このページを表示する権限がありません。"),
    404: ("Not Found", "指定されたページが見つかりませんでした。"),
    500: ("Internal Server Error", "サーバー側で問題が発生しました。時間をおいて試してください。"),
}

# 表に無い番号が来たときの文言。
# ★何も返さないと真っ白な画面になるので、受け皿を必ず用意する。
FALLBACK_ERROR_PAGE = ("Error", "問題が発生しました。")


def show_error(status: int):
    """エラー画面を作って返す。

    ★JavaScript向けのURL(/api/...)にはHTMLではなくJSONを返す。
      main.js は {"error": "..."} の形を待っているので、HTMLを返すと
      JS側が「JSONとして読めない」と別のエラーになり、本当の原因が消える。
    """
    name, message = ERROR_PAGES.get(status, FALLBACK_ERROR_PAGE)

    if request.path.startswith("/api/"):
        return jsonify(error=message), status

    return (
        render_template(
            "error.html",
            title=str(status),
            error_code=status,
            error_name=name,
            error_message=message,
        ),
        status,
    )


def register_error_pages(app) -> None:
    """エラー画面の担当を取り付ける。app.py の create_app() から呼ばれる。

    ★表を回して登録している。1つずつ @app.errorhandler(404) と書くと、
      種類を増やすたびに2か所を直すことになり、片方だけ直す事故が起きる。
    """
    for status in ERROR_PAGES:
        # ★default=status が必要(Pythonのつまずきどころ)。
        #   関数の中で外側の status を読むと、for が回り終わった後の値(500)を
        #   全部が見てしまう。これが無いと404を開いても500の文言が出る。
        def handler(error, default=status):
            return show_error(getattr(error, "code", None) or default)

        app.register_error_handler(status, handler)

    # 見本のURL(開発モードのときだけ)。
    #
    # ★本番では登録しない。お客さんが開ける「わざとエラーを出すURL」は残さない。
    #   500は開発中に本物を出せない(デバッガが出る)ので、ここから確認する。
    if app.config.get("DEBUG"):

        @app.get("/__error/<int:status>")
        def error_preview(status: int):
            current_app.logger.info("エラー画面の見本を表示しました: %s", status)
            return show_error(status)
