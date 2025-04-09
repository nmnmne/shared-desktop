<template>
  <div class="tools-page">
    <SidebarAll :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div class="container tools-left" v-if="!toolName">
        <h2 class="title">Выберите инструмент</h2>
      </div>
      <div v-else>
        <TrafficLights v-if="toolName === 'traffic_lights'" />
        <PhaseControl v-if="toolName === 'phase_control'" />
        <SGCount v-if="toolName === 'sg_count'" />
        <TrafficPro v-if="toolName === 'traffic_pro'" />
        <GetFirmware v-if="toolName === 'get_firmware'" />
        <CalculateCycle v-if="toolName === 'calculate_cycle'" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarAll from "@/components/SidebarAll.vue";
import TrafficLights from "@/tools/TrafficLights.vue";
import PhaseControl from "@/tools/PhaseControl.vue"
import SGCount from "@/tools/SGCount.vue"
import TrafficPro from "@/tools/TrafficPro.vue"
import GetFirmware from "@/tools/GetFirmware.vue"
import CalculateCycle from "@/tools/CalculateCycle.vue"

const route = useRoute();
const router = useRouter();
const toolsData = ref(null);
const toolName = ref(route.params.toolName || null);

watch(() => route.params.toolName, (newTool) => {
  toolName.value = newTool || null;
});

const handleChangeTool = (tool) => {
  router.push(`/tools_all/${tool.toolName}`);
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
