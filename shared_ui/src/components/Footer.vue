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
      <a href="http://192.168.45.90/admin/" class="admin-link" target="_blank">Админ</a>
      <a href="http://192.168.45.90/" class="old-site-link" target="_blank">Старый сайт</a>

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