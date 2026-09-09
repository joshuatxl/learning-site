/* Front page interactions
 * ───────────────────────
 *  hover a card → a large centred popup opens over a translucent dark mask.
 *    If the publisher allows iframe embedding (detected at build time and
 *    stored as `frameable` in article-data.json) the popup shows the real
 *    web page; otherwise it shows a clean, readable text extract.
 *  "Summarise this" → replaces the view with the AI summary.
 *    button toggles: "View original" ⇄ "View summary".
 *    summaries are cached in localStorage — survive reloads, never regenerated.
 *  "Open original ↗" opens the real page in a new tab.
 *  close: leave the popup, click the mask, ✕, or Esc.
 *  click a card (popup closed) → opens the source in a new tab.
 */
(function () {
  "use strict";

  function endpoint() { return (window.BRIEFING_SUMMARISE_URL || "").trim(); }
  var CACHE_PREFIX = "briefing:summary:";
  var OPEN_DELAY = 170;
  var MASK_ARM_DELAY = 450;
  var FRAME_TIMEOUT = 4500;

  var mask, pop, elFrames, elBody, elSummary, elLoading;
  var elTitle, elMeta, elBtn, elOpen, elClose;
  var current = null;          // { id, title, url, source, date, body, frameable }
  var view = "article";        // "article" | "summary"
  var articleView = "reader";  // "frame" | "reader" | "loading"
  var openTimer = null, frameTimer = null, maskArmedAt = 0;
  var dataPromise = null;

  // Live-page iframes kept for the session so re-opening is instant.
  var FRAME_MAX = 4;
  var framePool = [];          // [{ url, el, ready }] — least→most recently used
  var frameFail = Object.create(null);  // urls that failed to embed → use reader

  function cacheGet(id) {
    try { return localStorage.getItem(CACHE_PREFIX + id); } catch (e) { return null; }
  }
  function cacheSet(id, text) {
    try { localStorage.setItem(CACHE_PREFIX + id, text); } catch (e) {}
  }

  function loadData() {
    if (!dataPromise) {
      var u = new URL("article-data.json", document.baseURI).href;
      dataPromise = fetch(u).then(function (r) { return r.ok ? r.json() : {}; })
                            .catch(function () { return {}; });
    }
    return dataPromise;
  }

  // Gemini summary → <p> nodes (plain text)
  function paragraphs(el, text) {
    el.textContent = "";
    String(text || "").split(/\n{2,}/).forEach(function (chunk) {
      chunk = chunk.trim();
      if (!chunk) return;
      var p = document.createElement("p");
      p.textContent = chunk;
      el.appendChild(p);
    });
    if (!el.childNodes.length) el.textContent = "No summary text.";
    el.scrollTop = 0;
  }

  // Reader body — a build-time-sanitised HTML fragment (h2/h3/p/pre/ul/li/…),
  // no scripts, no attributes except validated hrefs. An optional hero image
  // (the article's own og:image) is placed at the top.
  function readerHtml(el, htmlFrag, image) {
    var hero = image
      ? '<img class="pop-hero" src="' + image.replace(/"/g, "&quot;") +
        '" alt="" onerror="this.remove()">'
      : "";
    el.innerHTML = hero + (htmlFrag ||
      "<p>No readable text for this article — use “Open original ↗”.</p>");
    el.querySelectorAll("a[href]").forEach(function (a) {
      a.target = "_blank"; a.rel = "noopener";
    });
    el.scrollTop = 0;
  }

  // ── build ─────────────────────────────────────────────────────
  function build() {
    mask = document.createElement("div");
    mask.className = "pop-mask";
    mask.addEventListener("click", close);
    mask.addEventListener("mousemove", function () {
      if (isOpen() && Date.now() >= maskArmedAt) close();
    });
    document.body.appendChild(mask);

    pop = document.createElement("div");
    pop.className = "article-pop";
    pop.innerHTML =
      '<div class="pop-head">' +
      '  <div class="pop-inner pop-titles"><h2></h2><p class="pop-meta"></p></div>' +
      '  <button class="pop-close" type="button" aria-label="Close">&times;</button>' +
      "</div>" +
      '<div class="pop-view">' +
      '  <div class="pop-frames"></div>' +
      '  <div class="pop-body reader" tabindex="0"></div>' +
      '  <div class="pop-summary reader" tabindex="0"></div>' +
      '  <p class="pop-loading">Loading the article…</p>' +
      "</div>" +
      '<div class="pop-foot"><div class="pop-inner pop-foot-row">' +
      '  <button type="button" class="pop-btn"></button>' +
      '  <a class="pop-open" target="_blank" rel="noopener">Open original ↗</a>' +
      "</div></div>";
    document.body.appendChild(pop);

    elTitle = pop.querySelector("h2");
    elMeta = pop.querySelector(".pop-meta");
    elFrames = pop.querySelector(".pop-frames");
    elBody = pop.querySelector(".pop-body");
    elSummary = pop.querySelector(".pop-summary");
    elLoading = pop.querySelector(".pop-loading");
    elBtn = pop.querySelector(".pop-btn");
    elOpen = pop.querySelector(".pop-open");
    elClose = pop.querySelector(".pop-close");

    elClose.addEventListener("click", close);
    elBtn.addEventListener("click", onButton);
    pop.addEventListener("mouseleave", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) close();
    });
  }

  function isOpen() { return pop && pop.classList.contains("is-open"); }
  function metaLine() { return [current.source, current.date].filter(Boolean).join("  ·  "); }

  // ── open ──────────────────────────────────────────────────────
  function openFor(card) {
    if (!pop) build();
    current = {
      id: card.dataset.id,
      title: card.dataset.title || "",
      url: card.dataset.href || "",
      source: card.dataset.source || "",
      date: card.dataset.date || "",
      body: (card.querySelector(".preview") || {}).textContent || "",
      image: card.dataset.image || "",
      frameable: false,
    };
    view = "article";
    articleView = "loading";
    render();

    var target = current;
    loadData().then(function (map) {
      if (current !== target) return;
      var rec = map && map[target.id];
      if (rec) {
        current.body = rec.body || current.body;
        current.date = rec.date || current.date;
        current.source = rec.source || current.source;
        current.frameable = !!rec.frameable;
        current.image = rec.image || current.image;
        elMeta.textContent = metaLine();
      }
      if (view !== "article") return;
      if (current.frameable) {
        startFrame(current.url);
      } else {
        articleView = "reader";
        readerHtml(elBody, current.body, current.image);
        applyView();
      }
    });

    mask.classList.add("is-open");
    pop.classList.add("is-open");
    document.body.classList.add("pop-lock");
    maskArmedAt = Date.now() + MASK_ARM_DELAY;
  }

  // ── live page: a small session pool of iframes ───────────────
  function getFrame(url) {
    for (var i = 0; i < framePool.length; i++) {
      if (framePool[i].url === url) {
        var hit = framePool.splice(i, 1)[0];   // bump to most-recent
        framePool.push(hit);
        return hit;
      }
    }
    var el = document.createElement("iframe");
    el.className = "pop-frame";
    el.title = "Article";
    el.setAttribute("referrerpolicy", "no-referrer");
    var rec = { url: url, el: el, ready: false };
    el.addEventListener("load", function () { onFrameLoad(rec); });
    framePool.push(rec);
    elFrames.appendChild(el);
    el.src = url;
    while (framePool.length > FRAME_MAX) {
      var gone = framePool.shift();
      if (gone.el.parentNode) gone.el.parentNode.removeChild(gone.el);
    }
    return rec;
  }

  function toReader() {
    articleView = "reader";
    readerHtml(elBody, current.body, current.image);
    applyView();
  }

  function startFrame(url) {
    if (frameFail[url]) { toReader(); return; }
    var rec = getFrame(url);
    framePool.forEach(function (r) { r.el.classList.toggle("active", r === rec); });
    clearTimeout(frameTimer);
    if (rec.ready) { articleView = "frame"; applyView(); return; }  // cached — instant
    articleView = "loading";
    applyView();
    frameTimer = setTimeout(function () {
      if (articleView === "loading" && !rec.ready) { frameFail[url] = 1; toReader(); }
    }, FRAME_TIMEOUT);
  }

  function onFrameLoad(rec) {
    rec.ready = true;
    if (current && current.frameable && current.url === rec.url &&
        view === "article" && articleView !== "reader") {
      clearTimeout(frameTimer);
      articleView = "frame";
      applyView();
    }
  }

  // ── render / view switching ─────────────────────────────────
  function applyView() {
    pop.classList.toggle("show-summary", view === "summary");
    pop.classList.toggle("show-frame", view === "article" && articleView === "frame");
    pop.classList.toggle("show-body", view === "article" && articleView === "reader");
    pop.classList.toggle("show-loading", view === "article" && articleView === "loading");
  }

  function render() {
    elTitle.textContent = current.title;
    elMeta.textContent = metaLine();
    elOpen.href = current.url || "#";

    if (view === "summary") {
      elSummary.classList.remove("is-error");
      paragraphs(elSummary, cacheGet(current.id) || "");
      elBtn.textContent = "View original";
    } else {
      if (articleView === "frame" && current.frameable) startFrame(current.url);
      else if (articleView !== "loading") readerHtml(elBody, current.body, current.image);
      elBtn.textContent = cacheGet(current.id) ? "View summary" : "Summarise this";
    }
    elBtn.disabled = false;
    applyView();
  }

  // ── footer button ──────────────────────────────────────────
  function onButton() {
    var label = elBtn.textContent;
    if (label === "View original") { view = "article"; render(); return; }
    if (label === "View summary")  { view = "summary"; render(); return; }

    if (cacheGet(current.id)) { view = "summary"; render(); return; }

    if (!endpoint()) {
      view = "summary";
      elSummary.classList.add("is-error");
      elSummary.textContent =
        "No summariser endpoint is configured yet. Deploy the worker in " +
        "workers/ (see workers/README.md), set extra.summarise_url in " +
        "mkdocs.yml to its URL, then redeploy the site.";
      elBtn.textContent = "View original";
      applyView();
      return;
    }

    var target = current;
    elBtn.disabled = true;
    elBtn.textContent = "Summarising…";
    view = "summary";
    elSummary.classList.remove("is-error");
    elSummary.textContent = "Summarising… Gemini is being called once for this article.";
    applyView();

    fetch(endpoint(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: target.url, title: target.title }),
    })
      .then(function (r) { if (!r.ok) throw new Error("endpoint " + r.status); return r.json(); })
      .then(function (d) {
        var text = (d && d.summary ? String(d.summary) : "").trim();
        if (!text) throw new Error("empty summary");
        cacheSet(target.id, text);
        if (current === target && isOpen()) { view = "summary"; render(); }
      })
      .catch(function (err) {
        if (current === target && isOpen()) {
          elSummary.classList.add("is-error");
          elSummary.textContent = "Could not summarise: " + err.message;
          elBtn.disabled = false;
          elBtn.textContent = "Summarise this";
        }
      });
  }

  // ── close ──────────────────────────────────────────────────
  function close() {
    clearTimeout(openTimer);
    clearTimeout(frameTimer);
    if (pop) {
      pop.classList.remove("is-open", "show-summary", "show-frame", "show-body", "show-loading");
      mask.classList.remove("is-open");
    }
    document.body.classList.remove("pop-lock");
    // NB: iframes in framePool are left loaded for the session.
    current = null;
    view = "article";
    articleView = "reader";
  }

  // ── card events ────────────────────────────────────────────
  document.addEventListener("mouseover", function (e) {
    if (isOpen()) return;
    var card = e.target.closest(".story-card");
    if (!card) return;
    clearTimeout(openTimer);
    openTimer = setTimeout(function () { openFor(card); }, OPEN_DELAY);
  });
  document.addEventListener("mouseout", function (e) {
    var card = e.target.closest(".story-card");
    if (card && !card.contains(e.relatedTarget)) clearTimeout(openTimer);
  });
  document.addEventListener("click", function (e) {
    if (isOpen() || (pop && pop.contains(e.target))) return;
    var card = e.target.closest(".story-card");
    if (card && card.dataset.href) window.open(card.dataset.href, "_blank", "noopener");
  });
})();
