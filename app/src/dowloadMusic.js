function runPythonScript(inputText) {
  ipcRenderer.send('run-python-script', inputText);
}

// Expose the `runPythonScript` function to the renderer process
window.runPythonScript = runPythonScript;

// Get the input element
const inputElement = document.getElementById('searchBar');

// Add an event listener for the enter key
inputElement.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    const inputText = inputElement.value;
    console.log('Sending input text to main process: ' + inputText);
  }
});