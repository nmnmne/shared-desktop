<template>
  <div class="tools-page">
    <AuthModal ref="authModal" />
    <SidebarPassport :toolsData="toolsData" @change-tool="handleChangeTool" />
    <div class="tools">
      <div class="container tools-left" v-if="!toolName">
        <h2 class="title">Выберите инструмент</h2>
      </div>
      <div v-else>
        <Passport1 v-if="toolName === 'passport_1'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import SidebarPassport from "@/components/SidebarPassport.vue";
import Passport1 from "@/tools/Passport1.vue";
import AuthModal from "@/components/AuthModal.vue";

const route = useRoute();
const router = useRouter();
const toolsData = ref(null);
const toolName = ref(route.params.toolName || null);
const authModal = ref(null);

// Обработчик события auth-required
const handleAuthRequired = () => {
  if (authModal.value) {
    authModal.value.show();
  }
};

onMounted(() => {
  window.addEventListener('auth-required', handleAuthRequired);
});

onUnmounted(() => {
  window.removeEventListener('auth-required', handleAuthRequired);
});

watch(() => route.params.toolName, (newTool) => {
  toolName.value = newTool || null;
});

const handleChangeTool = (tool) => {
  router.push(`/tools_passport/${tool.toolName}`);
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