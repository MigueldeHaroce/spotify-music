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



document.getElementById('aux1').addEventListener('change', function() {
  var mainContainer = document.getElementById('mainContainer');
  mainContainer.style.transition = "all 0.5s ease";
  var searchBar = document.getElementById('searchBar');

  if(this.checked) {
    document.body.style.backgroundColor = '#101010';
    mainContainer.style.backgroundColor = '#c4302b';
    mainContainer.style.borderStyle = 'solid';
    mainContainer.style.borderWidth = '2px';
    mainContainer.style.borderColor = '#fff';
    searchBar.placeholder = "Yt link to donwload...";

  } else {
    document.body.style.backgroundColor = '#000';
    mainContainer.style.backgroundColor = 'rgb(24, 94, 82)';
    mainContainer.style.borderStyle = 'none';
    searchBar.placeholder = "Playlist link to donwload...";
  }
});