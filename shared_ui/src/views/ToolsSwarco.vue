<template>
  <div class="tools-page">
    <SidebarSwarco :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div v-if="!currentTool">Выберите инструмент</div>
      <div v-else>
        <SwarcoITC v-if="currentTool.toolName === 'SwarcoITC'" />
        <SwarcoLog v-if="currentTool.toolName === 'SwarcoLog'" />
      </div>

    </div>
  </div>
</template>

<script setup>
import SidebarSwarco from "@/components/SidebarSwarco.vue";
import SwarcoITC from "@/tools/SwarcoITC.vue";
import SwarcoLog from "@/tools/SwarcoLog.vue";
import {onMounted, ref} from "vue";
// import Tool1 from "@/tools/Tool1.vue";

const toolsData = ref(null);
const currentTool = ref(null);

const handleChangeTool = (tool) => {
  currentTool.value = tool;
}

</script>

<style scoped>

.tools {
  padding: 20px;
  flex-grow: 1;
}

.tools-page {
  display: flex;
  height: 100%;
}

@media (max-width: 900px) {
  .tools-page {
    display: block;
  }
}

</style>
