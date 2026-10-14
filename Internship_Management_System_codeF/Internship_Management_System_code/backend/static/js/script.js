/* InternshipHub interactions */
(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Theme toggle ---------- */
    var themeBtn = document.getElementById("themeToggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", function () {
            var next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
            document.documentElement.dataset.theme = next;
            try { localStorage.setItem("ih-theme", next); } catch (e) {}
        });
    }

    /* ---------- Mobile menu ---------- */
    var toggle = document.getElementById("navToggle");
    var links = document.getElementById("navLinks");
    if (toggle && links) {
        toggle.addEventListener("click", function () {
            var open = links.classList.toggle("open");
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
        });
    }

    /* ---------- Show / hide password ---------- */
    document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var input = btn.parentElement.querySelector("input");
            input.type = input.type === "password" ? "text" : "password";
        });
    });

    /* ---------- Toasts disappear on their own ---------- */
    document.querySelectorAll(".toast").forEach(function (t) {
        setTimeout(function () { t.remove(); }, 5200);
    });

    /* ---------- 3D tilt on cards ---------- */
    if (!reduceMotion && window.matchMedia("(hover: hover)").matches) {
        document.querySelectorAll("[data-tilt]").forEach(function (el) {
            el.addEventListener("mousemove", function (e) {
                var r = el.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width;
                var py = (e.clientY - r.top) / r.height;
                el.classList.add("is-tilting");
                el.style.setProperty("--ty", ((px - 0.5) * 12).toFixed(2) + "deg");
                el.style.setProperty("--tx", ((0.5 - py) * 12).toFixed(2) + "deg");
                el.style.setProperty("--gx", (px * 100).toFixed(1) + "%");
                el.style.setProperty("--gy", (py * 100).toFixed(1) + "%");
            });
            el.addEventListener("mouseleave", function () {
                el.classList.remove("is-tilting");
                el.style.setProperty("--tx", "0deg");
                el.style.setProperty("--ty", "0deg");
            });
        });

        /* Hero scene follows the pointer */
        var scene = document.querySelector("[data-scene]");
        if (scene) {
            document.addEventListener("mousemove", function (e) {
                var r = scene.getBoundingClientRect();
                var cx = r.left + r.width / 2;
                var cy = r.top + r.height / 2;
                var dx = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth / 2)));
                var dy = Math.max(-1, Math.min(1, (e.clientY - cy) / (window.innerHeight / 2)));
                var stack = scene.querySelector(".stack");
                stack.style.setProperty("--ry", (-16 + dx * 14).toFixed(1) + "deg");
                stack.style.setProperty("--rx", (8 - dy * 10).toFixed(1) + "deg");
            });
        }
    }

    /* ---------- Live search on the internships page ---------- */
    var box = document.getElementById("searchBox");
    if (box) {
        var items = document.querySelectorAll("[data-search-item]");
        var count = document.getElementById("resultCount");
        var none = document.getElementById("noMatch");

        box.addEventListener("input", function () {
            var q = box.value.trim().toLowerCase();
            var shown = 0;
            items.forEach(function (item) {
                var match = item.dataset.text.indexOf(q) !== -1;
                item.hidden = !match;
                if (match) { shown++; }
            });
            count.textContent = shown + (shown === 1 ? " internship" : " internships");
            none.hidden = shown !== 0 || items.length === 0;
        });
    }
})();
