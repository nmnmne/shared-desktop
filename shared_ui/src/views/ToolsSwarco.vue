<template>
  <div class="tools-page">
    <SidebarSwarco :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div v-if="!toolName"><h2 class="title">Выберите инструмент</h2></div>
      <div v-else>
        <SwarcoITC v-if="toolName === 'swarco_itc'" />
        <SwarcoLog v-if="toolName === 'swarco_log'" />
        <DownloadConfig v-if="toolName === 'download_config'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarSwarco from "@/components/SidebarSwarco.vue";
import SwarcoITC from "@/tools/SwarcoITC.vue";
import SwarcoLog from "@/tools/SwarcoLog.vue";
import DownloadConfig from "@/tools/DownloadConfig.vue";

const route = useRoute();
const router = useRouter();
const toolsData = ref(null);
const toolName = ref(route.params.toolName || null);

watch(() => route.params.toolName, (newTool) => {
  toolName.value = newTool || null;
});

const handleChangeTool = (tool) => {
  router.push(`/tools_swarco/${tool.toolName}`);
};

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
