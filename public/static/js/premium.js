/* Optional depth enhancement. The page is complete without JavaScript. */
(() => {
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const stage = document.querySelector("[data-depth]");
  if (!stage) return;
  let frame = 0;
  let bounds;
  let x = 0;
  let y = 0;
  const reset = () => {
    cancelAnimationFrame(frame);
    frame = 0;
    stage.style.removeProperty("--depth-x");
    stage.style.removeProperty("--depth-y");
  };
  stage.addEventListener("pointerenter", () => {
    bounds = stage.getBoundingClientRect();
  });
  stage.addEventListener(
    "pointermove",
    (event) => {
      if (!finePointer.matches || reducedMotion.matches || !bounds) return;
      x = Math.max(
        -1,
        Math.min(1, ((event.clientX - bounds.left) / bounds.width) * 2 - 1),
      );
      y = Math.max(
        -1,
        Math.min(1, ((event.clientY - bounds.top) / bounds.height) * 2 - 1),
      );
      if (frame) return;
      frame = requestAnimationFrame(() => {
        stage.style.setProperty("--depth-x", `${(-y * 3).toFixed(2)}deg`);
        stage.style.setProperty("--depth-y", `${(x * 4).toFixed(2)}deg`);
        frame = 0;
      });
    },
    { passive: true },
  );
  stage.addEventListener("pointerleave", reset);
  stage.addEventListener("pointercancel", reset);
  reducedMotion.addEventListener("change", reset);
  finePointer.addEventListener("change", reset);
})();
