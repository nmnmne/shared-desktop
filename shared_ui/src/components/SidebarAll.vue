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
    title: "Просмотр ДК",
    toolName: "traffic_lights",
  },
  {
    id: 2,
    title: "Управление фазой",
    toolName: "phase_control",
  },
  {
    id: 3,
    title: "Управление контроллером",
    toolName: "traffic_pro",
  },
  {
    id: 4,
    title: "Версия прошивки контроллера",
    toolName: "get_firmware",
  },
  {
    id: 5,
    title: "Калькулятор времени цикла",
    toolName: "calculate_cycle",
  },
  {
    id: 6,
    title: "Отчеты Дирижёра",
    toolName: "sg_count",
  },
  {
    id: 7,
    title: "Работа с паспортом",
    toolName: "",
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
