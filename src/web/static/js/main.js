/* ===========================================================================
   main.js = 全ページ共通の道具

   ▼ ここには共通処理だけを置く
     ページ固有の処理を書くと6人で編集したときに衝突する。
     ページごとに別ファイルを作り、そのページのHTMLで読み込む:

       {% block scripts %}
         <script src="{{ url_for('static', filename='js/mypage.js') }}"></script>
       {% endblock %}
   =========================================================================== */

/* base.html の <meta name="csrf-token"> に埋め込まれた整理券を読む。
   Flask側(CSRFProtect)がこれを検証するので、送信時に必須。 */
const CSRF_TOKEN = document
  .querySelector('meta[name="csrf-token"]')
  ?.getAttribute("content");

/**
 * 取得(GET)
 *   const todos = await api.get("/api/todos");
 */
async function apiGet(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  return handleResponse(response);
}

/**
 * 送信(POST / PUT / DELETE)
 *   await api.post("/api/todos", { title: "牛乳を買う" });
 *   await api.delete("/api/todos/3");
 */
async function apiSend(url, data = null, method = "POST") {
  const options = {
    method: method,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      // ★これが無いと Flask に 400 で弾かれる(CSRF対策)
      "X-CSRFToken": CSRF_TOKEN,
    },
  };

  if (data !== null) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);
  return handleResponse(response);
}

/**
 * 返事を解釈する。fetch は 4xx/5xx でも例外を投げないので、
 * ここで明示的に失敗を throw して呼び出し側の try/catch に流す。
 * Flask側が {"error": "..."} を返していればその文言をそのまま使う。
 */
async function handleResponse(response) {
  let payload = null;

  // サーバーが落ちるとHTMLが返ることもあるので、変換失敗を許容する。
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.error || `通信に失敗しました (ステータス: ${response.status})`;
    throw new Error(message);
  }

  return payload;
}

const api = {
  get: apiGet,
  post: (url, data) => apiSend(url, data, "POST"),
  put: (url, data) => apiSend(url, data, "PUT"),
  delete: (url) => apiSend(url, null, "DELETE"),
};

/**
 * Python の flash() と同じ見た目でメッセージを出す。
 *   showMessage("保存しました", "success");
 * category は "success" / "error" / "warning" / "message"。
 */
function showMessage(text, category = "message") {
  let list = document.querySelector(".flash-list");

  if (!list) {
    list = document.createElement("ul");
    list.className = "flash-list";
    const header = document.querySelector(".site-header");
    header?.insertAdjacentElement("afterend", list);
  }

  const item = document.createElement("li");
  item.className = `flash flash-${category}`;
  // 利用者の入力が混ざる可能性があるので innerHTML は使わない
  item.textContent = text;
  list.appendChild(item);

  setTimeout(() => item.remove(), 4000);
}

/**
 * 送信中はボタンを無効化して二重送信を防ぐ。
 *   await withBusy(button, async () => {
 *     await api.post("/api/todos", { title: "牛乳" });
 *   });
 */
async function withBusy(button, task) {
  if (button) {
    button.disabled = true;
  }
  try {
    return await task();
  } finally {
    // 失敗してもボタンを戻す(戻さないと永久に押せなくなる)
    if (button) {
      button.disabled = false;
    }
  }
}
