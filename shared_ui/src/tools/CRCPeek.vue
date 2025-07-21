<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Расчет контрольной суммы RAG</h2>
      
      <div>
        <input 
          type="file" 
          class="custom-file-input"
          id="file" 
          ref="fileInput" 
          @change="handleFileUpload"
        />
      </div>

      <div v-if="fileContent" class="file-content-container">
        <div class="form-group mt-3">
          <textarea 
            class="file-content-textarea" 
            id="file-content" 
            v-model="fileContent" 
            rows="24" 
            style="font-family: monospace;"
          ></textarea>
        </div>
        
        <div class="form-group mt-2">
          <button 
            class="btn btn-primary" 
            @click="processFile"
            :disabled="processing"
          >
            <span v-if="processing">Обработка...</span>
            <span v-else>Процесс</span>
          </button>
          <button 
            class="btn btn-success" 
            @click="saveFile"
            :disabled="!fileProcessed"
          >
            Сохранить
          </button>
        </div>
        
        <div v-if="fileProcessed" class="alert alert-info mt-3">
          <strong>Разница контрольной суммы:</strong> {{ crcDiff }}<br>
          <strong>Сумма в файле:</strong> {{ sumInFile }}<br>
          <strong>Новая сумма в файле:</strong> {{ newSumInFile }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "CRCPeek",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath: "/api/crcpeek/",
      fileContent: null,
      initialCrc: null,
      sumInFile: null,
      crcDiff: 0,
      newSumInFile: 0,
      filename: null,
      processing: false,
      fileProcessed: false
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      try {
        this.processing = true;
        this.fileProcessed = false;
        
        // Читаем файл локально для мгновенного отображения
        this.fileContent = await this.readFileAsText(file);
        
        // Отправляем на сервер для получения начальных данных
        const formData = new FormData();
        formData.append('file', file);

        const response = await this.sendRequest(formData);
        this.initialCrc = response.data.crc_sum;
        this.sumInFile = response.data.sum_in_file;
        
        this.processing = false;
      } catch (error) {
        console.error("Ошибка при обработке файла:", error);
        this.processing = false;
      }
    },

    async processFile() {
      if (!this.fileContent) return;

      try {
        this.processing = true;
        
        const formData = new FormData();
        formData.append('file_content', this.fileContent);
        formData.append('initial_crc', this.initialCrc);
        formData.append('sum_in_file', this.sumInFile);
        formData.append('action', 'process');

        const response = await this.sendRequest(formData);
        
        // Обновляем содержимое файла и расчетные данные
        this.fileContent = response.data.file_content;
        this.crcDiff = response.data.crc_diff;
        this.newSumInFile = response.data.new_sum_in_file;
        this.fileProcessed = true;
        
        this.processing = false;
      } catch (error) {
        console.error("Ошибка при обработке файла:", error);
        this.processing = false;
      }
    },

    async saveFile() {
      if (!this.fileContent || !this.fileProcessed) return;

      try {
        this.processing = true;
        
        const formData = new FormData();
        formData.append('file_content', this.fileContent);
        formData.append('initial_crc', this.initialCrc);
        formData.append('sum_in_file', this.sumInFile);
        formData.append('action', 'save');

        const response = await this.sendRequest(formData);
        
        // Создаем и скачиваем файл
        const blob = new Blob([response.data.file_content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.data.filename || 'RAG.T';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.processing = false;
      } catch (error) {
        console.error("Ошибка при сохранении файла:", error);
        this.processing = false;
      }
    },

    async sendRequest(formData) {
      for (let ip of this.serverIPs) {
        const server = `http://${ip}${this.apiPath}`;
        try {
          const response = await axios.post(server, formData, {
            headers: {
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'multipart/form-data'
            }
          });
          return response;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
          throw error;
        }
      }
      throw new Error("Ошибка при отправке данных ко всем серверам.");
    },

    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file, 'utf-8');
      });
    }
  }
};
</script>

<style scoped>
.file-content-container {
  margin-top: 20px;
}

.btn {
  margin-right: 10px;
}

.alert {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
}

.alert-info {
  background-color: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}

.file-content-textarea {
  width: 100%;
  max-width: 100%;
  min-width: 100%;
  min-height: calc(1em * 24 + 1rem + 2px); 
  font-family: monospace;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;

}

.file-content-textarea {
  box-sizing: border-box;
}

.file-content-textarea::-moz-resizer {
  display: none;
}
</style>