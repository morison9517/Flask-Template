# =============================================================================
# デモ用のAPI(画面ではなくデータを返す受付)
#
#   ★これは動作確認用です。自分たちのAPIは src/web/api.py に書きます。
#     書き方の見本としてどうぞ。
#
# ▼ routes.py との違い
#
#   routes.py … HTMLを丸ごと返す。ページが切り替わる。
#   api.py    … データだけ返す。ページを切り替えずに一部だけ書き換えられる。
#
#   使い分けの目安:
#     ページ移動を伴う操作(ログイン、詳細ページへ移動) → routes.py
#     その場で追加・削除・チェック(いいね、Todo追加)   → api.py
#
# ▼ JavaScript側との対応
#
#   demo/templates/demo/index.html の中のJSから呼ばれている。
#   送受信の作法(整理券を付ける、エラーを拾う)は main.js の api がやるので、
#   自分たちのページでは api.post("/api/todos", { title: "牛乳" }) と書くだけでよい。
# =============================================================================

from flask import jsonify, request

from web.demo import demo_bp
from web.demo.models import Todo
from web.extensions import db


@demo_bp.get("/__demo/api/todos")
def list_todos():
    """一覧を返す。"""
    # limit(100) で取りすぎを防ぐ。
    # ★上限が無いと、データが増えたときに画面が固まる。
    todos = db.session.query(Todo).order_by(Todo.id.desc()).limit(100).all()

    return jsonify({"todos": [todo.to_dict() for todo in todos]})


@demo_bp.post("/__demo/api/todos/create")
def create_todo():
    """1件追加する。"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "送信内容の形式が正しくありません。"}), 400

    title = str(data.get("title", "")).strip()

    # ★入力チェックは必ずサーバー側でもやる。
    #   画面側(HTMLのrequiredやJS)のチェックは、開発者ツールから素通りできる。
    if not title:
        return jsonify({"error": "内容を入力してください。"}), 400
    if len(title) > 200:
        return jsonify({"error": "200文字以内で入力してください。"}), 400

    # ★デモのTodoは持ち主を持たない(本番のUserに紐付けない)。
    #   理由は demo/models.py のコメント参照。紐付けの書き方も同じ場所に見本がある。
    todo = Todo(title=title)

    # ★add したあと commit して初めてDBに書き込まれる。
    db.session.add(todo)
    db.session.commit()

    # 201 = 「新しく作った」を表す返事。
    return jsonify({"todo": todo.to_dict()}), 201


@demo_bp.patch("/__demo/api/todos/<int:todo_id>")
def toggle_todo(todo_id: int):
    """済み / 未済 を切り替える。

    <int:todo_id> = URLのこの部分を数字として受け取り、引数に渡す指定。
    ★int を指定しているので、数字でないURLはここに届く前に404になる。
    """
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "見つかりませんでした。"}), 404

    todo.is_done = not todo.is_done
    db.session.commit()

    return jsonify({"todo": todo.to_dict()})


@demo_bp.delete("/__demo/api/todos/<int:todo_id>/delete")
def delete_todo(todo_id: int):
    """1件消す。"""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "見つかりませんでした。"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"deleted": todo_id})
