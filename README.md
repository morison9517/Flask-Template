# Flask Template Demo

**はじめてのWebアプリを、短い期間で形にするためのひな型**です。
ログイン機能つきのWebアプリが、コマンド1つで手元のパソコンに立ち上がります。

> 中身は Python の Flask で作った Webアプリのテンプレートです。
> 数日〜数週間の個人開発やハッカソンに向けて、**読みやすさと始めやすさを優先**しています。

---

## あなたはどっち?

| | こんな人 | 最初に読むもの |
| --- | --- | --- |
| 🌱 | プログラミングはほぼ初めて。Git や Docker と言われてもピンとこない | **[はじめての人へ(docs/START.md)](docs/START.md)** |
| 🛠️ | 開発の経験がある。仕組みと使い方だけ知りたい | このページの **[経験者向け:30秒まとめ](#経験者向け30秒まとめ)** |

分からない言葉が出てきたら **[用語集(docs/GLOSSARY.md)](docs/GLOSSARY.md)** を開いてください。

---

## 何ができるの?

起動すると、こんな状態から始められます。

- **ログインの仕組みが動いている**:新規登録・ログイン・ログアウト。パスワードの安全な保存や、何度も間違えた人の締め出しも入っています
- **画面の土台がある**:ヘッダー・フッターつきの共通の型紙に、ページを1枚ずつ足していけます
- **データを保存できる**:データベース(MySQL)がつながっています
- **公開する準備もある**:インターネットに出すための設定と手順書が入っています

あとは **「何を作りたいか」の中身を書くだけ** です。

> 例えると、**内装工事が済んだ空き店舗**です。電気・水道・レジ・鍵はもう付いているので、
> あなたは「何を売るか」と「お店の飾りつけ」に集中できます。

---

## いきなり動かす

Docker Desktop と Git が入っていれば、ターミナルで次の4行です。
(何のことか分からなければ [はじめての人へ](docs/START.md) から読んでください。順番に説明しています)

```bash
git clone https://github.com/morison9517/Flask-Template.git
cd Flask-Template
cp .env.example .env          # Windows の場合: Copy-Item .env.example .env
docker compose up --build
```

起動したら、**もう1つターミナルを開いて**、データを入れる表を作ります(初回だけ)。

```bash
docker compose exec web flask init-db
```

ブラウザで **<http://localhost:5000>** を開いて「セットアップ完了 🎉」と出れば成功です。

うまくいかないときは **[docs/SETUP.md](docs/SETUP.md) の「困ったとき」** を見てください。

---

## 最初に出る「セットアップ完了」の画面について

これは**動作確認用の画面(デモ)**です。消す作業は要りません。
自分のトップページを作った瞬間に、自動で出なくなります。

| | |
| --- | --- |
| 出なくなる条件 | `src/web/routes.py` に `"/"` を1つ書く(書き方は下の「ページを1枚増やしてみる」) |
| あとで見たいとき | <http://localhost:5000/__demo>(開発中だけ) |
| 公開したサイト | 最初から出ない |
| 完全に消したいとき | `src/web/demo/` フォルダを消し、`src/web/app.py` の「デモ」の数行を消す |

---

## ページを1枚増やしてみる

**2つのファイルを触るだけです。**

**① 画面を書く** — `src/web/templates/mypage.html` を新しく作る

```html
{% extends "base.html" %}

{% block content %}
<h1>マイページ</h1>
<p>ここに好きなことを書けます。</p>
{% endblock %}
```

ヘッダーやフッターは書きません。1行目の `{% extends "base.html" %}` が、共通の型紙から自動で付けてくれます。

**② URLとつなぐ** — `src/web/routes.py` を2か所直す

```python
from flask import Blueprint, render_template     # ← render_template を足す


@main_bp.get("/mypage")                           # ← この4行をファイルの下に足す
def my_page():
    return render_template("mypage.html", title="マイページ")
```

保存して2〜3秒待ち、<http://localhost:5000/mypage> を開けば表示されます。

> `"/mypage"` を `"/"` にすると、それがトップページになります(デモの画面は自動で出なくなります)。

ログインした人だけに見せたいときは、1行足すだけです。

```python
from flask_login import login_required            # ← ファイルの上に足す


@main_bp.get("/mypage")
@login_required                                   # ← これを足す
def my_page():
    ...
```

---

## 型紙(`base.html`)の考え方

全ページに同じヘッダーをコピーすると、直すときに全部のファイルを回ることになります。
そこで**共通部分は1枚の型紙にまとめ、各ページは「真ん中の中身」だけを書きます。**

```text
base.html(型紙)                      mypage.html(中身)
┌──────────────────┐
│ ヘッダー          │
├──────────────────┤
│                  │  ←──  {% block content %}
│  ここが穴         │            <h1>マイページ</h1>
│                  │        {% endblock %}
├──────────────────┤
│ フッター          │
└──────────────────┘
```

| 穴の名前 | 何を入れるか |
| --- | --- |
| `content` | ページの本体(必ず書く) |
| `head_extra` | そのページだけで使うCSS |
| `scripts` | そのページだけで使うJavaScript |

> ★つまずきやすい点が2つあります。
>
> 1. `{% extends "base.html" %}` は**必ず1行目**に書く
> 2. `{% block content %}` の**外に書いたものは表示されない**(エラーも出ないので気づきにくい)

---

## フォルダの地図

**ふだん触るのは ★ の付いた場所だけ**です。他は土台なので、最初は気にしなくて構いません。

```text
Flask-Template/
├── src/web/                アプリ本体
│   ├── ★ routes.py         URLと画面をつなぐ(ページを増やすときに触る)
│   ├── ★ models.py         保存するデータの形を決める
│   ├── ★ templates/        画面のHTML(base.html が共通の型紙)
│   ├── ★ static/           CSS / JavaScript / 画像
│   ├── ★ config.py         サイトの名前などの設定
│   ├── auth/               ログイン・新規登録
│   ├── errors.py           エラー画面(404など)の文言
│   ├── loginlimit.py       ログインを何度も間違えた人を締め出す
│   ├── demo/               動作確認用の画面(触らなくてよい)
│   └── app.py ほか         全体をつなぐ土台
│
├── docs/                   手順書(START / SETUP / Pyhelp / DEPLOY / GLOSSARY)
├── media/                  利用者が上げたファイルの置き場
│
├── compose.yml             開発用の起動設定
├── compose.prod.yml        公開用の起動設定
├── Dockerfile              アプリを動かす「箱」の作り方
├── docker/nginx/           公開用の入口(Nginx)の設定
├── pyproject.toml          使っている部品の一覧
├── uv.lock                 部品の版の記録(全員が同じ版を使うため)
│
├── .env.example            設定の見本(これを .env にコピーして使う)
└── LICENSE                 使ってよい条件(MIT)
```

> **サイトの名前を変える**:`src/web/config.py` の `SITE_NAME` を1か所直すだけです。
> 全ページのタイトルとヘッダーに反映されます。

複数人で作るときは、**担当ごとに触るファイルを分ける**と、変更の取り合い(コンフリクト)がほぼ起きません。

| 担当 | 触る場所 |
| --- | --- |
| 見た目 | `src/web/templates/` `src/web/static/css/` |
| 画面の動き | `src/web/static/js/` |
| データの形 | `src/web/models.py` |
| URLと処理 | `src/web/routes.py` |
| ログイン | `src/web/auth/` |

---

## よく使うコマンド

| やりたいこと | コマンド |
| --- | --- |
| 起動する | `docker compose up` |
| 止める | 起動したターミナルで `Ctrl + C` |
| エラーの内容を見る | `docker compose logs -f web` |
| データを入れる表を作る | `docker compose exec web flask init-db` |
| 表を作り直す(★データは消える) | `docker compose exec web flask drop-db` のあと `init-db` |
| 書き方をチェックする | `docker compose exec web ruff check src/` |

詳しい使い方と、困ったときの対処は **[docs/SETUP.md](docs/SETUP.md)** にあります。

---

## 経験者向け:30秒まとめ

| 項目 | 内容 |
| --- | --- |
| 構成 | Flask 3 / SQLAlchemy 2 / Jinja2 / MySQL 8.4 / Python 3.13 |
| 実行環境 | Docker Compose。dev は `flask run --debug`(自動リロード)、prod は gunicorn 3 workers + Nginx |
| 依存管理 | uv(`pyproject.toml` + `uv.lock`) |
| アプリの組み立て | Application Factory(`src/web/app.py` の `create_app()`)+ Blueprint |
| 認証 | Flask-Login(セッション)。パスワードは Werkzeug のハッシュ。IP単位のログイン試行制限(DBに記録するので複数 worker でも正しく数える) |
| CSRF | Flask-WTF。フォームは `csrf_token()`、JS は `X-CSRFToken` ヘッダー(`static/js/main.js` の `api` が自動付与) |
| 設定 | `.env` → 環境変数 → `config.py` |
| 静的ファイル | `url_for('static')` に中身のハッシュを自動付与(キャッシュ破棄)。本番は Nginx が配信 |
| 本番 | `compose.prod.yml`。HTTPS は `.env` の `HTTPS_DOMAIN` で切替(Let's Encrypt / certbot)。手順は [DEPLOY.md](docs/DEPLOY.md) |
| 依存の更新 | Dependabot(月1・まとめて1PR) |
| ポート | アプリ 5000 / MySQL 3307(ホスト側) |

**あえて入れていないもの**(短期・入門向けのため):

- **マイグレーション**:`db.create_all()` のみ。表の形を変えるときは作り直し(データは消える)
- **テスト・CI**:未同梱
- **SEO / OGP**:未同梱

コード内のコメントは初心者向けに厚めです。読み飛ばして構いません。
本書の「箱」「金庫」「整理券」などの言い換えは、[用語集の対応表](docs/GLOSSARY.md#このテンプレートでの呼び方) で正式な用語と対応させています。
長期運用やチーム開発なら、下の兄弟テンプレートのほうが向いています。

---

## 物足りなくなったら

このテンプレートは「短く・簡単に」を優先しています。次のようなことが必要になったら、兄弟のテンプレートに移るのが近道です。

| 必要になったこと | 移り先 |
| --- | --- |
| 公開した後も、データを残したまま表の形を変えたい | **Django版**(マイグレーションあり) |
| データを画面から直接見たり直したりしたい | **Django版**(管理画面 `/admin/` あり) |
| 検索結果やSNSでの見え方を整えたい | Django版・Gin版・Echo版 |
| 処理の速さや、型による間違い防止がほしい | **Gin版・Echo版**(Go) |

画面(HTML/CSS/JS)の作り方と、型紙の考え方はどれも同じです。ここで覚えたことはそのまま持っていけます。

- Django版:<https://github.com/morison9517/Django-Template>
- Gin版:<https://github.com/morison9517/Gin-Template>
- Echo版:<https://github.com/morison9517/Echo-Template>

---

## 手順書の一覧

| ファイル | 中身 |
| --- | --- |
| [docs/START.md](docs/START.md) | はじめての人へ。道具の入れ方から、最初の1文字を変えるまで |
| [docs/SETUP.md](docs/SETUP.md) | 毎日の使い方、データベースの見方、困ったときの対処 |
| [docs/Pyhelp.md](docs/Pyhelp.md) | Python の書き方(はじめての人と、他の言語を知っている人の両方向け) |
| [docs/DEPLOY.md](docs/DEPLOY.md) | インターネットに公開する手順 |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | 用語集。分からない言葉はここ |

---

## ライセンス

MIT License([LICENSE](LICENSE))。
自由に使って、改造して、公開して構いません(商用も可)。条件は「著作権表示を残すこと」だけです。
