# =============================================================================
# デモ用のデータの形。
#
#   ★このフォルダは開発モードのときだけ読み込まれるので、
#     この表(demo_todos)は本番のDBには作られません。
#
#     仕組み:SQLAlchemyは「読み込まれたクラス」しか表として覚えない。
#     本番では demo/ を一切読み込まないので、demo_todos は存在しないまま。
#
#   自分たちの表は src/web/models.py に書きます。書き方の見本としてどうぞ。
#
# ▼ ★デモは本番のモデルに一切ぶら下がりません
#
#   以前ここには User への紐付け(ForeignKey と relationship)がありましたが、
#   外しました。紐付けがあると、
#     ・デモ用の表から本番の users 表に向けてDBに制約が作られる
#     ・本番の User クラスに user.todos という項目が生える(backref)
#   という形で、消したはずのデモが本番側に痕跡を残します。
#
#   デモはデモだけで完結させ、本番側には何も残さない方針にしています。
#   紐付けの書き方の見本は src/web/models.py にあります。
# =============================================================================

from web.extensions import db


class Todo(db.Model):
    """やることリスト1件分(デモ)。"""

    # ★表の名前に demo_ を付けている理由
    #   "todos" のままだと、チームが自分たちのTodoを作った瞬間に
    #   名前がぶつかって、アプリが起動しなくなる:
    #       InvalidRequestError: Table 'todos' is already defined
    #   デモが名前を1つ占領しないよう、必ず demo_ を付ける。
    __tablename__ = "demo_todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    def to_dict(self) -> dict:
        """JavaScriptに渡せる形(JSONにできる辞書)に変換する。

        ★ここで返す形が、そのままJavaScript側で受け取る形になる。
          項目名を変えるときは demo/templates/demo/index.html のJSも一緒に直す。
        """
        return {
            "id": self.id,
            "title": self.title,
            "is_done": self.is_done,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Todo {self.id}: {self.title}>"
