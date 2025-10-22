<template>
  <div class="tools-page">
    <SidebarAll :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div class="container tools-left" v-if="!toolName">
        <h2 class="title">Выберите инструмент</h2>
      </div>
      <div v-else>
        <ApiDir v-if="toolName === 'api_dir'" />
        <PhaseControl v-if="toolName === 'phase_control'" />
        <SGCount v-if="toolName === 'sg_count'" />
        <TrafficLights v-if="toolName === 'traffic_lights'" />
        <GetFirmware v-if="toolName === 'get_firmware'" />
        <CalculateCycle v-if="toolName === 'calculate_cycle'" />
        <TabDtGen v-if="toolName === 'tab_dt_gen'" />
        <CalcConflicts v-if="toolName === 'calc_conflicts'" />
        <Passport v-if="toolName === 'passport'" />
        <PassportAuto v-if="toolName === 'passport_auto'" />
        <TabComGen v-if="toolName === 'tab_com_gen'" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarAll from "@/components/SidebarAll.vue";
import ApiDir from "@/tools/ApiDir.vue";
import PhaseControl from "@/tools/PhaseControl.vue"
import SGCount from "@/tools/SGCount.vue"
import TrafficLights from "@/tools/TrafficLights.vue"
import GetFirmware from "@/tools/GetFirmware.vue"
import CalculateCycle from "@/tools/CalculateCycle.vue"
import TabDtGen from "@/tools/TabDtGen.vue"
import CalcConflicts from "@/tools/CalcConflicts.vue";
import Passport from "@/tools/Passport.vue";
import PassportAuto from "@/tools/PassportAuto.vue";
import TabComGen from "@/tools/TabComGen.vue";

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
