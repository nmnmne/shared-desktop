let checkbox = document.querySelector('.theme-checkbox')

if(localStorage.getItem('theme') == "true") {
  theme.setAttribute('href', '../css/dark.css')
  checkbox.checked = true
}

checkbox.onchange = function() {
  if(this.checked) {
    console.log("DarkTheme")
    localStorage.setItem('theme', true)
    theme.setAttribute('href', './src/assets/css/dark.css')
  } else {
    console.log("LightTheme")
    localStorage.setItem('theme', false)
    theme.setAttribute('href', './src/assets/css/light.css')
  }
}