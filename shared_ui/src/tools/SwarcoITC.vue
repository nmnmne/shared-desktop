<template>
  <div class="container tools-left">
    <h2 class="title">Сброс сессий пользователя 'itc'</h2>
    <div class="form-inline">
      <div>
        <input
          type="text"
          v-model="deviceIp"
          class="text"
          placeholder="000.000.000.000"
          required
          autocomplete="off"
          style="width: 20ch;"
        />
      </div>
      <div class="form-inline">
        <button @click="executeCommand('ps')">Просмотреть</button>
        <button hidden @click="executeCommand('top')">Выполнить TOP</button>
        <button class="red-button" @click="executeCommand('kill')">Завершить</button>
      </div>
    </div>

    <div v-if="response">
      <pre>{{ response }}</pre>
    </div>

    <div v-if="error">
      <h3>Ошибка:</h3>
      <pre>{{ error }}</pre>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  data() {
    return {
      deviceIp: '',
      serverIPs: serverIPs,
      response: null,
      error: null
    };
  },
  methods: {
    async executeCommand(command) {
      if (!this.deviceIp) {
        this.error = "Пожалуйста, введите IP устройства.";
        this.response = null;
        return;
      }

      this.response = null;
      this.error = null;

      const apiIp = this.serverIPs[0];

      let apiUrl = "";
      switch (command) {
        case "ps":
          apiUrl = `http://${apiIp}/execute_ps/`;
          break;
        case "top":
          apiUrl = `http://${apiIp}/execute_top/`;
          break;
        case "kill":
          apiUrl = `http://${apiIp}/execute_kill/`;
          break;
        default:
          this.error = "Неизвестная команда.";
          return;
      }

      const requestData = {
        ip: this.deviceIp
      };

      try {
        const response = await axios.post(apiUrl, requestData);
        this.response = response.data.result;
      } catch (error) {
        this.error = "Ошибка при выполнении запроса: " + error.message;
      }
    }
  }
};
</script>

<style scoped>

pre {
  padding: 10px;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>