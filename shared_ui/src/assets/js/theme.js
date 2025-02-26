const checkbox = document.querySelector('.theme-checkbox');
const toggle = document.getElementById('theme-toggle');


document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'true') {
    checkbox.checked = true;
    theme.setAttribute('href', './src/assets/css/dark.css');
    console.log("DarkTheme");
  } else {
    checkbox.checked = false;
    theme.setAttribute('href', './src/assets/css/light.css');
    console.log("LightTheme");
  }
  toggle.classList.toggle('active', checkbox.checked);
});

toggle.addEventListener('click', function() {
  checkbox.checked = !checkbox.checked;
  toggle.classList.toggle('active', checkbox.checked);
  handleThemeChange();
});

checkbox.addEventListener('change', handleThemeChange);

function handleThemeChange() {
  if (checkbox.checked) {
    localStorage.setItem('theme', true);
    theme.setAttribute('href', './src/assets/css/dark.css');
  } else {
    localStorage.setItem('theme', false);
    theme.setAttribute('href', './src/assets/css/light.css');
  }
}