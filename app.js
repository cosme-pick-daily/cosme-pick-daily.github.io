(function () {
  "use strict";

  var DATA_URL = "data/products.json";
  var statusEl = document.getElementById("status");
  var listEl = document.getElementById("products");

  // 外部リンク・画像は https のみ許可する
  function safeUrl(value) {
    try {
      var url = new URL(value);
      return url.protocol === "https:" ? url.href : null;
    } catch (e) {
      return null;
    }
  }

  function formatPrice(price) {
    var n = Number(price);
    return Number.isFinite(n) ? n.toLocaleString("ja-JP") + "円" : "";
  }

  // "2026-10-28" -> "2026.10.28"
  function formatDate(added) {
    return /^\d{4}-\d{2}-\d{2}$/.test(added || "") ? added.replace(/-/g, ".") : "";
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function renderCard(p) {
    var link = safeUrl(p.url);
    if (!p.name || !link) return null;

    var li = el("li", "card");

    // 画像がない・読み込めないときは空の枠を表示する
    var src = safeUrl(p.image);
    if (src) {
      var img = el("img", "card-image");
      img.alt = p.name;
      img.loading = "lazy";
      img.referrerPolicy = "no-referrer";
      img.onerror = function () { img.replaceWith(el("div", "card-image")); };
      img.src = src;
      li.appendChild(img);
    } else {
      li.appendChild(el("div", "card-image"));
    }

    var body = el("div", "card-body");
    body.appendChild(el("h2", "card-name", p.name));

    var meta = el("div", "card-meta");
    meta.appendChild(el("span", "card-price", formatPrice(p.price)));
    var date = formatDate(p.added);
    if (date) meta.appendChild(el("span", "card-date", date + " 追加"));
    body.appendChild(meta);

    var button = el("a", "card-button", "楽天で見る");
    button.href = link;
    button.target = "_blank";
    button.rel = "sponsored nofollow noopener";
    body.appendChild(button);

    li.appendChild(body);
    return li;
  }

  function render(products) {
    // 新しい順。同じ日付なら後から追加したものを上にする
    var sorted = products
      .map(function (p, i) { return { p: p, i: i }; })
      .sort(function (a, b) {
        var da = a.p.added || "", db = b.p.added || "";
        if (da !== db) return da < db ? 1 : -1;
        return b.i - a.i;
      });

    var count = 0;
    sorted.forEach(function (item) {
      var card = renderCard(item.p);
      if (card) {
        listEl.appendChild(card);
        count++;
      }
    });
    statusEl.textContent = count === 0 ? "準備中です" : "";
  }

  fetch(DATA_URL, { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error(res.status);
      return res.json();
    })
    .then(function (data) {
      render(Array.isArray(data) ? data : []);
    })
    .catch(function () {
      statusEl.textContent = "準備中です";
    });
})();
