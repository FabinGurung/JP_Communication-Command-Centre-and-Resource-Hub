"use strict";
/* One accessible, compact site menu. Never lock the document scroll. */
(() => {
  const button = document.querySelector("[data-nav-toggle]");
  const menu = document.querySelector("[data-global-nav]");
  if (!button || !menu) return;
  const setOpen = open => {
    button.setAttribute("aria-expanded", String(open));
    menu.classList.toggle("is-open", open);
    button.setAttribute("aria-label", open ? "Close site navigation" : "Open site navigation");
  };
  button.addEventListener("click", () => setOpen(button.getAttribute("aria-expanded") !== "true"));
  menu.querySelectorAll("a").forEach(link => link.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && button.getAttribute("aria-expanded") === "true") {
      setOpen(false);
      button.focus();
    }
  });
  document.addEventListener("pointerdown", e => {
    if (button.getAttribute("aria-expanded") === "true" &&
        !button.contains(e.target) && !menu.contains(e.target)) setOpen(false);
  });
})();
