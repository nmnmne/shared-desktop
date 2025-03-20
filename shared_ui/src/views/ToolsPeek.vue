<template>
  <div class="tools-page">
    <SidebarPeek :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div v-if="!toolName"><h2 class="title">Выберите инструмент</h2></div>
      <div v-else>
        <PeekProcesses v-if="toolName === 'peek_processes'" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarPeek from "@/components/SidebarPeek.vue";
import PeekProcesses from "@/tools/PeekProcesses.vue";

const route = useRoute();
const router = useRouter();
const toolsData = ref(null);
const toolName = ref(route.params.toolName || null);

watch(() => route.params.toolName, (newTool) => {
  toolName.value = newTool || null;
});

const handleChangeTool = (tool) => {
  router.push(`/tools_peek/${tool.toolName}`);
};
</script>

<style scoped>

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
