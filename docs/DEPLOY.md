# インターネットに公開する

ここまで作ったアプリは、まだ**あなたのパソコンの中だけ**で動いています。
このページは、それを**インターネット上のサーバーに載せて、誰でも見られるようにする**(=**デプロイする**)ための手順です。

| あなたは | 読み方 |
| --- | --- |
| 🌱 公開ははじめて | [0. 公開に必要なもの](#0-公開に必要なもの) から順番に読んでください |
| 🛠️ 経験がある | 下の **[経験者向けの要約](#経験者向けの要約)** だけで足ります。詰まったら [7. 困ったとき](#7-困ったとき) |

> ★**本番の前に一度、必ず練習してください。**
> ここに書いてある手順を、公開する当日に初めて打つのは危険です。一度通しておけば、当日は同じことを繰り返すだけです。

---

## 経験者向けの要約

<details>
<summary>開く</summary>

- 構成:`compose.prod.yml` = Nginx(80/443)→ gunicorn(3 workers)→ MySQL 8.4(ポート非公開)
- 静的ファイルは Nginx が `src/web/static` を直接配信(30日キャッシュ。URLには中身のハッシュが付く)。サーバー上にソースの clone が必要
- 起動時に `flask init-db`(`db.create_all()`)が走る。マイグレーションは無いので、スキーマ変更は手作業か作り直し
- `.env`:`FLASK_ENV=production` / `SECRET_KEY` / DBのパスワード / `HTTPS_DOMAIN`
- HTTPS:certbot(webroot)で証明書を取得 → `.env` に `HTTPS_DOMAIN=ドメイン` → `up -d nginx`。証明書更新は cron で `certbot renew` + `nginx -s reload`
- 1GB メモリのサーバー向けに MySQL のメモリ設定を絞ってある(`compose.prod.yml` の db の `command:`)

```bash
cp .env.example .env    # FLASK_ENV=production, SECRET_KEY, DB_PASSWORD を変更
docker compose -f compose.prod.yml up -d --build
docker compose -f compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d <domain> --email <mail> --agree-tos --no-eff-email
# .env に HTTPS_DOMAIN=<domain> を追記して
docker compose -f compose.prod.yml up -d nginx
```

</details>

---

## 0. 公開に必要なもの

公開には、パソコンの外に次の2つを用意します。

| 必要なもの | 何か | 例えると | 費用の目安 |
| --- | --- | --- | --- |
| **サーバー** | 24時間動き続ける、インターネット上のコンピューター | お店を開く**テナント** | 月数百円〜(AWS の EC2、さくらのVPS など) |
| **ドメイン** | `example.com` のような、インターネット上の名前 | お店の**住所と看板** | 年数百円〜数千円 |

> **ドメインが無くても練習はできます。** サーバーの IP アドレス(`http://203.0.113.10` のような数字)で開けます。
> ただし、鍵マーク付きの **HTTPS にするにはドメインが必要**です。

サーバーには、**SSH** という方法でターミナルからつないで、コマンドを打ちます。
サーバーの借り方と SSH のつなぎ方は、借りた会社の案内に必ず書いてあるので、それに従ってください。

> ★サーバーは、**メモリ 1GB 以上**、OS は **Ubuntu** を選ぶと、この手順書のとおりに進められます。

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

サーバーに SSH でつないだら、Docker の公式の手順(<https://docs.docker.com/engine/install/ubuntu/>)で入れます。
入ったかどうかは、次の2行で確かめられます。

```bash
docker version
docker compose version
```

### ② コードを置く

```bash
git clone <あなたのリポジトリのURL>
cd <できたフォルダ>
```

> テンプレートそのものではなく、**あなたが作ったアプリのリポジトリ**を clone します。
> GitHub に上げていない場合は、先に上げてください。GitHub の準備と push のやり方は
> Progate の記事([Windows](https://prog-8.com/docs/git-env-win) / [Mac](https://prog-8.com/docs/git-env))の3〜5章にあります。

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
| `FLASK_SECURE_COOKIES` | HTTPS にするまでは `False`、**HTTPS にしたら `True`** |

> ★`.env` はサーバーの上で、`nano .env` のようにして書き換えます(保存は `Ctrl + O` → Enter、終了は `Ctrl + X`)。
> 中身は**絶対に GitHub に上げない**でください。パスワードが世界中に見えてしまいます。

`SECRET_KEY`(ログイン状態に押す**割り印**の鍵)は、これで作れます。

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

| | Let's Encrypt(サーバーの中で取る) | AWSのロードバランサー |
| --- | --- | --- |
| 費用 | **無料** | 動かしているだけで月20ドル前後 |
| 更新 | 90日ごと(自動にできる) | AWSが自動でやる |
| 設定 | **このテンプレートに用意済み** | VPC・サブネット2つ・ターゲットグループ |
| 向き | サーバー1台 | 複数台に増やす前提 |

**サーバー1台なら Let's Encrypt です。以下はその手順です。**

> ロードバランサーを使う場合、アプリ側は何も変えません。
> HTTPSはAWS側で終わらせて、サーバーにはHTTPで届きます。
> `prod.conf`(HTTP版)のままで正しく動きます。
> `X-Forwarded-Proto` が「元はHTTPSだった」と Flask に伝えているからです。

### 先に確かめること(★ここを飛ばすと必ず失敗します)

- **ドメインのAレコードが、このサーバーのIPを指していること**

  証明書は「そのドメインを開いたら本当にあなたのサーバーが出るか」を
  確かめてから発行されます。向いていなければ、何度試しても取れません。

  ```bash
  nslookup 自分のドメイン
  ```

- **80番と443番が外から入れること**(AWSならセキュリティグループ)

  80番は「もうHTTPSだから要らない」と思って閉じがちですが、
  **証明書の確認はHTTPで来ます。**閉じると取得も更新もできません。

### ① HTTPのまま起動しておく

```bash
docker compose -f compose.prod.yml up -d
```

`http://自分のドメイン` が開けることを確認してください。
**ここが開けない状態では、証明書は取れません。**

### ② まず練習で取ってみる(★これを先にやる)

```bash
docker compose -f compose.prod.yml run --rm certbot certonly   --webroot -w /var/www/certbot   -d 自分のドメイン   --email 自分のメールアドレス --agree-tos --no-eff-email   --dry-run
```

`--dry-run` は練習用の指定です。**本物の証明書は作られませんが、
本番と全く同じ確認が走ります。**

なぜ練習を挟むかというと、Let's Encrypt には
**「同じ内容は1週間に5回まで」という回数制限**があるからです。
設定が合っているか分からないまま本番で何度も失敗すると、
**その週はもうHTTPSにできません。**`--dry-run` は制限に数えられないので、
ここで何度でも試せます。

`The dry run was successful` と出たら次へ進みます。

### ③ 本物を取る

上のコマンドから `--dry-run` を外して、もう一度実行するだけです。

```
Successfully received certificate.
```

と出れば成功です。証明書は `certbot_conf` の保管庫に入りました。

### ④ HTTPSに切り替える

**`.env` に1行書くだけです。** 設定ファイルは書き換えません。

```
HTTPS_DOMAIN=自分のドメイン
```

`https://` は付けず、ドメインだけを書きます(例:`app.example.com`)。
そして Nginx を作り直します。

```bash
docker compose -f compose.prod.yml up -d nginx
```

`https://自分のドメイン` を開いて、鍵マークが付けば成功です。
`http://` で開いても、自動でHTTPSへ移ります。

> **仕組み**:`HTTPS_DOMAIN` が空のあいだは `docker/nginx/prod.conf`(HTTP)、
> 中身が入ると `docker/nginx/prod-https.conf`(HTTPS)が使われます。
> 証明書の場所もこの値から決まるので、ドメインをファイルに書く必要がありません。
> **本番のドメインがGitに残らない**のも利点です。

> **起動しなかったら、先にログを見てください。**
>
> ```bash
> docker compose -f compose.prod.yml logs nginx
> ```
>
> `cannot load certificate` と出ていれば、`HTTPS_DOMAIN` の値が
> 証明書を取ったドメインと違います(打ち間違い、または取る前に書いた)。
> **`HTTPS_DOMAIN` を空に戻して `up -d nginx` すれば、HTTPのサイトとしてすぐ復帰します。**
> 落ち着いて直せます。

### ⑤ 自動更新を仕掛ける

証明書は90日で切れます。**切れるとサイトが警告だらけになり、
多くのブラウザは開くことすら止めます。**手で更新し続けるのは現実的ではないので、
サーバー側の `cron`(決まった時刻に自動で実行する仕組み)に登録します。

```bash
crontab -e
```

開いたら、次の1行を足します(`/path/to/app` は自分の置き場所に変える)。

```
0 3,15 * * * cd /path/to/app && docker compose -f compose.prod.yml run --rm certbot renew --quiet && docker compose -f compose.prod.yml exec -T nginx nginx -s reload
```

- `0 3,15 * * *` = 毎日3時と15時。**1日2回で構いません**
- `renew` は**期限が30日以内に迫ったときだけ**実際に更新します。
  それ以外は何もせずに終わるので、毎日走らせても制限に当たりません
- 更新しただけでは Nginx は古い証明書を持ったままです。
  最後の `nginx -s reload` で読み直させます。**これを忘れると、
  更新は成功しているのにサイトは期限切れのまま**になります

### ⑥ 数日待ってから HSTS を有効にする

`docker/nginx/prod-https.conf` の最後に、コメントアウトされた1行があります。

```nginx
# add_header Strict-Transport-Security "max-age=31536000" always;
```

有効にすると、ブラウザが「このサイトは今後HTTPSでしか開かない」と覚えます。
安全になりますが、**一度覚えさせると1年間取り消せません。**

その間に証明書が切れると、ブラウザはHTTPへ逃げることすら拒むので、
**サイトが完全に開けなくなり、HTTPに戻して直すこともできません。**

自動更新が実際に1回回ったのを確かめてから外してください。急ぐ理由はありません。

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

### **時々**502になる / しばらく待つと勝手に直る

**★DBがメモリ不足で強制終了されています。**アプリのバグではありません。

メモリ1GBのサーバー(AWSの `t3.micro` など無料枠でよく使うもの)で起きます。
MySQL 8 は既定のままだと800MB近く使うので、アプリと合わせて足りなくなり、
**OSが「いちばんメモリを食っている奴」としてMySQLを終了させます。**

たちが悪いのは、この症状の出方です。

- アプリのログにはエラーが出ない(アプリは正常に動いている)
- 少し待つと `restart: always` でDBが戻ってくるので、勝手に直る
- **再現しないので、何が悪いのか分からない**

確かめ方はこれです。

```bash
docker compose -f compose.prod.yml ps
```

db の `STATUS` が `Up 30 seconds` のように**短い時間**になっていたら、
さっき落ちて起き直した直後です。`docker compose -f compose.prod.yml logs db`
に `Out of memory` や `killed` が出ていれば確定です。

**このテンプレートの `compose.prod.yml` には、対策の4行を最初から入れてあります**
(db の `command:` の部分)。それでも起きる場合は、サーバーのメモリを
2GBに上げるか、スワップ(メモリが足りないときにディスクを借りる仕組み)を
用意してください。

```bash
# スワップを2GB用意する(サーバー側で1回だけ)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### CSSやJSを直したのに、本番の画面が古いまま

**そのファイルのURLに「版の印」が付いていない**のが原因です。

本番ではブラウザがCSS・JS・画像を30日間手元に取っておきます。このテンプレートは
URLに中身から作った印を付けて、直したときだけ取り直させています(`src/web/assets.py`)。
HTMLに `/static/...` と直接書いたファイルには、この印が付きません。

```html
<!-- × 印が付かない。直しても古いまま -->
<link rel="stylesheet" href="/static/css/mypage.css" />

<!-- ○ 印が付く -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/mypage.css') }}" />
```

手元の画面だけ古いときは、`Ctrl + Shift + R`(Macは `Cmd + Shift + R`)で
強制的に読み直せます。

### 鍵マークが付かない / 「保護されていない通信」と出る

まず、どちらの状態か切り分けます。

```bash
docker compose -f compose.prod.yml logs nginx
```

| ログの様子 | 原因 |
| --- | --- |
| `cannot load certificate` | `.env` の `HTTPS_DOMAIN` が、証明書を取ったドメインと違う |
| 何も出ず、80番で普通に動いている | `.env` の `HTTPS_DOMAIN` が空のまま(または書いた後に `up -d nginx` していない) |
| `certificate has expired` | 自動更新が回っていない(`nginx -s reload` 忘れが多い) |

**証明書そのものの期限は、これで見られます。**

```bash
docker compose -f compose.prod.yml run --rm --entrypoint openssl certbot   x509 -enddate -noout -in /etc/letsencrypt/live/自分のドメイン/fullchain.pem
```

どの場合も、`.env` の `HTTPS_DOMAIN` を空に戻して
`up -d nginx` すれば、**HTTPのサイトとしてはすぐ復帰します。**
慌てて設定をいじる前に、先にサイトを生かしてから直してください。

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
- [ ] **`https://` で開けて、鍵マークが付いている**
- [ ] **`http://` で開いたら、自動でHTTPSに移る**
- [ ] **証明書の自動更新を `crontab` に登録した**(★これが無いと90日後に止まります)
- [ ] `docker compose -f compose.prod.yml restart` して、データが残っている

**最後の1つが特に大事です。** 再起動でデータが消えるなら、保管庫の設定が間違っています。
