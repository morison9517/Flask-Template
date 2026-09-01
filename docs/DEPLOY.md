# 本番に出す手順

このファイルは**サーバーにアプリを載せるとき**に見る紙です。
日々の開発は [SETUP.md](SETUP.md) を見てください。

> ★**本番前に一度、必ず練習してください。**
> ここに書いてある手順を、本番当日に初めて打つのは危険です。
> 一度通しておけば、当日は同じことを繰り返すだけになります。

---

## 開発と本番の違い(先に頭に入れておくこと)

| | 開発 | 本番 |
| --- | --- | --- |
| 使うファイル | `compose.yml` | **`compose.prod.yml`** |
| サーバー | flask run(1人ずつ捌く) | **gunicorn(3人同時)** |
| コードの反映 | 保存したら即 | **build し直したとき** |
| CSS・画像を配る人 | Flask | **Nginx** |
| DBのポート | PCから見える(3307) | **開けない** |
| エラー画面 | 詳しく出る | **出ない(内部情報が漏れるため)** |

**「保存しても本番に反映されない」のは正しい動きです。** 本番は箱に焼き込んだコードで動きます。

---

## 1. 準備(初回だけ)

### ① サーバーに Docker を入れる

```bash
docker version
docker compose version
```

### ② コードを置く

```bash
git clone <リポジトリのURL>
cd case_flask
```

### ③ 金庫(`.env`)を作る

```bash
cp .env.example .env
```

**そして必ず中身を書き換えます。** 見本のままだと危険です。

| 項目 | 本番で入れる値 |
| --- | --- |
| `SECRET_KEY` | **長いランダムな文字列**(下のコマンドで作る) |
| `FLASK_ENV` | `production` |
| `DB_PASSWORD` / `DB_ROOT_PASSWORD` | **開発用と違うパスワード** |

割り印(SECRET_KEY)はこれで作れます。

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

> ★`FLASK_ENV=development` のまま本番に出すと、エラーが起きたときに
> **設定ファイルの中身やDBのパスワードが画面に出ます。** 必ず `production` にしてください。

---

## 2. 起動する

```bash
docker compose -f compose.prod.yml up -d --build
```

**`-f compose.prod.yml` を毎回付けます。** 忘れると開発用が起動します。

初回は数分かかります。終わったら状態を見ます。

```bash
docker compose -f compose.prod.yml ps
```

`db` `web` `nginx` の3つが `running` なら成功です。

**DBの表を作るコマンドは要りません。** 起動時に自動で用意されます。

### 開いて確認

ブラウザで `http://<サーバーのアドレス>/auth/login` を開きます。

> ★`/`(トップページ)は、まだ自分たちで作っていないうちは **404 になります。**
> 開発中は `/` にデモページが出ますが、**本番ではデモを登録しないため**です。
> 「デモが本番に出ない」ことの裏返しなので、故障ではありません。
> `src/web/routes.py` に `@main_bp.get("/")` を書けば解消します。
>
> ★同じ理由で、**新規登録とログインは成功しても飛び先が404に見えます。**
> 成功したかどうかは、404の画面ではなくログで判断してください
> (302 が返っていれば成功しています)。

### 最初の利用者を作る

Flask版には管理画面がありません。**普通に新規登録の画面から作ってください。**

```
http://<サーバーのアドレス>/auth/register
```

> DBの中身を直接見たいときは、下の「本番のDBをDBeaverで見たいとき」を参照。

---

## 3. コードを直したとき

```bash
git pull
docker compose -f compose.prod.yml up -d --build
```

**この2行だけです。** DBの表づくりは起動時に自動で走ります。

> ★列の型を変えた場合(`String(80)` → `String(200)` など)は、
> **自動では変わりません。** Flaskの `create_all()` は「無い表を作る」だけで、
> 既にある表の形は変えないためです。
>
> 本番でどうしても変える必要が出たら、DBeaverで直接ALTERするか、
> 一度データを捨てて作り直すことになります。
> **本番に出す前にモデルを固めておくのが安全です。**

---

## 4. HTTPSにする

練習の段階では `http://` のままで構いません。**本番では必ずHTTPSにします。**

やり方は2つあります。

### ① サーバーの中で証明書を取る(Let's Encrypt)

無料です。90日ごとの更新が必要ですが、自動化できます。
サーバー1台の構成ならこちらが安く、設定も少なくて済みます。

### ② AWSのロードバランサーに任せる

証明書の更新が自動になりますが、**動かしているだけで月20ドル前後かかります。**
VPC・サブネット2つ・ターゲットグループの設定も必要です。

> どちらの場合も、`docker/nginx/prod.conf` に443番の設定を足し、
> `compose.prod.yml` の nginx に証明書の置き場所をマウントします。

### ★HTTPSにしたら必ず戻すこと

`.env` の1行です。

```
FLASK_SECURE_COOKIES=True
```

練習中に `False` にしていた場合、**戻し忘れるとログイン状態が
HTTPSでない経路でも持ち歩けてしまいます。**

---

## 5. よく使うコマンド

| やりたいこと | コマンド |
| --- | --- |
| 起動 | `docker compose -f compose.prod.yml up -d --build` |
| 停止 | `docker compose -f compose.prod.yml down` |
| 状態を見る | `docker compose -f compose.prod.yml ps` |
| ログを見る | `docker compose -f compose.prod.yml logs -f web` |
| Nginxのログ | `docker compose -f compose.prod.yml logs -f nginx` |
| 箱の中に入る | `docker compose -f compose.prod.yml exec web bash` |

> ★`down -v` は**絶対に打たないでください。**
> `-v` はDBと画像の保管庫ごと消す指定です。利用者のデータが全部消えます。

---

## 6. 本番のDBをDBeaverで見たいとき

本番では**DBのポートを開けていません。** 開けると世界中からログインを試されます。

代わりに、SSHのトンネルを通して見ます。DBeaverの接続設定で
「SSH」タブを開き、サーバーへのSSH情報を入れてください。
そのうえで、ホストは `127.0.0.1`、ポートは `3306` にします。

> トンネル = 自分のPCとサーバーの間に専用の通路を1本引くイメージです。
> 通路の中を通るので、外からは見えません。

---

## 7. 困ったとき

### 画面が真っ白 / デザインが崩れている

Nginxが `src/web/static/` を見つけられていない可能性があります。
`compose.prod.yml` の nginx に、この行があるか確認してください。

```yaml
- ./src/web/static:/var/www/static:ro
```

> ★Django版と違い、Flaskには「CSSを1か所に集めるコマンド」がありません。
> ソースのフォルダをそのままNginxに見せる作りになっています。
> **サーバー上に `git clone` したソースが必要**なのはこのためです。

### ログインできない(ログイン画面に戻される)

**`FLASK_SECURE_COOKIES` が原因です。**

`http://` でアクセスしているのに `True` になっていると、
ログイン自体は成功しているのにログイン状態が保存されません。
エラーも出ないので、まずここを疑ってください。

練習中は `.env` に `FLASK_SECURE_COOKIES=False` を入れてください。

### ボタンを押すと 400(The CSRF token is missing)

フォームに整理券が入っていません。HTMLにこの1行があるか確認してください。

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
```

JavaScriptから送っている場合は、`main.js` の `api` を使えば自動で付きます。

### 502 Bad Gateway と出る

Nginxは動いているが、Flask が返事をしていません。
web のログを見てください。だいたい起動時のエラーです。

```bash
docker compose -f compose.prod.yml logs web
```

### プロフィールアイコンが表示されない

`media` の保管庫がNginxから見えていない可能性があります。
`compose.prod.yml` の nginx に `media_files:/var/www/media:ro` があるか確認してください。

**なお、開発用と本番用で画像の保管庫は別です。** 開発中に入れた画像は本番にはありません。

### 起動しない / 起動してすぐ落ちる

`volumes:` に `- .:/app` を書いていないか確認してください。
**本番でこれを書くと、箱に焼き込んだものが隠れて起動しません。**
本番でいちばん多い事故です。

---

## 8. 本番に出す前のチェックリスト

デプロイの練習のときに、この順で確認してください。

- [ ] `.env` の `FLASK_ENV` が `production`
- [ ] `.env` の `SECRET_KEY` を見本から変えた
- [ ] `.env` の `DB_PASSWORD` を開発用から変えた
- [ ] `/auth/login` が開ける
- [ ] **CSSが当たっている**(見た目が崩れていない)
- [ ] **新規登録 → ログイン → ログアウトが通る**
- [ ] `docker compose -f compose.prod.yml restart` して、データが残っている

**最後の1つが特に大事です。** 再起動でデータが消えるなら、保管庫の設定が間違っています。
