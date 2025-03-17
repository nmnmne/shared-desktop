<template>
  <div class="tools-page">
    <SidebarAll :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div v-if="!toolName">Выберите инструмент</div>
      <div v-else>
        <ApiDir v-if="toolName === 'api_dir'" />
        <PhaseControl v-if="toolName === 'phase_control'" />
        <SGCount v-if="toolName === 'sg_count'" />
        <ManageController v-if="toolName === 'manage_controller'" />
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
import ManageController from "@/tools/ManageController.vue"

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
