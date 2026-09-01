# Flask Template Demo

**Team AIB** のハッカソン用Flask開発テンプレート。
**`docker compose up` だけで、アプリとDBが揃った開発環境が立ち上がります。**

> リポジトリ名は `case_flask`、画面上の表示名は `Flask Template Demo` です。
> プロダクト名が決まったら、表示名は `src/web/templates/base.html` の
> `<title>` とヘッダーの2箇所を直してください。

---

## いきなり動かす

```bash
# 1. 金庫を作る(初回だけ)
cp .env.example .env          # Windows: Copy-Item .env.example .env

# 2. 起動する
docker compose up --build

# 3. DBに表を作る(別のターミナルで、初回だけ)
docker compose exec web flask init-db
```

→ <http://localhost:5000> を開く

うまくいかないときは **[docs/SETUP.md](docs/SETUP.md)** を見てください。困ったときの対処が全部書いてあります。

---

## 最初に出るデモページについて

起動して `/` を開くと「セットアップ完了 🎉」というデモページが出ます。
**これは消さなくて大丈夫です。** DjangoやRailsの初期画面と同じ仕組みで、条件を満たすと自動で出なくなります。

| | |
| --- | --- |
| 出る条件 | 開発モード **かつ** `src/web/routes.py` にまだ `"/"` が無いとき |
| 消える条件 | `routes.py` に `"/"` を1つ書く(それだけ) |
| 本番 | `FLASK_ENV=production` では最初から出ない。デモ用の表(`demo_todos`)もDBに作られない |
| あとで見たい | `/__demo` で開ける(開発モードのときだけ) |

```python
# src/web/routes.py にこれを書いた瞬間、デモは出なくなります
@main_bp.get("/")
def index():
    return render_template("index.html", title="ホーム")
```

デモの画面は**1枚で完結しています**(`base.html` も `style.css` も `main.js` も使いません)。
デモの役目は「セットアップが動いているか」を見せる計器なので、共通ファイルに頼らせていません。
おかげで `base.html` を自分たちの見た目に作り替えても、この計器だけは最後まで正しく動きます。
ページの書き方の見本は `src/web/templates/login.html` を見てください(`base.html` を継いだ本物のページです)。

デモ一式は `src/web/demo/` にまとまっています。不要になったらフォルダごと削除して、`app.py` の「デモ」の3行を消してください。

---

## 使っている技術

| 分類 | 技術 |
| --- | --- |
| フロント | 素のHTML / CSS / JavaScript(Jinjaテンプレート) |
| バック | Flask 3 / SQLAlchemy |
| DB | MySQL 8.4(確認は DBeaver、ポートは **3307**) |
| 環境 | Docker Compose |
| 本番 | Nginx / gunicorn / AWS(**`compose.prod.yml` に構成済み**) |
| 画像 | Pillow(送られてきたファイルが本当に画像か確かめる用) |
| 部品管理 | uv |

---

## フォルダの地図

「Flaskアプリ = 1軒のお店」だと思って読んでください。

```
case_flask/
├── src/web/                お店の建物そのもの(アプリ本体)
│   ├── app.py              全部をつなげて起動する
│   ├── config.py           設定を1か所に集める
│   ├── extensions.py       共用の道具(DB・ログイン管理・CSRF)
│   ├── models.py           データの形(DBの表)を決める
│   ├── routes.py           画面を返す受付。URL → HTML
│   ├── auth/               ログイン・新規登録
│   ├── demo/               動作確認用のデモページ(開発モード限定・触らない)
│   │                       1枚完結なので、書き方の見本は login.html を見ること
│   ├── templates/          お客さんが見るHTML(base.html が共通の型紙)
│   └── static/             CSS / JS / 画像
│
├── media/                  利用者が上げたファイル(★中身はGitHubに上げない)
│
├── docs/                   チームで見る手順書(SETUP / Pyhelp / DEPLOY)
├── tools/                  開発中だけ使う小道具スクリプト
│
├── compose.yml             アプリとDBをまとめて動かす段取り表(開発用)
├── compose.prod.yml        本番用の段取り表(★開発中は使わない)
├── docker/nginx/           本番でCSSと画像を配るNginxの設定
├── Dockerfile              箱を組み立てるレシピ
├── pyproject.toml          買い物リスト(必要な部品の一覧)
├── uv.lock                 レシート(全員が同じバージョンを使うための記録)
│
├── .vscode/                チーム共通のエディタ設定
│
├── LICENSE                 使ってよい条件(MIT)
├── .env                    金庫(★GitHubに上げない)
└── .env.example            金庫の中身の見本(こちらは上げる)
```

---

## 担当ごとに触る場所

**基本的に他の人と同じファイルを触らないように分けてあります。** これでコンフリクト(変更の取り合い)がほぼ起きません。

| 担当 | 触る場所 |
| --- | --- |
| 見た目 | `src/web/templates/` `src/web/static/css/` |
| 画面の動き | `src/web/static/js/` |
| データの形 | `src/web/models.py` |
| URLと処理 | `src/web/routes.py` |
| ログイン | `src/web/auth/` |

`app.py` `extensions.py` `config.py` `compose.yml` `Dockerfile` は**土台**です。
触る必要が出たら、**先にチームに共有してから**変更してください(全員に影響します)。

---

## ページを1枚増やす手順

1. **`src/web/templates/` にHTMLを1枚置く**(`login.html` をコピーするのが早い)

   ```html
   {% extends "base.html" %}

   {% block content %}
   <h1>マイページ</h1>
   {% endblock %}
   ```

   > ヘッダーとフッターは書きません。`base.html` から自動的に付きます。

2. **`src/web/routes.py` に関数を1つ書く**

   ```python
   @main_bp.get("/mypage")
   def my_page():
       return render_template("mypage.html", title="マイページ")
   ```

3. 保存して2〜3秒待つ → <http://localhost:5000/mypage>

ログインしている人だけに見せたいときは、1行足すだけです。

```python
from flask_login import login_required

@main_bp.get("/mypage")
@login_required          # ← これを足す
def my_page():
    ...
```

---

## base.html(型紙)の仕組み

ヘッダーとフッターを全ページにコピペすると、直すときに全ファイルを回ることになります。
そこで**共通部分を1枚の「型紙」にまとめ、各ページは真ん中の中身だけを書く**形にしています。

```
base.html(型紙)                    mypage.html(中身)
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

穴は3つ用意してあります。

| 穴の名前 | 用途 |
| --- | --- |
| `content` | ページの本体(必須) |
| `head_extra` | そのページだけで使うCSS |
| `scripts` | そのページだけで使うJS |

**ヘッダーを直したいときは `base.html` を1枚直すだけ**で、全ページに反映されます。

> ★つまずきやすい点が2つあります。
>
> 1. `{% extends %}` は**必ず1行目**
> 2. `{% block content %}` の**外に書いたものは表示されない**(エラーも出ない)

---

## よく使うコマンド

| やりたいこと | コマンド |
| --- | --- |
| 起動する | `docker compose up` |
| 裏で起動する | `docker compose up -d` |
| 止める | `docker compose down` |
| エラーを見る | `docker compose logs -f web` |
| DBに表を作る | `docker compose exec web flask init-db` |
| DBを作り直す | `docker compose exec web flask drop-db` してから `init-db` |
| 箱の中に入る | `docker compose exec web bash` |
| 書き方をチェック | `docker compose exec web ruff check src/` |

---

## 3つのテンプレートの対応表

同じ構成・同じ画面で作ってあるので、1つ分かれば他も読めます。

| やること | Flask版 | Gin版 | Django版 |
| --- | --- | --- | --- |
| 起動の入口 | `src/web/app.py` | `cmd/server/main.go` | `manage.py` + `config/` |
| 設定 | `config.py` | `internal/config/` | `config/settings.py` |
| データの形 | `models.py` | `internal/models/` | `main/models.py` |
| 画面を返す | `routes.py` | `handlers/page.go` | `main/views.py` |
| ログイン | `auth/routes.py` | `handlers/auth.go` | `accounts/views.py` |
| 型紙 | `base.html`(Jinja) | `base.html`(Go) | `base.html`(Django) |
| 表を作る | `flask init-db` | 起動時に自動 | 起動時に自動 |
| 表の形を変える | 作り直し(データ消滅) | 列の追加のみ可 | **データを保ったまま変更可** |
| 管理画面 | 無い | 無い | **`/admin/`** |
| アプリのポート | 5000 | 8080 | 8000 |
| DBのポート | 3307 | 3308 | 3309 |
| 本番イメージ | 438MB | **48MB** | 913MB |

> ポートをずらしてあるので、**3つ同時に起動しても衝突しません。**

---

## ドキュメント

- **[docs/SETUP.md](docs/SETUP.md)** — 環境構築、日々の操作、DBeaverでの接続、困ったときの対処
- **[docs/Pyhelp.md](docs/Pyhelp.md)** — Pythonの書き方(コーディング経験者向けの早わかり)
- **[docs/DEPLOY.md](docs/DEPLOY.md)** — 本番に出す手順

---

## ライセンス

MIT License([LICENSE](LICENSE))

自由に使って、改造して、公開して構いません(商用も可)。
条件は「著作権表示を残すこと」だけです。
