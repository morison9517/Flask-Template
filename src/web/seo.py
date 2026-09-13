# =============================================================================
# seo.py = 検索結果とSNSでの見え方を用意する担当
#
#   ★画面には1文字も出ない。出るのは検索結果と、SNSやチャットにURLを
#     貼ったときのカード。「作ったのに何も変わらない」と思ったら、
#     リンクをSlackやXに貼って確かめること。
#
#   このファイルが用意するもの:
#     ・全ページのHTMLから使える値(canonical_url / site_url / ogp_image)
#     ・/robots.txt と /favicon.ico
#       ★どちらもサイト直下に無いと読まれない。/static/ に置いても
#         検索エンジンは見に来ないので、ここで直下に出している。
#
#   文言(サイト名・説明文・画像)は config.py にある。このファイルは仕組みだけ。
#
#   ▼ 消したいとき
#
#     このファイルを消し、app.py の _register_seo(app) の1行と、
#     base.html の検索・SNS向けのタグを消す。
# =============================================================================

from flask import current_app, request, send_from_directory


def register_seo(app) -> None:
    """SEO関連の値とURLを取り付ける。app.py の create_app() から呼ばれる。"""

    @app.context_processor
    def inject_seo() -> dict:
        """全ページのHTMLから使える値を足す。

        context_processor = ここに書いた値が、render_template に渡さなくても
        どのページのHTMLからでも使えるようになる仕組み。

        ★説明文(description)はここに入れていない。
          context_processor の値は render_template で渡した値に必ず負けるので、
          ここに書くと「ページ側で渡したのに反映されない」形になる。
          どちらを使うかの判断は base.html の {% set %} 1行で書いている。
        """
        # ★末尾のスラッシュを落とす。落とさないと画像のURLが "//static/..." になる。
        # ★本番でHTTPSになるかどうかは ProxyFix が面倒を見ている(app.py)。
        #   Nginx と Flask の間はHTTPなので、それが無いと http:// を出してしまう。
        site_url = request.url_root.rstrip("/")

        return {
            "site_url": site_url,
            # ★request.base_url は ?以降 を含まない。
            #   ?utm_source=... が付いただけのURLを別ページとして数えられると、
            #   検索エンジンからの評価が分散する。
            "canonical_url": request.base_url,
            "ogp_image": current_app.config.get("OGP_IMAGE", ""),
        }

    @app.get("/robots.txt")
    def robots_txt():
        """検索エンジンへの案内。中身は src/web/static/robots.txt。"""
        return send_from_directory(app.static_folder, "robots.txt")

    @app.get("/favicon.ico")
    def favicon():
        """タブのアイコン。

        ★<link rel="icon"> を書いていても、ブラウザは最後の手段として
          サイト直下の /favicon.ico を取りに来る。
          ファイルが無ければ404が返るだけで害はない。
        """
        return send_from_directory(app.static_folder, "favicon.ico")
