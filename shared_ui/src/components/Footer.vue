<template>
  <footer>
    <div class="footer-container">
      <div class="theme">
        <label>Тёмная тема</label>
        <input
          type="checkbox"
          class="theme-checkbox"
          hidden
          v-model="isDarkTheme"
          @change="toggleTheme"
        />
        <div class="toggle-switch" id="theme-toggle" :class="{ active: isDarkTheme }" @click="toggleTheme">
          <div class="slider"></div>
        </div>
      </div>
      <a href="http://192.168.45.66:8000/" class="old-site-link">Старый сайт</a>
    </div>
  </footer>
  </template>
  
  <script setup>
  import { onMounted } from "vue";
  import { loadTheme, toggleTheme, isDarkTheme } from "@/assets/js/theme.js";
  
  // Загружаем тему при монтировании компонента
  onMounted(() => {
    loadTheme(); // Загружаем тему из localStorage
  });
  </script>
  
  <style lang="scss" scoped>
  @use "@/assets/css/Footer.scss" as *;

  </style>