# 環境構築と日々の操作

このファイルは**困ったときに最初に見る紙**です。分からなくなったら人に聞く前にここを見てください。

---

## 0. 準備するもの(初回だけ)

| ツール | 用途 | 確認コマンド |
| --- | --- | --- |
| Docker Desktop | アプリとDBを動かす箱 | `docker version` |
| Git | ソースコードの共有 | `git --version` |
| VSCode | エディタ(推奨) | — |

**Python を自分のPCに入れる必要はありません。** Dockerの箱の中に入っているものを使います。

> Docker Desktop は**起動しておく必要があります**。タスクバーのクジラのアイコンが動いていればOKです。
> PCを再起動すると止まっていることがあるので、`docker` コマンドが失敗したらまずこれを疑ってください。

---

## 1. 初回セットアップ(1回だけ、10分程度)

### ① リポジトリを持ってくる

```bash
git clone <リポジトリのURL>
cd case_flask
```

### ② 金庫(`.env`)を作る

`.env` は**GitHubに上がっていません**(パスワードが入っているため)。見本をコピーして作ります。

```powershell
# Windows (PowerShell)
Copy-Item .env.example .env
```

```bash
# Mac / Linux
cp .env.example .env
```

そのあと、`.env` の中身をチームで共有されたものに合わせてください。
**開発中はコピーしたままの値でも動きます。**

### ③ 箱を組み立てて起動する

```bash
docker compose up --build
```

初回は部品のダウンロードで**3〜5分**かかります。2回目以降は数秒です。

ログが流れ終わって以下のような行が出たら成功です。

```
web-1  | * Running on http://0.0.0.0:5000
```

### ④ DBに棚を作る

**別のターミナルを開いて**(上のターミナルはログを流し続けているので)実行します。

```bash
docker compose exec web flask init-db
```

`DBに棚を作りました` と出ればOKです。

### ⑤ ブラウザで確認

<http://localhost:5000> を開いてください。

- **「セットアップ完了 🎉」と出て、データベースが「接続OK」** → 成功です
- 「未接続」と出る → DBの起動待ちの可能性があります。10秒待ってページを再読み込み
- 画面が出ない → 下の「困ったとき」へ

---

## 2. 毎日の操作(これだけ覚えれば作業できます)

### 作業を始めるとき

```bash
docker compose up
```

### 作業を終わるとき

```bash
# 上のターミナルで Ctrl + C を押す。それだけです。
# 完全に片付けたい場合:
docker compose down
```

### コードを直したとき

**何もしなくていいです。** ファイルを保存すると自動で反映されます。

- Python(`.py`)→ アプリが自動で再起動します。**ブラウザを再読み込みするだけ**
- HTML / CSS / JS → **ブラウザを再読み込みするだけ**

> CSSを直したのに変わらない場合は、**キャッシュ**(ブラウザが前の内容を覚えている状態)です。
> `Ctrl + Shift + R`(Macは `Cmd + Shift + R`)で強制的に読み直せます。

### ログ(エラーの内容)を見たいとき

```bash
docker compose logs -f web
```

**エラーが出たら、まずここを見ます。** 赤い文字の一番下あたりに原因が書いてあります。
`-f` は「流れ続ける」の意味で、止めるときは `Ctrl + C` です。

### 箱の中に入って作業したいとき

```bash
docker compose exec web bash
```

箱の中のターミナルに入ります。出るときは `exit` です。

---

## 3. データベースの操作

### 棚を作る / 増やした棚を反映する

`models.py` に**新しいクラスを足した**あと:

```bash
docker compose exec web flask init-db
```

### 棚の形を変えたとき(列を追加・変更した)

**既にある棚の形は自動で変わりません。** 一度捨てて作り直します。

```bash
docker compose exec web flask drop-db
docker compose exec web flask init-db
```

> ⚠️ **中のデータは全部消えます。** ハッカソン中はこれが一番早くて確実です。
> (本番運用ではデータを保ったまま形を変える方法を使いますが、今回は不要です)

### DBがどうしてもおかしいとき(最終手段)

```bash
docker compose down -v
docker compose up --build
docker compose exec web flask init-db
```

`-v` を付けると**保管庫ごと消える**ので、DBが完全に初期状態に戻ります。

---

## 3.5 DBeaverでDBの中身を見る

### 接続設定

`docker compose up` でDBが起動している状態で、DBeaverから新しい接続を作ります。

| 項目 | 値 |
| --- | --- |
| ドライバ | MySQL |
| Server Host | `localhost` |
| **Port** | **`3307`** |
| Database | `hack_app` |
| Username | `hack_user` |
| Password | `hack_password` |

> ⚠️ **ポートは 3306 ではなく 3307 です。**
> PCに既にMySQLが入っている人とぶつからないよう、`compose.yml` でずらしています。
> (アプリ側は箱の中で `db:3306` に繋いでいるので、この番号とは無関係です)

### 「Public Key Retrieval is not allowed」と出たら

MySQL 8 のログイン方式のためです。接続設定の **Driver properties** で以下を変更してください。

| プロパティ | 値 |
| --- | --- |
| `allowPublicKeyRetrieval` | `true` |
| `useSSL` | `false` |

開発用のローカルDBなので、これで問題ありません。

### 管理者として入りたいとき

テーブルを直接消したりする場合は、`hack_user` では権限が足りないことがあります。

| Username | Password |
| --- | --- |
| `root` | `root_password` |

### 見ておくと理解が早いところ

- `users` / `todos` テーブル → `models.py` に書いた設計図がそのまま形になっています
- `users` の `password_hash` 列 → 保存されているのが**元に戻せない文字列**であることが目で確認できます

---

## 4. ライブラリを追加したいとき

例:画像処理の `Pillow` を使いたくなった場合。

1. `pyproject.toml` の `dependencies` に1行足す

```toml
dependencies = [
    "Flask",
    ...
    "Pillow",   # ← 追加
]
```

2. 箱に反映する

```bash
docker compose exec web uv sync
docker compose restart web
```

3. **`pyproject.toml` と `uv.lock` をコミットしてpushする**

> ⚠️ **これを共有しないと、他のメンバーの環境で `ModuleNotFoundError` が出ます。**
> pull した人は `docker compose exec web uv sync` を実行すれば揃います。

---

## 5. 困ったとき

### 「画面が出ない / 繋がらない」

```bash
docker compose ps
```

`web` と `db` の両方が `running` になっているか確認します。

- `web` が居ない/落ちている → `docker compose logs web` でエラーを読む
- `db` が `starting` → まだ準備中です。30秒待つ

### 「port is already allocated」と出る

**その番号を別のアプリが既に使っています。**

- `5000` の場合(Macで多い):`compose.yml` の `"5000:5000"` を `"5001:5000"` に変更 → `http://localhost:5001`
- `3307` の場合:`"3307:3306"` を `"3308:3306"` に変更

> **左の数字だけ**を変えてください。右はアプリ側の番号なので変えると動きません。

### VSCodeに「パッケージ 'Flask' がインストールされていません」と出る

**無視してOKです。** 部品は箱の中に入っているので、アプリは正常に動きます。

VSCodeは自分のPC側で動いているため、箱の中の部品が見えていないだけです。
そのため補完や定義ジャンプは効きませんが、**動作には一切影響しません。**

### 「ModuleNotFoundError: No module named 'xxx'」

誰かがライブラリを追加した直後です。

```bash
docker compose exec web uv sync
docker compose restart web
```

### 「Can't connect to MySQL server」

DBの起動待ちです。少し待って再読み込み。それでもダメなら:

```bash
docker compose restart web
```

### 「Bad Request / The CSRF token is missing」

フォームに**整理券を入れ忘れています**。HTMLのフォームの中に次の1行があるか確認してください。

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
```

JavaScriptから送っている場合は、`main.js` の `api.post()` を使ってください(整理券が自動で付きます)。

### 「値が届かない / 空っぽになる」

HTMLの `name="○○"` と、Pythonの `request.form.get("○○")` の**文字が一致しているか**を確認してください。ここのズレが原因の8割です。

### それでも分からないとき

以下の3つをセットでチームに投げてください。**これが揃っていれば誰でも助けられます。**

1. 何をしようとしたか
2. `docker compose logs web` の最後20行
3. ブラウザに出ている画面(スクリーンショット)

---

## 6. どうしてもDockerが動かない人向け(非常口)

**基本は使わないでください。** Dockerが壊れて時間が無いときだけの手段です。

```powershell
# uv を入れる (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 部品を入れる
uv sync

# DBだけDockerで動かす
docker compose up -d db

# .env の DB_HOST を db から 127.0.0.1 に、DB_PORT を 3307 に変更してから
$env:PYTHONPATH="src"; $env:FLASK_APP="web.app"; uv run flask run --debug
```

> `DB_HOST` を変える理由:箱の中からは `db` という名前で呼べますが、
> 自分のPCから見るときは「localhost の 3307番」経由になるためです。
