<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Получение версии прошивки контроллера</h2>
      <div class="form-inline">

        <input 
          id="ip-address" 
          v-model="ipAddress" 
          type="text" 
          placeholder="Введите IP адрес"
          class="text"
          required
          autocomplete="off"
          style="width: 20ch;"
        >

        <select 
          id="protocol" 
          v-model="selectedProtocol" 
          style="width: 10ch;"
          class="select"
          required
          @change="clearError"
        >
          <option value="" disabled selected>Тип ДК</option>
          <option value="Swarco">Swarco</option>
          <option value="Поток">Поток</option>
        </select>

        <button 
          @click="getFirmware" 
          class="submit-btn"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Загрузка...' : 'Получить' }}
        </button>
      </div>

      <div v-if="responseData" class="response-container">
        <pre class="response">{{ responseData.version }}</pre>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "GetFirmware",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath: "/get_firmware_api/",
      ipAddress: "",
      selectedProtocol: "",
      responseData: null,
      errorMessage: null,
      isLoading: false,
      pollingInterval: null
    };
  },
  methods: {
    clearError() {
      this.errorMessage = null;
    },
    
    validateForm() {
      if (!this.ipAddress.trim()) {
        alert("Пожалуйста, введите IP адрес");
        return false;
      }
      
      if (!this.selectedProtocol) {
        alert("Пожалуйста, выберите тип ДК");
        return false;
      }
      
      return true;
    },

    async getFirmware() {
      if (!this.validateForm()) return;

      this.isLoading = true;
      this.errorMessage = null;
      this.responseData = null;

      const requestData = {
        ip: this.ipAddress,
        protocol: this.selectedProtocol
      };

      // Останавливаем предыдущий интервал
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
      }

      // Начинаем опрос
      this.pollingInterval = setInterval(() => {
        this.pollFirmwareVersion(requestData);
      }, 2000);

      // Первый запрос
      await this.pollFirmwareVersion(requestData);
    },

    async pollFirmwareVersion(requestData) {
      for (let ip of this.serverIPs) {
        try {
          const server = `http://${ip}${this.apiPath}`;
          const response = await axios.post(server, requestData, {
            headers: {
              Authorization: `Token ${this.token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.data.version && response.data.version !== "loading") {
            clearInterval(this.pollingInterval);
            this.responseData = response.data;
            this.isLoading = false;
            return;
          } else if (response.data.version === "loading") {
            this.responseData = response.data;
            return;
          }
        } catch (error) {
          console.warn(`Ошибка подключения к ${ip}:`, error);
          clearInterval(this.pollingInterval);
          this.isLoading = false;
          
          this.errorMessage = error.response?.data?.errorMessage || 
                              error.message || 
                              "Произошла ошибка при получении данных";
          return;
        }
      }
    }
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  }
};
</script>

<style scoped>
.response-container {
  margin-top: 6px;
  padding: 6px;
  border-radius: 4px;
}

.error-message {
  padding: 6px;
  color: #d32f2f;
  border-radius: 4px;
}

.response {
  font-size: 17px;
}
</style>