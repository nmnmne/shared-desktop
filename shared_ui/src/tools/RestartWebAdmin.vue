<template>
  <div class="container tools-left">
    <h2 class="title">Перезагрузка web интерфейса</h2>

    <div class="form-inline">
      <input
        type="text"
        v-model="ipAddress"
        class="text"
        placeholder="000.000.000.000"
        required
        autocomplete="off"
        style="width: 20ch;"
      />
      <button @click="handleSubmit">Перезагрузка</button>
    </div>

    <p :style="{ color: responseMessage.color }">{{ responseMessage.text }}</p>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';

export default {
  name: "RestartWebAdmin",
  data() {
    return {
      ipAddress: '',
      responseMessage: {
        text: '',
        color: 'green',
      },
      serverIPs: serverIPs,
      apiPath: '/api/restart_web_admin/',
    };
  },
  methods: {
    async handleSubmit() {
      const selectedIP = this.serverIPs[0];
      const server = `http://${selectedIP}${this.apiPath}`;
      
      try {
        const response = await fetch(server, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken'),
          },
          body: JSON.stringify({ ip_address: this.ipAddress }),
        });

        const data = await response.json();

        if (data.status === 'success') {
          this.responseMessage.color = 'green';
          this.responseMessage.text = data.message;
        } else {
          this.responseMessage.color = 'red';
          this.responseMessage.text = data.message;
        }
      } catch (error) {
        console.warn(`Ошибка подключения к ${server}:`, error);
        this.responseMessage.color = 'red';
        this.responseMessage.text = 'Ошибка при подключении к серверу.';
      }
    },

    getCookie(name) {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
      if (match) return match[2];
    },
  },
};
</script>

<style scoped>

</style>