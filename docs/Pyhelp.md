# Python の書き方

このテンプレートを触るのに必要な **Python の書き方だけ** をまとめたページです。
Python を一から全部学ぶ教科書ではありません。**ここに書いてあることが読めれば、テンプレートのコードは読めます。**

| あなたは | 読み方 |
| --- | --- |
| 🌱 プログラミングがはじめて | 上から順に読んでください。灰色の「他の言語を知っている人へ」は**開かずに飛ばして**大丈夫です |
| 🛠️ 他の言語(Java / PHP / JavaScript など)を書ける | 下の **[早見表](#他の言語を知っている人への早見表)** でほぼ足ります。気になる所だけ各章の灰色の部分を開いてください |

分からなくなったら、この順で調べてください。

1. このページで書き方を確かめる
2. 実際に動いているコードを読む(`src/web/demo/` の中が全部お手本です)
3. それでも分からなければ、人(または AI)に聞く

---

## 他の言語を知っている人への早見表

<details>
<summary>開く(Java / PHP / JavaScript との対応表)</summary>

| やりたいこと | Java / PHP / JavaScript | Python |
| --- | --- | --- |
| ブロック | `{ }` | **インデント(スペース4つ)** + 行末の `:` |
| 文の終わり | `;` | 改行(`;` は書かない) |
| 変数 | `String s = "a";` / `$s = "a";` / `let s = "a";` | `s = "a"`(型注釈は任意:`s: str = "a"`) |
| 命名 | `userName` | `user_name`(snake_case)。定数は `MAX_SIZE`(慣習のみ、再代入は防げない) |
| 真偽値 / null | `true` / `false` / `null` | `True` / `False` / `None` |
| 論理演算 | `&&` `\|\|` `!` | `and` `or` `not` |
| else if | `else if` | `elif` |
| インクリメント | `i++` | `i += 1`(`++` は無い) |
| for | `for (i = 0; i < n; i++)` | `for x in items:` / `for i in range(n):` / `for i, x in enumerate(items):` |
| 配列 / リスト | `ArrayList` / `array` / `Array` | `list`:`[1, 2]`。`items[-1]` で末尾 |
| 連想配列 | `HashMap` / 連想配列 / `Object` | `dict`:`{"k": "v"}`。安全に取るなら `d.get("k", 既定値)` |
| 文字列の埋め込み | `` `${name}` `` | `f"{name}"` |
| null 判定 | `x == null` | `x is None` |
| 空判定 | `s == null \|\| s.isEmpty()` | `if not s:`(空文字・空リスト・0・None は偽) |
| 関数 | `function f(a) {}` | `def f(a, b=1):`(既定値・キーワード引数あり) |
| 複数の戻り値 | オブジェクトで包む | `return a, b` → `x, y = f()` |
| this | `this`(暗黙) | `self`(メソッドの第1引数に**明示**) |
| コンストラクタ | クラス名と同じ / `__construct` / `constructor` | `__init__` |
| 継承 | `extends` | `class Child(Parent):` |
| private | `private` | 先頭に `_`(慣習のみ) |
| 例外 | `try / catch` | `try / except` |
| リソース解放 | try-with-resources | `with` |
| アノテーション | `@Override` 等 | デコレータ `@...`(関数を受け取って包む関数。Flask はルート登録に使う) |

</details>

---

## 0. 最初の3つのルール

Python には、**見た目でびっくりしやすい決まり**が3つあります。

### ① 字下げ(行頭のスペース)に意味がある

```python
if not title:
    return "空です"
```

`if` の次の行が右に下がっています。この**スペース4つ**が「ここは `if` の中身だよ」という意味です。
字下げがずれると、**動くけれど思った動きにならない**、という厄介な壊れ方をします。

> 心配は要りません。VSCode で **Tab キーを押すとスペース4つが入る**設定にしてあり、
> 保存すると自動で整えてくれます(`.vscode/settings.json`)。自分で数える必要はありません。

### ② 行の終わりに `;` は付けない

改行がそのまま「文の終わり」です。

### ③ 型を書かない

```python
title = "こんにちは"    # 文字
count = 3              # 数字
```

入れたもので、Python が「これは文字」「これは数字」と自分で判断します。

<details>
<summary>他の言語を知っている人へ</summary>

- `{ }` の代わりにインデントがブロックを決めます。行末の `:` を忘れると `SyntaxError` です
- 型が無いわけではなく、動的型付けです。`"1" + 1` は `TypeError` になります(暗黙の変換はしません)
- このテンプレートのコードは型ヒント(`def f(x: int) -> str:`)を一部で付けていますが、実行時には検査されません

</details>

---

## 1. 変数

**変数**は、値に**名前を付けて取っておく入れ物**です。

```python
user_name = "太郎"
max_size = 200
```

- 名前は**小文字とアンダースコア**でつなぐのが Python の習慣です(`user_name`)
- **全部大文字**の名前は「この値は変えないでね」という目印です(`MAX_SIZE = 200`)

---

## 2. もし〜なら(条件分岐)

```python
if count > 10:
    print("たくさん")
elif count > 5:
    print("ふつう")
else:
    print("すこし")
```

- `elif` は「そうでなくて、もし〜なら」です
- 行の終わりの **`:`(コロン)を忘れやすい**ので注意してください

### 「かつ」「または」「でない」

```python
if title and len(title) <= 200:    # title があって、かつ 200文字以下なら
    ...
```

| 意味 | 書き方 |
| --- | --- |
| かつ | `and` |
| または | `or` |
| でない | `not` |

### 「空っぽ」かどうかを調べる

空の文字 `""`、空のリスト `[]`、`0`、`None`(何もない)は、どれも**「いいえ」扱い**になります。
だから、空かどうかは `not` だけで調べられます。

```python
if not title:
    return jsonify({"error": "内容を入力してください。"}), 400
```

これは `src/web/demo/api.py` に実際に出てくる書き方です。「タイトルが空なら、エラーを返す」という意味です。

<details>
<summary>他の言語を知っている人へ</summary>

- 条件式を `( )` で囲む必要はありません
- `if not title:` は `title == null || title.isEmpty()` に相当します。空文字・空コレクション・`0`・`None` が偽(falsy)です
- 三項演算子は `a if 条件 else b` の順で書きます

</details>

---

## 3. くり返し

Python の `for` は、**中身を1つずつ取り出す**形で書きます。

```python
fruits = ["みかん", "りんご", "ぶどう"]

for fruit in fruits:
    print(fruit)
```

> 箱の中のみかんを、1個ずつ取り出して手に持つイメージです。

### 決まった回数くり返す

```python
for i in range(5):      # 0, 1, 2, 3, 4 の5回
    print(i)
```

### 何番目かも知りたい

```python
for i, fruit in enumerate(fruits):
    print(i, fruit)     # 0 みかん / 1 りんご / 2 ぶどう
```

### 1を足すとき

```python
count += 1              # count = count + 1 と同じ
```

<details>
<summary>他の言語を知っている人へ</summary>

- C 系の `for (i = 0; ...)` はありません。`range()` か `enumerate()` を使います
- `i++` / `i--` はありません。`+= 1` を使います
- `while` は他の言語と同じです

</details>

---

## 4. リストと辞書 ← ★いちばんよく使う

### リスト:順番に並べたもの

```python
fruits = ["みかん", "りんご", "ぶどう"]

fruits[0]              # "みかん"(番号は 0 から数える)
fruits[-1]             # "ぶどう"(マイナスは後ろから)
len(fruits)            # 3(いくつあるか)
fruits.append("かき")   # 最後に足す
```

### 辞書:名前と値をセットにしたもの

```python
todo = {"id": 1, "title": "みかんを買う", "is_done": False}

todo["title"]          # "みかんを買う"
todo["is_done"] = True # 書き換える
```

> 辞書は、**ラベルの付いた引き出し**のようなものです。「title」の引き出しを開けると、中身が出てきます。

画面(JavaScript)に送るデータも、ほとんどがこの辞書の形です。
`src/web/demo/models.py` の `to_dict()` は、データベースの1件をこの形に変えています。

### ★ `.get()` を使うと、うっかり止まらない

```python
data["title"]            # title の引き出しが無いと、エラーで止まる
data.get("title", "")    # 無ければ "" を返してくれる。止まらない
```

> 自動販売機に例えると、`[ ]` は「売り切れのボタンを押すと機械が止まる」、
> `.get()` は「売り切れなら代わりの品を出してくれる」です。

**利用者から送られてきたデータには、必ず `.get()` を使ってください。** 何が送られてくるか分からないからです。

<details>
<summary>他の言語を知っている人へ</summary>

- `list` は可変長配列、`dict` は挿入順を保持するハッシュマップです
- `dict` のリテラルは JSON とほぼ同じ見た目です。Flask では `jsonify(dict)` や、ビュー関数から `dict` を返すだけで JSON レスポンスになります
- 存在しないキーへの `d["k"]` は `KeyError` です。外部入力には `d.get("k", default)` を使います

</details>

---

## 5. 関数:処理に名前を付ける

**関数**は、ひとまとまりの処理に名前を付けたものです。料理のレシピ1枚のようなものです。

```python
def greet(name):
    return "こんにちは " + name

greet("太郎")    # "こんにちは 太郎"
```

- `def` で始めて、`( )` の中に**受け取る値**、`return` で**返す値**を書きます

### 何も渡されなかったときの値を決める

```python
def greet(name, greeting="こんにちは"):
    return greeting + " " + name

greet("太郎")              # "こんにちは 太郎"
greet("太郎", "おはよう")   # "おはよう 太郎"
```

### 2つ以上の値を返す

```python
def check_db():
    return "ok", ""

status, message = check_db()   # status に "ok"、message に "" が入る
```

`src/web/demo/routes.py` の `_check_db()` がこの書き方です。

### 名前の先頭の `_`

```python
def _safe_redirect_target(target):    # src/web/auth/routes.py より
```

先頭の `_` は「**このファイルの中だけで使う関数です**」という目印です。外から呼んでも動きますが、呼ばないのがお約束です。

<details>
<summary>他の言語を知っている人へ</summary>

- 引数の既定値・キーワード引数(`greet(name="太郎")`)が使えます。オーバーロードはありません
- 複数の戻り値は実際にはタプルです(`return a, b` = `return (a, b)`)
- `_` 始まりは慣習上の private です。アクセス制御はありません
- ★既定値に `[]` や `{}` を書くのは避けてください(呼び出しをまたいで共有されます)

</details>

---

## 6. クラス:データと処理のまとまり

**クラス**は「設計図」です。設計図から作った1つ1つの実物を**オブジェクト**と呼びます。

```python
class Todo:
    def __init__(self, title):    # 作るときに最初に動く
        self.title = title

    def show(self):                # ★1つ目には必ず self と書く
        return self.title

todo = Todo("みかんを買う")         # 設計図から1つ作る
todo.show()                        # "みかんを買う"
```

- `self` は「**この実物自身**」という意味です
- クラスの中の関数には、**1つ目に必ず `self`** を書きます(書き忘れると呼んだ瞬間にエラーになります)

### このテンプレートでは「表の設計図」として出てくる

```python
class Todo(db.Model):
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
```

`src/web/demo/models.py` より。**データベースの表の形**を書いています。
`title` という列(最大200文字、空は禁止)と、`is_done` という列(はい/いいえ)がある、という意味です。
ここには計算も `if` も出てきません。**項目を並べるだけ**の場所です。

<details>
<summary>他の言語を知っている人へ</summary>

- `__init__` がコンストラクタ、`self` が `this` です。`self` はメソッドの第1引数として**明示**します
- `class Todo(db.Model):` の `( )` は継承です。SQLAlchemy の宣言的マッピングで、クラス属性の `db.Column` がテーブル定義になります
- このテンプレートは Flask-SQLAlchemy(SQLAlchemy 2 系)です。取得は `db.session.get(Todo, id)` や `db.session.query(Todo)...` の形を使っています

</details>

---

## 7. 文字

### つなげる

```python
"こんにちは " + name
```

### ★ f-string(とても便利)

文字の前に `f` を付けると、`{ }` の中に変数をそのまま書けます。

```python
name = "太郎"
f"こんにちは {name} さん"    # "こんにちは 太郎 さん"
```

### よく使う道具

```python
title.strip()      # 前後の空白を取る
title.lower()      # 小文字にする
len(title)         # 文字数
str(3)             # 数字 → 文字
int("3")           # 文字 → 数字
```

`src/web/demo/api.py` の `str(data.get("title", "")).strip()` は、
「送られてきた title を文字として受け取り、前後の空白を取る」を1行でやっています。
空白だけを送ってくる人がいても弾けるようにするためです。

<details>
<summary>他の言語を知っている人へ</summary>

- f-string は JavaScript のテンプレートリテラル相当です(`${}` ではなく `{}`)
- 文字列は不変(immutable)です。`len()` はコードポイント数なので、日本語も1文字=1と数えます

</details>

---

## 8. `None`:何もない

```python
todo = db.session.get(Todo, todo_id)
if todo is None:
    return jsonify({"error": "見つかりませんでした。"}), 404
```

`None` は「**何もない**」を表す特別な値です。探したけれど見つからなかった、などのときに出てきます。
`None` かどうかは **`is None`** で調べます(`== None` とは書かないのが Python の習慣です)。

<details>
<summary>他の言語を知っている人へ</summary>

`None` は `null` 相当のシングルトンなので、同一性比較 `is` を使います。

</details>

---

## 9. `import`:他の部品を使えるようにする

```python
from flask import jsonify, request    # flask という部品の中から、jsonify と request を使う
import json                           # json という部品をまるごと使う
```

- **ファイルの一番上**に書きます
- 使っていない `import` は、保存したときに VSCode が教えてくれます。消して構いません
- ただし **`# noqa: F401` と書いてあるものは消さないでください。** 「使っていないように見えるけれど、読み込むこと自体に意味がある」という目印です

---

## 10. このテンプレートで見かける、Python らしい書き方

### `@` で始まる行(デコレータ)

```python
@main_bp.get("/mypage")
def my_page():
    ...
```

**関数に貼るシール**です。「この関数は、`/mypage` を開かれたときに動かしてね」という注文を、関数の外から貼っています。

> 荷物に「われもの注意」のシールを貼るのと同じです。中身(関数)は変えずに、扱い方だけ指定しています。

よく出てくるもの:`@main_bp.get(...)`(開いたとき)、`@main_bp.post(...)`(送られてきたとき)、`@login_required`(ログインした人だけ)

### `[ ... for ... in ... ]`(まとめて変換)

```python
[todo.to_dict() for todo in todos]
```

「全部の Todo を1つずつ辞書に変えて、リストにする」を1行で書いています。次と同じ意味です。

```python
result = []
for todo in todos:
    result.append(todo.to_dict())
```

**自分で書けなくても大丈夫です。** 読めれば十分です。

### `with`(使い終わったら片付けてくれる)

```python
with open("memo.txt") as f:
    text = f.read()
```

ファイルを開いて読み、**終わったら自動で閉じて**くれます。

### `try` / `except`(失敗したときの受け止め)

```python
try:
    number = int(text)
except ValueError:
    return jsonify({"error": "数字を入力してください。"}), 400
```

`try` の中で失敗したら、`except` の中が動きます。

> ★`try` で囲むのは、「**利用者の入力のせいで失敗しうる所**」だけにしてください。
> 何でも囲むと自分のバグまで隠れてしまい、「エラーは出ないのに動かない」というつらい状態になります。

<details>
<summary>他の言語を知っている人へ</summary>

- デコレータは「関数を受け取って関数を返す関数」です。Flask の `@bp.get(path)` はルーティング登録に使われています
- リスト内包表記はジェネレータ式・辞書内包表記(`{k: v for ...}`)もあります
- `with` はコンテキストマネージャ(try-with-resources / `using` 相当)です
- `except Exception:` で広く捕まえるのは避けてください。Flask はハンドラ外の例外を 500 として `errors.py` に回します

</details>

---

## 11. ★つまずきポイント集

よく起きる順です。**エラーが出たら、まずここを見てください。**

| 出たエラー・症状 | 原因と直し方 |
| --- | --- |
| `IndentationError` / 動くけど動きが変 | 字下げがずれています。スペース4つに揃えてください |
| `SyntaxError`(`if` や `def` の行) | 行の終わりの `:` を忘れています |
| `NameError: name 'true' is not defined` | `True` / `False` / `None` は**先頭が大文字**です |
| `TypeError: ... missing 1 required positional argument` | クラスの中の関数に `self` を書き忘れています |
| `KeyError` | 辞書に無い名前を `[ ]` で取っています。`.get()` に変えてください |
| `NameError: name 'render_template' is not defined` | `import` を書き忘れています。ファイルの上に `from flask import render_template` を足す |
| 表の形を変えたのに、データベースが変わらない | `flask init-db` は無い表を作るだけです。作り直してください(★データは消えます):`flask drop-db` → `flask init-db`(詳しくは [SETUP.md](SETUP.md#3-データベースの操作)) |
| HTML に書いたのに画面に出ない | `{% block content %}` 〜 `{% endblock %}` の外に書いています。中に入れてください |

---

## 12. 練習にちょうどいい場所

**いちばん勉強になるのは `src/web/demo/` の中を読むこと**です。実際に動いているコードなので、間違いがありません。

| 読むファイル | 分かること |
| --- | --- |
| `src/web/demo/models.py` | クラスの書き方 / データベースの表の作り方 |
| `src/web/demo/api.py` | 関数 / 辞書 / `if` / デコレータ |
| `src/web/demo/routes.py` | 2つの値を返す書き方 / 画面に値を渡す方法 |
| `src/web/models.py` | 自分の表を書く場所(見本がコメントで入っています) |

### 最初の練習メニュー

1. `src/web/demo/api.py` の `list_todos` を読んで、**何をしているか自分の言葉で説明してみる**
2. `src/web/models.py` のコメントを参考に、表の設計図を1つ書いてみる
3. `docker compose exec web flask init-db` を打って、[DBeaver](SETUP.md#35-データベースの中身を目で見るdbeaver) で**本当に表ができたのを見る**
4. `src/web/routes.py` に、画面を返す関数を1つ書いてみる([README の手順](../README.md#ページを1枚増やしてみる))

**3番が特に大事です。** 自分の書いたコードが表になって現れるのを一度見ると、その後の話がすっと入ります。

---

## おまけ:Python と付き合うコツ

**書いたら、すぐ動かしてください。**

完璧に書き上げてから動かそうとすると、エラーが10個まとめて出てきて、どこが原因か分からなくなります。
1行足したら保存して、ブラウザで確かめる。表示されたら次を足す。この繰り返しがいちばん速いです。

このテンプレートは**保存するだけで自動で反映される**ので、この進め方がやりやすくなっています。

<details>
<summary>他の言語を知っている人へ</summary>

静的型付け言語に慣れていると、実行するまで型の間違いが分からないのは不安に感じるかもしれません。
`docker compose exec web ruff check src/` で書き方の検査ができます。型の検査が必要な規模になったら、
mypy / pyright の導入か、Go の兄弟テンプレート(Gin版・Echo版)を検討してください。

</details>
