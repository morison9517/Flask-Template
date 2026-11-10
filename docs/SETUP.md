# 毎日の使い方と、困ったとき

このファイルは**開発中にいつでも開く手引き**です。分からなくなったら、人に聞く前にまずここを見てください。

| こんなとき | 見るところ |
| --- | --- |
| はじめて動かす | [START.md](START.md)(道具の入れ方から順番に説明しています) |
| 毎日の起動・終了 | [2. 毎日の操作](#2-毎日の操作) |
| データベースを触りたい | [3. データベースの操作](#3-データベースの操作) |
| エラーが出た・動かない | [5. 困ったとき](#5-困ったとき) |
| Python の書き方が分からない | [Pyhelp.md](Pyhelp.md) |
| インターネットに公開したい | [DEPLOY.md](DEPLOY.md) |
| 言葉が分からない | [GLOSSARY.md](GLOSSARY.md) |

> **経験者向けの要点**:すべて Docker Compose 経由です(ホストに Python は不要)。
> 依存は uv、DB は MySQL 8.4(ホスト側 3307)、スキーマは `flask init-db`(`db.create_all()`)で作成、
> 変更は `drop-db` → `init-db` の作り直しです。コードは保存で自動リロードされます。

---

## 1. 初回セットアップ

> **[START.md](START.md) を最後まで進めた人は、ここは飛ばして構いません。** 同じことの短い版です。

用意するもの:**Docker Desktop**(起動しておく)・**Git**・**VSCode**(おすすめ)。Python は要りません。
Git と GitHub の準備がまだなら、Progate の記事([Windows](https://prog-8.com/docs/git-env-win) / [Mac](https://prog-8.com/docs/git-env))の1〜4章を済ませてください。

```bash
# ① テンプレートを持ってくる
git clone https://github.com/morison9517/Flask-Template.git
cd Flask-Template

# ② 設定ファイル(金庫)を作る。中身はそのままで動く
cp .env.example .env               # Windows の場合: Copy-Item .env.example .env

# ③ 起動する(初回は3〜5分かかる)
docker compose up --build
```

次の行が出たら起動しています。

```text
web-1  | * Running on http://0.0.0.0:5000
```

**ターミナルをもう1つ開いて**、データを入れる表を作ります(初回だけ)。

```bash
docker compose exec web flask init-db
```

`DBに表を作りました` と出ればOKです。ブラウザで <http://localhost:5000> を開き、

- **「セットアップ完了 🎉」で、データベースが「接続OK」** → 成功です
- 「未接続」と出る → データベースがまだ起動中かもしれません。10秒待って再読み込み
- 画面が出ない → [5. 困ったとき](#5-困ったとき) へ

> **なぜターミナルを2つ使うの?**
> 1つ目のターミナルは、アプリが動いている間ずっと「今なにが起きているか」(ログ)を流し続けています。
> そこには新しいコマンドを打てないので、もう1つ開いて命令します。

---

## 2. 毎日の操作

### 始めるとき

```bash
docker compose up
```

Docker Desktop が起動していることを先に確認してください(クジラのアイコン🐳)。

### 終わるとき

起動したターミナルで **`Ctrl + C`** を押す。それだけです。

```bash
# 箱(コンテナ)ごと完全に片付けたいとき。データは消えません
docker compose down
```

### コードを直したとき

**何もしなくていいです。** 保存すれば自動で反映されます。

| 直したもの | どうなるか |
| --- | --- |
| Python(`.py`) | アプリが自動で再起動する。2〜3秒待ってブラウザを再読み込み |
| HTML / CSS / JavaScript | ブラウザを再読み込みするだけ |

> CSS を直したのに見た目が変わらないときは、ブラウザが前の内容を覚えています(キャッシュ)。
> `Ctrl + Shift + R`(Mac は `Command + Shift + R`)で強制的に読み直せます。

### エラーの内容を見たいとき

```bash
docker compose logs -f web
```

**エラーが出たら、まずここです。** 赤い文字の**いちばん下のあたり**に原因が書いてあることが多いです。
`-f` は「流れ続ける」の意味で、見終わったら `Ctrl + C` で抜けます。

### 箱の中で作業したいとき

```bash
docker compose exec web bash
```

アプリが動いている箱(コンテナ)の中のターミナルに入ります。出るときは `exit` です。
ふだんは使いません。上級者向けの非常手段だと思ってください。

---

## 3. データベースの操作

### 表を作る / 新しい表を足したとき

`src/web/models.py` に**新しいクラス(表の設計図)を足した**あとに打ちます。

```bash
docker compose exec web flask init-db
```

既にある表はそのまま残り、**無い表だけ**が作られます。データは消えません。

### 表の形を変えたとき(列を足した・型を変えた)

**既にある表の形は、自動では変わりません。** いったん全部消して作り直します。

```bash
docker compose exec web flask drop-db
docker compose exec web flask init-db
```

> ⚠️ **中のデータは全部消えます。** 開発中はこれがいちばん早くて確実です。
> 公開した後はこの方法が使えないので、**公開する前に表の形を固めておく**のが安全です。
> (データを残したまま形を変えたくなったら、[Django版](https://github.com/morison9517/Django-Template) への引っ越しを考える時期です)

### どうしてもおかしいとき(最終手段)

```bash
docker compose down -v
docker compose up --build
docker compose exec web flask init-db        # 別のターミナルで
```

`-v` は**データの保管庫(ボリューム)ごと消す**指定です。データベースが完全にまっさらに戻ります。

---

## 3.5 データベースの中身を目で見る(DBeaver)

**DBeaver** は、データベースの中身を Excel のように見られる無料のアプリです。
<https://dbeaver.io/download/> から「Community Edition」を入れてください。

### つなぎ方

`docker compose up` でアプリを起動したまま、DBeaver で「新しい接続」→「MySQL」を選び、次を入れます。

| 項目 | 値 |
| --- | --- |
| Server Host | `localhost` |
| **Port** | **`3307`** |
| Database | `hack_app` |
| Username | `hack_user` |
| Password | `hack_password` |

> ⚠️ **ポートは 3306 ではなく 3307 です。**
> パソコンに元から MySQL が入っている人とぶつからないよう、番号をずらしてあります。

### 「Public Key Retrieval is not allowed」と出たら

接続設定の「ドライバのプロパティ(Driver properties)」で、次の2つを変えてください。
手元の開発用データベースなので、これで問題ありません。

| プロパティ | 値 |
| --- | --- |
| `allowPublicKeyRetrieval` | `true` |
| `useSSL` | `false` |

### 管理者として入りたいとき

表を直接消すなどの強い操作は、`hack_user` では権限が足りないことがあります。
Username を `root`、Password を `root_password` にすると管理者で入れます。

### 見ておくと理解が早いところ

- `users` 表 → `models.py` に書いた設計図が、そのまま表の形になっています
- `users` の `password_hash` 列 → パスワードが**元に戻せない形**で保存されているのが分かります
- `demo_todos` 表 → デモ画面の Todo です。`demo_` で始まる表は消しても構いません

---

## 4. 部品(ライブラリ)を足したいとき

例:画像を扱う `Pillow` を使いたくなった場合。

**① `pyproject.toml` の `dependencies` に1行足す**

```toml
dependencies = [
    "Flask",
    ...
    "Pillow",   # ← 追加
]
```

**② 箱に反映する**

```bash
docker compose exec web uv sync
docker compose restart web
```

**③ 仲間と共有する**(1人で作っているなら不要)

`pyproject.toml` と `uv.lock` の2つを commit して push してください。
(commit / push が分からなければ [用語集の Git の項目](GLOSSARY.md#git-と-github) を、
GitHub の準備がまだなら Progate の記事([Windows](https://prog-8.com/docs/git-env-win) / [Mac](https://prog-8.com/docs/git-env))を見てください)

> ⚠️ これを共有しないと、仲間の環境で `ModuleNotFoundError` が出ます。
> pull した側は `docker compose exec web uv sync` を打てば揃います。

---

## 4.5 部品を新しい版にする

部品には後から弱点(脆弱性)が見つかることがあります。直った版が出ても、**入れ替えない限り古いまま**です。
数日〜数週間の開発ならあまり気にしなくて構いませんが、公開したまま長く置くなら、ときどき上げてください。

### 自動で知らせてもらう

`.github/dependabot.yml` が入っています。GitHub に上げておくと、**月に1回、更新をまとめた提案(プルリクエスト)**が届きます。
届いたら、手元に取り込んで `docker compose up --build` で動くか確かめ、問題なければ取り込み(マージ)ます。

> 急ぎの修正(セキュリティ更新)は、GitHub の画面で別に有効にします:
> リポジトリの **Settings → Advanced Security → Dependabot security updates**

### 手で上げる

```bash
docker compose exec web uv lock --upgrade
docker compose exec web uv sync
```

動作を確かめてから、`pyproject.toml` と `uv.lock` を commit します。

---

## 5. 困ったとき

上から、よく起きる順に並べています。

### 画面が出ない / つながらない

```bash
docker compose ps
```

`web` と `db` の両方が `running`(または `Up`)になっているか見ます。

- `web` がいない・止まっている → `docker compose logs web` でエラーを読む
- `db` が `starting` → まだ起動中です。30秒待つ
- そもそもコマンドが失敗する → **Docker Desktop が起動していません。** クジラのアイコンを確認

### 「port is already allocated」と出る

**その番号を、別のアプリがもう使っています。** `compose.yml` の番号を変えます。

- `5000` の場合(Mac でよく起きる):`"5000:5000"` を `"5001:5000"` に変え、<http://localhost:5001> を開く
- `3307` の場合:`"3307:3306"` を `"3317:3306"` に変える

> **左の数字だけ**を変えてください。右はアプリの中の番号なので、変えると動かなくなります。

### 「ModuleNotFoundError: No module named '○○'」

部品が箱に入っていません。誰かが部品を足した直後によく起きます。

```bash
docker compose exec web uv sync
docker compose restart web
```

### 「Can't connect to MySQL server」

データベースの起動待ちです。少し待って再読み込みしてください。それでもだめなら:

```bash
docker compose restart web
```

### 「Bad Request / The CSRF token is missing」

フォームに**整理券(CSRFトークン)を入れ忘れています**。`<form>` の中に次の1行があるか確認してください。

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
```

JavaScript から送っている場合は、`main.js` の `api.post()` を使ってください(整理券が自動で付きます)。

### 送った値が届かない / 空っぽになる

HTML の `name="○○"` と、Python の `request.form.get("○○")` の**文字が完全に一致しているか**確認してください。
原因の8割はここのズレです。

### 画面に書いたはずの文字が出ない

`{% block content %}` 〜 `{% endblock %}` の**外に書いていないか**確認してください。
外側に書いたものは、エラーも出ずに無視されます。

### VSCode に「パッケージ 'Flask' がインストールされていません」と出る

**無視して大丈夫です。** 部品は箱の中にあるので、アプリは正しく動きます。
VSCode は箱の外(あなたのパソコン)で動いているので、箱の中が見えていないだけです。

### それでも分からないとき

人に聞くときは、次の3つをセットで伝えてください。**これが揃っていれば、誰でも助けられます。**

1. 何をしようとしたか
2. `docker compose logs web` の最後の20行
3. ブラウザに出ている画面(スクリーンショット)

> AI(ChatGPT や Claude など)に聞くときも同じです。この3つを貼ると、的確な答えが返ってきます。

---

## 6. どうしても Docker が動かない人向け(非常口)

**ふだんは使わないでください。** Docker がどうしても動かず、時間も無いときだけの手段です。

```powershell
# uv を入れる(Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 部品を入れる
uv sync

# データベースだけ Docker で動かす
docker compose up -d db

# .env の DB_HOST を db から 127.0.0.1 に、DB_PORT を 3306 から 3307 に変えてから
$env:PYTHONPATH="src"; $env:FLASK_APP="web.app"; uv run flask run --debug
```

> `DB_HOST` を変える理由:箱の中からは `db` という名前で呼べますが、
> 箱の外(あなたのパソコン)から見ると「このパソコンの3307番」になるためです。
