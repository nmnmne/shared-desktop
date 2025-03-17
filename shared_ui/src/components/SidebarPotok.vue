<template>
  <aside class="sidebar">
    <ul class="sidebar__list">
      <li 
        v-for="item in sidebarNav" 
        :key="item.id" 
        class="sidebar__item" 
        :class="{ 'sidebar__item--active': activeTool === item }"
      >
        <div class="sidebar__item-container" @click="setTool(item)">
          <span>{{ item.title }}</span>
        </div>
      </li>
    </ul>
  </aside>
</template>

<script setup>
import { ref } from "vue";

const sidebarNav = ref([
  {
    id: 1,
    title: "Перезагрузить WEB",
    toolName: "restart_web_admin",
  },
  {
    id: 2,
    title: "Генератор строк",
    toolName: "dt_potok",
  },
  {
    id: 3,
    title: "Работа с конфигуратором",
    toolName: "potok_tlc",
  },
]);

const activeTool = ref(null);
const emit = defineEmits(["changeTool"]);

const setTool = (item) => {
  activeTool.value = item;
  emit("changeTool", item);
};
</script>

<style lang="scss" scoped>
@use "@/assets/css/Sidebar.scss" as *;
</style>