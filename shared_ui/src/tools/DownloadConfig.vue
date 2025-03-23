<template>
  <div class="container tools-left">
    <h2 class="title">Скачать конфигурацию Swarco</h2>

      <div style="margin-bottom: 5px;" class="form-inline">
        <input
          type="text"
          class="text text-mid"
          placeholder="Номер СО"
          v-model="searchController"
          @input="handleInput"
          style="width: 10ch;"
        />

        <input
          type="text"
          class="text text-mid"
          placeholder="000.000.000.000"
          v-model="ipAddrVal"
          @input="handleIpInput"
        />

        <input
          type="text"
          class="text_ text-mid"
          v-model="typeControllerVal"
          placeholder="Тип ДК"
          disabled
          style="width: 10ch;"
        />

        <button
          id="get_config"
          class="button"
          @click="downloadConfig"
          :style="{
            backgroundColor: isLoading ? 'var(--yellow)' : '',
            color: isLoading ? 'black' : ''
          }"
          :disabled="isLoading"
          style="width: 25ch;"
        >
          {{ isLoading ? 'Ждите...' : 'Скачать конфиг' }}
        </button>
      </div>

  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "DownloadConfig",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      searchController: '',
      timeoutId: null,
      ipAddrVal: '',
      typeControllerVal: '',
      addressVal: '',
      descriptionVal: '',
      isLoading: false,
    };
  },
  methods: {
    // Обработка ввода с задержкой
    handleInput() {
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      this.timeoutId = setTimeout(() => {
        this.searchHost();
      }, 700);
    },

    // Обработка ввода IP-адреса вручную
    handleIpInput() {
      // Если IP введен вручную, сбрасываем поле поиска
      this.searchController = '';
    },

    async searchHost() {
      const searchValue = this.searchController.trim();
      if (!searchValue) {
        this.clearResults();
        return;
      }

      try {
        const response = await this.sendRequest(
          `/api/v1/trafficlight-objects/${encodeURIComponent(searchValue)}`
        );

        if (response) {
          this.ipAddrVal = response.ip_adress || "";
          this.typeControllerVal = response.type_controller || "";
          this.addressVal = response.address || "";
          this.descriptionVal = response.description || "";
        }
      } catch (error) {
        console.error("Ошибка при поиске по номеру СО:", error);
        this.clearResults();
      }
    },

    clearResults() {
      this.ipAddrVal = "";
      this.typeControllerVal = "";
      this.addressVal = "";
      this.descriptionVal = "";
    },

    async downloadConfig() {
      if (!this.ipAddrVal) {
        alert("Пожалуйста, введите IP-адрес.");
        return;
      }

      // Если поле поиска не пустое, проверяем тип ДК
      if (this.searchController.trim() && this.typeControllerVal !== 'Swarco') {
        alert("Тип ДК должен быть Swarco.");
        return;
      }

      // Устанавливаем состояние загрузки
      this.isLoading = true;

      // Если тип ДК не указан, отправляем Swarco по умолчанию
      const typeController = this.typeControllerVal || 'Swarco';

      const data = {
        hosts: {
          [this.ipAddrVal]: {
            host_id: this.searchController,
            request_entity: ['get_config'],
            type_controller: typeController, // Используем значение по умолчанию, если тип ДК не указан
            address: this.addressVal,
          },
        },
        type_request: 'get_config',
      };

      try {
        const response = await this.sendRequest('/api/v1/download-config/', data);
        console.log('response', response);

        // Проверяем, что ответ содержит данные
        if (response && this.ipAddrVal in response) {
          const responseData = response[this.ipAddrVal];

          // Проверяем наличие ошибки
          if (responseData.request_errors) {
            console.error("Ошибка при загрузке конфигурации:", responseData.request_errors);
            alert(`Ошибка: ${responseData.request_errors}`);
            return;
          }

          // Проверяем наличие url_to_archive
          if (responseData.responce_entity && responseData.responce_entity.url_to_archive) {
            const urlToFile = responseData.responce_entity.url_to_archive;
            const fileName = Object.keys(urlToFile)[0];
            const fileUrl = urlToFile[fileName];

            // Создаем ссылку для скачивания
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = fileName;
            link.click();
          } else {
            console.error("Ключ 'responce_entity.url_to_archive' отсутствует в ответе");
            alert("Ошибка: Не удалось получить ссылку для скачивания.");
          }
        } else {
          console.error("Ответ сервера пуст или некорректен");
          alert("Ошибка: Некорректный ответ сервера.");
        }
      } catch (error) {
        console.error("Ошибка при загрузке конфигурации:", error);
        alert("Ошибка при загрузке конфигурации.");
      } finally {
        // Сбрасываем состояние загрузки
        this.isLoading = false;
      }
    },

    // Отправка запроса на сервер
    async sendRequest(url, data = null) {
      for (let ip of this.serverIPs) {
        const server = `http://${ip}${url}`;
        try {
          const config = {
            headers: {
              Authorization: `Token ${this.token}`,
            },
          };
          const response = data
            ? await axios.post(server, data, config)
            : await axios.get(server, config);
          return response.data;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }
      alert('Ошибка при отправке данных ко всем серверам.');
      return null;
    },
  },
};
</script>

<style scoped>
.button {
  transition: background-color 0.3s ease;
}
</style>