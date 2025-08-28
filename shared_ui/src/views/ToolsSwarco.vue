<template>
  <div class="tools-page">
    <SidebarSwarco :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div class="container tools-left" v-if="!toolName">
        <h2 class="title">Выберите инструмент</h2>
      </div>
      <div v-else>
        <SwarcoITC v-if="toolName === 'swarco_itc'" />
        <SwarcoLog v-if="toolName === 'swarco_log'" />
        <DownloadConfig v-if="toolName === 'download_config'" />
        <CalcConflicts v-if="toolName === 'calc_conflicts'" />
        <NumDt v-if="toolName === 'num_dt'" />
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
import CalcConflicts from "@/tools/CalcConflicts.vue";
import NumDt from "@/tools/NumDt.vue";

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
