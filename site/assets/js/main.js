/* ============================================================
   OYA — interactions
   ============================================================ */
(function () {
  "use strict";

  /* ---- Sticky nav shadow ---- */
  var nav = document.getElementById("nav");
  function onScroll() {
    if (!nav) return;
    nav.classList.toggle("scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- Mobile nav toggle ---- */
  var toggle = document.getElementById("navToggle");
  var links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") links.classList.remove("open");
    });
  }

  /* ---- Scroll reveal ---- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (entry.isIntersecting) {
          var el = entry.target;
          // small stagger for siblings
          var delay = Math.min(i * 60, 180);
          setTimeout(function () { el.classList.add("in"); }, delay);
          io.unobserve(el);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- Animated counters ---- */
  function formatNum(value, isFloat) {
    if (isFloat) return value.toFixed(2);
    return Math.round(value).toLocaleString("en-US");
  }
  function animateCount(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var suffix = el.getAttribute("data-suffix") || "";
    var isFloat = String(el.getAttribute("data-count")).indexOf(".") !== -1;
    // Remove any placeholder text (e.g. "0") but keep element children such as
    // a trailing "+" span. A single dedicated text node holds the number.
    Array.prototype.slice.call(el.childNodes).forEach(function (n) {
      if (n.nodeType === 3) el.removeChild(n);
    });
    var node = document.createTextNode("");
    el.insertBefore(node, el.firstChild);
    var start = null, dur = 1600;
    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      node.nodeValue = formatNum(target * eased, isFloat) + suffix;
      if (p < 1) requestAnimationFrame(frame);
      else node.nodeValue = formatNum(target, isFloat) + suffix;
    }
    requestAnimationFrame(frame);
  }
  var counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window && counters.length) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          co.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  } else {
    counters.forEach(function (el) {
      var t = parseFloat(el.getAttribute("data-count"));
      var s = el.getAttribute("data-suffix") || "";
      var f = String(el.getAttribute("data-count")).indexOf(".") !== -1;
      Array.prototype.slice.call(el.childNodes).forEach(function (n) {
        if (n.nodeType === 3) el.removeChild(n);
      });
      el.insertBefore(document.createTextNode((f ? t.toFixed(2) : t.toLocaleString("en-US")) + s), el.firstChild);
    });
  }

  /* ---- FAQ accordion (hackathon page) ---- */
  var faqs = document.querySelectorAll(".faq-item");
  faqs.forEach(function (item) {
    var q = item.querySelector(".faq-q");
    var a = item.querySelector(".faq-a");
    if (!q || !a) return;
    q.addEventListener("click", function () {
      var isOpen = item.classList.contains("open");
      faqs.forEach(function (other) {
        other.classList.remove("open");
        var oa = other.querySelector(".faq-a");
        if (oa) oa.style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add("open");
        a.style.maxHeight = a.scrollHeight + "px";
      }
    });
  });

  /* ---- Smooth-scroll for in-page anchors (with nav offset) ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href");
      if (id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var y = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: y, behavior: "smooth" });
    });
  });
})();
