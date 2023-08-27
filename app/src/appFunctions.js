const closeBtn = document.getElementById("close");
const minimizeBtn = document.getElementById("minus");

closeBtn.addEventListener("click", close_app);
minimizeBtn.addEventListener("click", minimize_app);

function close_app() {
  app.window.close();
}

function minimize_app() {
  app.window.minimize();
}

document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("loaded");
});