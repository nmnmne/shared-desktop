<template>
  <div>
    <h2></h2>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "",
  data() {
    return {
      condition: "",
      functions: [],
      conditionResult: "",
      token: import.meta.env.VITE_API_TOKEN,
      apiPath: "",
      serverIPs: serverIPs,
    };
  },
  methods: {
    async sendData() {
      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath}`;

        try {
          const response = await axios.post(server, this.transformedProcesses);
          this.responseData = response.data.repaired_cmd_sg;
          this.responseIsError = false;
          this.showModal = true;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }

      // Если ни один сервер не ответил
      this.responseMessage = "Ошибка при отправке данных ко всем серверам.";
      this.responseIsError = true;
      this.showModal = true;
    }
  }
};
</script>

<style scoped>

</style>
