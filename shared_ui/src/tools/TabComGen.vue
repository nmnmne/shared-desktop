<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Генератор таблицы коммутаций</h2>

      <div class="mb10">
        <label>Выберите тип контроллера и количество клемм:</label>
      </div>

      <div class="form-inline mb10">
          <select 
            id="controller-type"
            v-model="controllerType" 
            @change="onControllerTypeChange"
            class="text"
            style="width: 11ch;"
          >
            <option value="Поток">Поток</option>
            <option value="Поток-Д">Поток-Д</option>
          </select>

          <select 
            id="num-klemm"
            v-model="numKlemm" 
            :disabled="controllerType === 'Поток-Д'"
            class="text"
            style="width: 8ch;"
          >
            <option v-for="n in evenNumbers" :key="n" :value="n">{{ n }}</option>
          </select>
          <small v-if="controllerType === 'Поток-Д'" class="form-text">
            Для Поток-Д всегда 12 клемм
          </small>
      </div>

      <!-- Форма для генерации таблицы -->
      <div class="generation-form">
        <div class="mb10">
          <label>Загрузите паспорт в формате .pdf для автоматического заполнения:</label>
        </div>

        <!-- Загрузка паспорта -->
        <div class="mb10">
          <input 
            type="file" 
            @change="handleFileUpload" 
            class="custom-file-input" 
            accept=".pdf"
            ref="fileInput"
          />
        </div>

        <!-- Информация о выбранном файле -->
        <div v-if="selectedFile" class="file-info">
          <p>Выбранный файл: <strong>{{ selectedFile.name }}</strong></p>
          <p>Размер: {{ (selectedFile.size / 1024).toFixed(2) }} KB</p>
        </div>

        <!-- Сообщения о статусе -->
        <div v-if="loading" class="status-message loading">
          {{ loadingMessage }}
        </div>
        
        <div v-if="responseMessage && responseIsError" class="status-message error">
          {{ responseMessage }}
        </div>

        <!-- Кнопка генерации -->
        <button 
          @click="generateSwitchTable" 
          class="btn btn-primary" 
          :disabled="!canGenerate || loading"
        >
          Сгенерировать таблицу коммутаций
        </button>

        <!-- Предпросмотр данных -->
        <div v-if="passportData" class="preview-section">
          <h3>Данные из паспорта:</h3>
          <div class="preview-data">
            <p><strong>Номер:</strong> {{ passportData.passport_info?.number }}</p>
            <p><strong>Адрес:</strong> {{ passportData.passport_info?.address }}</p>
            <p><strong>Направлений:</strong> {{ passportData.total_directions }}</p>
          </div>
        </div>

      </div>
    </div>
      <div class="tools-right">
        <!-- Отображение JSON ответа от паспорта -->
        <div v-if="passportData" class="response-section">
          <h3>Полные данные паспорта:</h3>
          <div class="json-display">
            <pre>{{ formattedPassportResponse }}</pre>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "TabComGen",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath1: "/read-pdf-passport/",
      apiPath2: "/generate-switch-table/",
      selectedFile: null,
      passportData: null,
      responseMessage: "",
      responseIsError: false,
      loading: false,
      loadingMessage: "",
      
      // Параметры для генерации таблицы
      controllerType: "Поток",
      numKlemm: 8,
      filename: "",
      
      // Опции для количества клемм
      evenNumbers: this.generateEvenNumbers(2, 128)
    };
  },
  computed: {
    formattedPassportResponse() {
      if (!this.passportData) return '';
      return JSON.stringify(this.passportData, null, 2);
    },
    canGenerate() {
      return this.passportData && this.filename.trim() !== '';
    }
  },
  methods: {
    generateEvenNumbers(start, end) {
      const numbers = [];
      for (let i = start; i <= end; i += 2) {
        numbers.push(i);
      }
      return numbers;
    },

    onControllerTypeChange() {
      if (this.controllerType === 'Поток-Д') {
        this.numKlemm = 12;
      } else {
        this.numKlemm = 8;
      }
      this.updateFilename();
    },

    updateFilename() {
      if (this.passportData && this.passportData.passport_info?.number) {
        const objectNumber = this.passportData.passport_info.number;
        this.filename = `Таблица коммутации СО ${objectNumber}.xlsx`;
      } else {
        this.filename = "";
      }
    },

    async handleFileUpload(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        this.selectedFile = files[0];
        this.passportData = null;
        this.responseMessage = "";
        this.filename = "";
        
        // Автоматически отправляем файл для чтения паспорта
        await this.readPassport();
      }
    },

    async readPassport() {
      if (!this.selectedFile) {
        this.responseMessage = "Пожалуйста, выберите файл";
        this.responseIsError = true;
        return;
      }

      this.loading = true;
      this.loadingMessage = "Чтение данных из паспорта...";
      this.responseMessage = "";
      this.responseIsError = false;

      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath1}`;
        
        const formData = new FormData();
        formData.append('file', this.selectedFile);

        try {
          const response = await axios.post(server, formData, {
            headers: {
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'multipart/form-data'
            },
            timeout: 30000
          });

          console.log("Passport response from", ip, ":", response);
          
          if (response.data.success) {
            this.passportData = response.data;
            this.responseMessage = `Паспорт успешно обработан сервером ${ip}`;
            this.responseIsError = false;
            this.updateFilename(); // Обновляем имя файла после получения данных
            break;
          } else {
            this.responseMessage = `Ошибка при обработке паспорта: ${response.data.message || 'Неизвестная ошибка'}`;
            this.responseIsError = true;
          }

        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
          
          if (error.response) {
            this.responseMessage = `Ошибка сервера ${ip}: ${error.response.status} - ${error.response.statusText}`;
          } else if (error.request) {
            this.responseMessage = `Не удалось подключиться к серверу ${ip}`;
          } else {
            this.responseMessage = `Ошибка при отправке запроса: ${error.message}`;
          }
          this.responseIsError = true;
        }
      }

      this.loading = false;

      if (!this.passportData && this.responseIsError) {
        this.responseMessage = "Ошибка при обработке паспорта на всех серверах.";
      }
    },

    async generateSwitchTable() {
      if (!this.canGenerate) {
        this.responseMessage = "Загрузите паспорт для генерации таблицы";
        this.responseIsError = true;
        return;
      }

      this.loading = true;
      this.loadingMessage = "Генерация таблицы коммутаций...";
      this.responseMessage = "";
      this.responseIsError = false;

      const requestData = {
        controller_type: this.controllerType,
        num_klemm: this.numKlemm,
        filename: this.filename,
        passport_info: this.passportData.passport_info,
        table_data: this.passportData.table_data
      };

      console.log("Sending data for table generation:", requestData);

      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath2}`;

        try {
          const response = await axios.post(server, requestData, {
            headers: {
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'application/json'
            },
            responseType: 'blob', // Важно для получения файла
            timeout: 30000
          });

          console.log("Table generation response from", ip, ":", response);
          
          // Создаем URL для скачивания файла
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', this.filename);
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.URL.revokeObjectURL(url);

          this.responseMessage = `Таблица успешно сгенерирована сервером ${ip}`;
          this.responseIsError = false;
          break;

        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
          
          if (error.response) {
            this.responseMessage = `Ошибка сервера ${ip}: ${error.response.status} - ${error.response.statusText}`;
          } else if (error.request) {
            this.responseMessage = `Не удалось подключиться к серверу ${ip}`;
          } else {
            this.responseMessage = `Ошибка при генерации таблицы: ${error.message}`;
          }
          this.responseIsError = true;
        }
      }

      this.loading = false;

      if (this.responseIsError) {
        this.responseMessage = "Ошибка при генерации таблицы на всех серверах.";
      }
    }
  }
};
</script>

<style scoped>

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.text:disabled {
  opacity: 0.4;
}

.form-text {
  color: #6c757d;
  font-size: 0.875em;
  margin: 8px;
  opacity: 0.5;
}

.btn-primary {
  background-color: var(--button-3-bgc);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
}

.btn-primary:disabled {
  background-color: var(--button-5-bgc);
  cursor: not-allowed;
}

.file-info {
  background-color: var(--info-2);
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.status-message {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.status-message.loading {
  background-color: var(--info-2);
  border-left: 4px solid #ffc107;
  color: #856404;
}

.status-message.error {
  background-color: var(--info-2);
  border-left: 4px solid #dc3545;
  color: #721c24;
}

.preview-section {
  margin-top: 20px;
  padding: 15px;
  background-color: var(--info-2);
  border-radius: 4px;
  border-left: 4px solid #17a2b8;
}

.preview-data p {
  margin: 5px 0;
}

.response-section h3 {
  margin-bottom: 10px;
  color: #333;
}

.json-display {
  background-color: var(--info-2);
  border: 1px solid var(--border-2);
  border-radius: 4px;
  padding: 15px;
  max-height: 800px;
  overflow-y: auto;
}

.json-display pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}
</style>