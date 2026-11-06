/* brain.js — the bill microsite's logic layer ("the brain").
   One small dependency-free script that powers the liquid layout:

   - builds the Tools rail's "On this page" anchors from the live headings
   - runs the public board: fetches /api/voice-posts, renders the rail's
     compact board + the full list on /your-voice, polls every 30s so new
     posts and answers appear without a reload
   - marks the rail's live state and the page's place in the bill section

   No framework, no external calls beyond the app's own /api endpoints —
   same contract as the rest of the microsite. */
(function () {
    "use strict";

    var POLL_MS = 30000;
    var boardEl = document.getElementById("bbBoard");
    var listEl = document.getElementById("yvList");
    var pendingEl = document.getElementById("yvPendingCount");
    var statusEl = document.querySelector("[data-brain-status]");
    var liveEl = document.querySelector("[data-brain-live]");
    var toolsEl = document.querySelector("[data-brain-tools]");

    function esc(s) {
        var d = document.createElement("div");
        d.textContent = s || "";
        return d.innerHTML;
    }

    /* ---- tools rail: auto "On this page" from headed anchors ------------- */
    function buildTools() {
        if (!toolsEl) return;
        var main = document.querySelector(".shell-main") || document;
        var heads = main.querySelectorAll("h2[id], h3[id], section[id]");
        var items = [];
        heads.forEach(function (h) {
            var label = h.textContent.trim();
            if (label && items.length < 8) {
                items.push('<li><a href="#' + h.id + '">' + esc(label) + "</a></li>");
            }
        });
        if (items.length) {
            toolsEl.innerHTML =
                items.join("") +
                '<li><a href="#main-content">Back to top</a></li>' +
                '<li><a href="javascript:window.print()">Print this page</a></li>';
        }
    }

    /* ---- the board -------------------------------------------------------- */
    function renderPost(p) {
        return (
            '<li class="bb-item">' +
            '<div class="bb-meta"><span class="bb-kind bb-kind--' +
            esc(p.kind) + '">' + esc(p.kind) + "</span>" +
            '<span class="bb-date">' + esc(p.date) + "</span></div>" +
            '<p class="bb-post">' + esc(p.post) + "</p>" +
            (p.response
                ? '<p class="bb-response">' + esc(p.response) + "</p>" +
                  (p.responder
                      ? '<p class="bb-responder">— ' + esc(p.responder) + "</p>"
                      : "")
                : '<p class="bb-pending">Awaiting an answer.</p>') +
            "</li>"
        );
    }

    function paint(data) {
        var posts = (data && data.posts) || [];
        if (pendingEl && data && data.awaiting_review > 0) {
            pendingEl.textContent =
                data.awaiting_review + " post(s) received and awaiting the review pass.";
        }
        if (boardEl) {
            if (posts.length) {
                boardEl.innerHTML =
                    '<ul class="bb-list">' +
                    posts.slice(-4).reverse().map(renderPost).join("") +
                    "</ul>";
            }
            if (liveEl) liveEl.hidden = false;
        }
        if (listEl && posts.length) {
            listEl.innerHTML = posts
                .slice()
                .reverse()
                .map(renderPost)
                .join("");
        }
        if (statusEl) {
            statusEl.textContent =
                posts.length ? posts.length + " on the board" : "the board is open";
        }
    }

    function poll() {
        fetch("/api/voice-posts")
            .then(function (r) { return r.json(); })
            .then(paint)
            .catch(function () {});
    }

    if (boardEl || listEl) {
        poll();
        setInterval(poll, POLL_MS);
    }
    buildTools();
})();
