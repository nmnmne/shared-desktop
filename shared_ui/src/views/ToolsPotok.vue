<template>
  <div class="tools-page">
    <SidebarPotok :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div class="container tools-left" v-if="!toolName">
        <h2 class="title">Выберите инструмент</h2>
      </div>
      <div v-else>
        <RestartWebAdmin v-if="toolName === 'restart_web_admin'" /> 
        <DtPotok v-if="toolName === 'dt_potok'" /> 
        <DtPotok2 v-if="toolName === 'dt_potok2'" /> 
        <PotokTLC v-if="toolName === 'potok_tlc'" />
        <NumDt v-if="toolName === 'num_dt'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarPotok from "@/components/SidebarPotok.vue";
import RestartWebAdmin from "@/tools/RestartWebAdmin.vue";
import DtPotok from "@/tools/DtPotok.vue";
import DtPotok2 from "@/tools/DtPotok2.vue";
import PotokTLC from "@/tools/PotokTLC.vue";
import NumDt from "@/tools/NumDt.vue";

const route = useRoute();
const router = useRouter();
const toolsData = ref(null);
const toolName = ref(route.params.toolName || null);

watch(() => route.params.toolName, (newTool) => {
  toolName.value = newTool || null;
});

const handleChangeTool = (tool) => {
  router.push(`/tools_potok/${tool.toolName}`);
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
