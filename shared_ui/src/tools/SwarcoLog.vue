<template>
  <div class="container tools-left">
    <h2 class="title">Расшифровка лог-файла Swarco</h2>
    <div class="form-inline">
      <input type="file" @change="handleFileUpload" class="custom-file-input" />
      <button @click="uploadFile">Обработать</button>
    </div>
    <div v-if="responseMessage">
      <p :class="{ 'error': responseIsError }">{{ responseMessage }}</p>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "SwarcoLog",
  data() {
    return {
      file: null,
      responseMessage: "",
      responseIsError: false,
      token: import.meta.env.VITE_API_TOKEN,
      apiPath: "/swarco_log_api/",
      serverIPs: serverIPs,
    };
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    async uploadFile() {
      if (!this.file) {
        this.responseMessage = "Пожалуйста, выберите файл для загрузки.";
        this.responseIsError = true;
        return;
      }

      const formData = new FormData();
      formData.append('logfile', this.file);

      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath}`;

        try {
          const response = await axios.post(server, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Token ${this.token}`
            },
            responseType: 'blob'
          });
          this.downloadFile(response.data, "processed_data.xlsx");
          this.responseMessage = "Файл успешно обработан и скачан.";
          this.responseIsError = false;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
          this.responseMessage = `Ошибка при отправке данных на сервер ${ip}.`;
          this.responseIsError = true;
        }
      }

      this.responseMessage = "Ошибка при отправке данных ко всем серверам.";
      this.responseIsError = true;
    },
    downloadFile(blob, filename) {
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  }
};
</script>

<style scoped>
.error {
  color: red;
}
</style>