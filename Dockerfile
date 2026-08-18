# =============================================================================
# アプリを動かす箱の作り方
#
#   上から順に実行される。Dockerは「前回と同じ工程は結果を再利用」するので、
#   変わりにくい作業(部品のインストール)を先に、よく変わる作業(コードの
#   コピー)を後に書く。こうすると2回目以降のビルドが数秒で終わる。
# =============================================================================

FROM python:3.13-slim

# uv = 部品を入れる係(pipの代替で高速)。本体だけコピーするので速い。
# ★latest にすると突然の更新でビルドが壊れるのでバージョンを固定する。
COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    # ↑ printの結果をすぐ出す(ログが遅れると原因調査しづらい)
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    # ↑ ★「Pythonのコードは /app/src にある」という案内。
    #   これがあるので from web.models import User と書ける。
    FLASK_APP=web.app \
    # ↑ Flaskに起動の入口を教える。flask run / flask init-db が短く打てる。
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    # ↑ ★部品の置き場所。既定の /app/.venv だと、開発時に自分のPCの
    #   フォルダで /app が上書きされて部品が消える。だから外に置く。
    PATH="/opt/venv/bin:$PATH" \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# ★買い物リストだけ先にコピーする理由
#   全ファイルを先にコピーすると、HTMLを1文字直すたびに部品の再インストールが
#   走る。リストだけ渡せば、リストが変わらない限り再インストールは起きない。
# uv.lock* の * は「あってもなくてもいい」(初回は存在しない)。
COPY pyproject.toml uv.lock* ./

RUN uv sync

# コピーしないものは .dockerignore に書いてある。
COPY . .

EXPOSE 5000

# --host=0.0.0.0 が必要な理由:
#   指定しないと箱の中からしかアクセスできず、
#   「起動してるのに画面が出ない」状態になる。
# --debug は保存時の自動再起動。★本番では付けない(内部情報が漏れる)。
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
