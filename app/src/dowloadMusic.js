const searchBar = document.getElementById("searchBar");

searchBar.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    const inputValue = searchBar.value;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "your-python-file.py", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({inputValue}));
  }
});