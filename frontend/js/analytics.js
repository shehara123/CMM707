/* --------------------------------------------------------------
      Lugx ‑ Basic Analytics Beacon
   -------------------------------------------------------------- */

(function () {
  /* ---------- helpers ---------- */
  const ENDPOINT = "/analytics/track";          // hits the ingress
  const PAGE_URL = location.pathname || "/";

  // UUIDv4 without hyphens (matches ClickHouse column)
  function uuid () {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11)
      .replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
      ).replace(/-/g,"");
  }

  function send (body) {
    body.sessionId = sessionStorage.getItem("lugx_sid") ||
                     (() => { const id = uuid(); sessionStorage.setItem("lugx_sid", id); return id; })();
    body.timestamp = new Date().toISOString();
    navigator.sendBeacon(ENDPOINT, JSON.stringify(body));
  }

  /* ---------- page view ---------- */
  send({ eventType: "page_view", page: PAGE_URL });

  /* ---------- clicks ---------- */
  addEventListener("click", ev => {
    const tag = ev.target.closest("a,button")?.innerText?.trim()?.slice(0,32) || ev.target.tagName;
    send({ eventType: "click", element: tag, page: PAGE_URL });
  }, { capture: true });

  /* ---------- scroll depth ---------- */
  let deepest = 0, reported = false;
  addEventListener("scroll", () => {
    const scrolled = (window.scrollY + innerHeight) / document.documentElement.scrollHeight;
    deepest = Math.max(deepest, scrolled);
    if (!reported && deepest > 0.75) {          // 75 % threshold
      send({ eventType: "scroll", extra: { depth: "75%" }, page: PAGE_URL });
      reported = true;
    }
  }, { passive: true });
})();

