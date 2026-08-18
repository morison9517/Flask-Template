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

## 使っている技術

| 分類 | 技術 |
| --- | --- |
| フロント | 素のHTML / CSS / JavaScript(Jinjaテンプレート) |
| バック | Flask 3 / SQLAlchemy |
| DB | MySQL 8.4(確認は DBeaver、ポートは **3307**) |
| 環境 | Docker Compose |
| 本番 | Nginx / AWS |
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
│   ├── templates/          お客さんが見るHTML(base.html が共通の型紙)
│   └── static/             CSS / JS / 画像
│
├── docs/                   チームで見る手順書
├── tools/                  開発中だけ使う小道具スクリプト
│
├── compose.yml             アプリとDBをまとめて動かす段取り表
├── Dockerfile              箱を組み立てるレシピ
├── pyproject.toml          買い物リスト(必要な部品の一覧)
├── uv.lock                 レシート(全員が同じバージョンを使うための記録)
│
├── .vscode/                チーム共通のエディタ設定
│
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

## ドキュメント

- **[docs/SETUP.md](docs/SETUP.md)** — 環境構築、日々の操作、DBeaverでの接続、困ったときの対処
