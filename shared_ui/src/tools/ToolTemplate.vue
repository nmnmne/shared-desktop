<template>
  <div class="container">
    <h2 class="title">Здесь заголовок</h2>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "здесь название",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath1: "здесь апи путь",
      responseData: null,
    };
  },
  methods: {
    async sendData() {
      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath1}`;
        const params = {
          key: "значение",
        };

        try {
          const response = await axios.post(server, {
            params,
            headers: {
              Authorization: `Token ${this.token}`,
            },
          });

          console.log("/Response/", response)

          this.responseData = response;
          this.responseIsError = false;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }

      // Если ни один сервер не ответил
      this.responseMessage = "Ошибка при отправке данных ко всем серверам.";
      this.responseIsError = true;
    }
  }
};
</script>

<style scoped>

</style>
