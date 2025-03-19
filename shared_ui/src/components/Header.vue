<template>
  <div class="header">
    <div class="brand">
      <img src="@/assets/img/logo.png" width="22" height="22" alt="Logo" />
      <span>Рабочий стол транспортного инженера</span>
    </div>
    <nav>
      <ul class="nav-list nav-list_right">
        <li v-for="item in menu" :key="item.id">
          <router-link
            :to="item.path"
            :class="{ active: $route.path.startsWith(item.path) }"
          >
            {{ item.title }}
          </router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ref } from "vue";

// Массив меню
const menu = ref([
  { id: 1, title: "Главная", path: "/home" },
  { id: 2, title: "Поток", path: "/tools_potok" },
  { id: 3, title: "Swarco", path: "/tools_swarco" },
  { id: 4, title: "Peek", path: "/tools_peek" },
  { id: 5, title: "Общее", path: "/tools_all" },
]);

</script>

<style lang="scss" scoped>
@use "@/assets/css/Header.scss" as *;
</style>
