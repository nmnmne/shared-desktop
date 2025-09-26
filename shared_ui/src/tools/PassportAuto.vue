<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Паспорт СО</h2>

      <div class="form-inline">
        <input type="file" @change="handleFileUpload" class="custom-file-input" multiple />
      </div>

      <div v-if="responseMessage">
        <p :class="{ 'error': responseIsError }">{{ responseMessage }}</p>
      </div>

      <div v-if="processingFiles.length > 0" class="files-list">
        <div v-for="(fileInfo, index) in processingFiles" :key="index" class="file-item">
          <div class="file-name">{{ fileInfo.originalName }}</div>
          <div class="file-status">
            <span v-if="fileInfo.status === 'pending'" class="status-pending">Ожидает обработки</span>
            <span v-if="fileInfo.status === 'processing'" class="status-processing">Обрабатывается...</span>
            <span v-if="fileInfo.status === 'processed'" class="status-processed">Обработан</span>
            <span v-if="fileInfo.status === 'error'" class="status-error">Ошибка</span>
            
            <button 
              v-if="fileInfo.status === 'processed'" 
              @click="downloadFile(fileInfo)"
              class="download-btn"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { fastApiServer } from "@/assets/js/config";

export default {
  name: "PassportAuto",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      apiUrl: `http://${fastApiServer}/api/v1/passport/validation`,
      selectedFiles: [],
      processingFiles: [],
      responseMessage: "",
      responseIsError: false,
    };
  },
  methods: {
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      if (files.length === 0) return;

      this.selectedFiles = files;
      this.responseMessage = "";

      // Если выбран один файл - обрабатываем сразу
      if (files.length === 1) {
        this.processSingleFile(files[0]);
      } else {
        // Если несколько файлов - добавляем в список для обработки
        this.prepareFilesList(files);
      }
    },

    prepareFilesList(files) {
      this.processingFiles = files.map(file => ({
        file: file,
        originalName: file.name,
        status: 'pending',
        processedData: null,
        error: null
      }));
    },

    async processSingleFile(file) {
      const fileInfo = {
        file: file,
        originalName: file.name,
        status: 'processing',
        processedData: null,
        error: null
      };
      
      this.processingFiles = [fileInfo];
      
      try {
        this.responseMessage = "Обработка файла...";
        this.responseIsError = false;

        const formData = new FormData();
        formData.append("files", file);

        const response = await axios.post(this.apiUrl, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Token ${this.token}`,
          },
          responseType: 'blob'
        });

        fileInfo.processedData = response.data;
        fileInfo.status = 'processed';
        
        // Автоматически сохраняем одиночный файл
        this.downloadFile(fileInfo);
        
        this.responseMessage = "Файл успешно обработан и сохранен!";
        this.responseIsError = false;

      } catch (error) {
        console.warn("Ошибка при загрузке файла:", error);
        fileInfo.status = 'error';
        fileInfo.error = error;
        this.responseMessage = "Ошибка при обработке файла.";
        this.responseIsError = true;
      }
    },

    async processMultipleFiles() {
      for (const fileInfo of this.processingFiles) {
        if (fileInfo.status === 'pending') {
          await this.processFile(fileInfo);
        }
      }
    },

    async processFile(fileInfo) {
      fileInfo.status = 'processing';
      
      try {
        const formData = new FormData();
        formData.append("files", fileInfo.file);

        const response = await axios.post(this.apiUrl, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Token ${this.token}`,
          },
          responseType: 'blob'
        });

        fileInfo.processedData = response.data;
        fileInfo.status = 'processed';
        
      } catch (error) {
        console.warn("Ошибка при обработке файла:", error);
        fileInfo.status = 'error';
        fileInfo.error = error;
      }
    },

    downloadFile(fileInfo) {
      if (!fileInfo.processedData) {
        console.warn("Нет данных для сохранения");
        return;
      }

      // Создаем URL для скачивания файла
      const blob = new Blob([fileInfo.processedData]);
      const downloadUrl = window.URL.createObjectURL(blob);
      
      // Генерируем имя для скачиваемого файла
      const originalName = fileInfo.originalName;
      const extension = originalName.lastIndexOf('.') > -1 
        ? originalName.substring(originalName.lastIndexOf('.'))
        : '.txt';
      const processedFileName = `обработанный_${originalName.split('.')[0]}${extension}`;

      // Создаем временную ссылку и автоматически кликаем по ней
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = processedFileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Освобождаем память
      setTimeout(() => {
        window.URL.revokeObjectURL(downloadUrl);
      }, 100);

      console.log("Файл сохранен:", processedFileName);
    },

    // Метод для обработки всех файлов по кнопке (если понадобится)
    processAllFiles() {
      this.processMultipleFiles();
    }
  },
  watch: {
    // Автоматически начинаем обработку при добавлении нескольких файлов
    processingFiles: {
      handler(newFiles) {
        if (newFiles.length > 1) {
          // Небольшая задержка для отображения статуса "Ожидает обработки"
          setTimeout(() => {
            this.processMultipleFiles();
          }, 100);
        }
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.error {
  color: red;
}

.files-list {
  margin-top: 20px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.file-name {
  flex: 1;
  font-weight: 500;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-pending {
  color: #666;
}

.status-processing {
  color: #ff9800;
}

.status-processed {
  color: #4caf50;
}

.status-error {
  color: #f44336;
}

.download-btn {
  padding: 5px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.download-btn:hover {
  background-color: #45a049;
}

.download-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>