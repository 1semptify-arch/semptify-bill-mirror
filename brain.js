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
    var FLAG_REASONS = [
        ["personal_details", "Personal details — a name, address, or case info"],
        ["threat", "A threat, harassment, or someone's info posted to hurt them"],
        ["hate", "Hate or bigotry aimed at a group"],
        ["spam", "Spam, advertising, or junk"],
        ["illegal", "Something illegal"],
        ["impersonation", "Pretending to be a real person or group"],
        ["other", "Something else"]
    ];

    function flagMarkup(id) {
        var radios = FLAG_REASONS.map(function (r, i) {
            return '<label><input type="radio" name="flag-' + esc(id) + '" value="' +
                r[0] + '"' + (i === FLAG_REASONS.length - 1 ? " checked" : "") +
                "> " + esc(r[1]) + "</label>";
        }).join("");
        return (
            '<details class="bb-flag"><summary>Report a problem</summary>' +
            '<div class="bb-flag-body">' +
            '<p class="bb-flag-why">Why does it break the review standard?</p>' +
            radios +
            '<button class="bb-flag-send" data-post-id="' + esc(id) + '">Send report</button>' +
            "</div></details>"
        );
    }

    function flagPost(btn, id) {
        var box = btn.closest(".bb-flag-body");
        var sel = box ? box.querySelector("input[type=radio]:checked") : null;
        if (!sel) return;
        btn.disabled = true;
        fetch("/api/voice-posts/" + encodeURIComponent(id) + "/flag", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reason: sel.value })
        })
        .then(function (r) {
            if (r.ok) {
                btn.closest(".bb-flag").outerHTML =
                    '<p class="bb-flag-done">Reported — a person will take another look. Thank you.</p>';
            } else {
                btn.disabled = false;
                btn.textContent = "Send report — try again";
            }
        })
        .catch(function () {
            btn.disabled = false;
            btn.textContent = "Send report — try again";
        });
    }

    document.addEventListener("click", function (e) {
        var t = e.target;
        var btn = t && t.closest ? t.closest(".bb-flag-send") : null;
        if (btn) flagPost(btn, btn.getAttribute("data-post-id"));
    });

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
            (p.id ? flagMarkup(p.id) : "") +
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
                    posts.slice(0, 4).map(renderPost).join("") +
                    "</ul>";
            }
            if (liveEl) liveEl.hidden = false;
        }
        if (listEl && posts.length) {
            listEl.innerHTML = posts.map(renderPost).join("");
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
