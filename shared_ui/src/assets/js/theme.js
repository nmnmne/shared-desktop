import { ref } from "vue";

// Состояние для темы
export const isDarkTheme = ref(false);

// Загружаем тему из localStorage при монтировании компонента
export function loadTheme() {
  const savedTheme = localStorage.getItem('theme');

  if (savedTheme === 'true') {
    isDarkTheme.value = true;
    document.body.classList.add('dark-theme');
  } else {
    isDarkTheme.value = false;
    document.body.classList.remove('dark-theme');
  }
}

// Переключение темы
export function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value;

  // Небольшая задержка для анимации
  setTimeout(() => {
    const toggleSwitch = document.querySelector('.toggle-switch');
    toggleSwitch.classList.toggle('active', isDarkTheme.value);
  }, 50); // Даем время на отрисовку

  if (isDarkTheme.value) {
    localStorage.setItem('theme', 'true');
    document.body.classList.add('dark-theme');
  } else {
    localStorage.setItem('theme', 'false');
    document.body.classList.remove('dark-theme');
  }
}
