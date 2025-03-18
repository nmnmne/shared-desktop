<template>
  <div class="container">
    <h2 class="title margin-bottom">Управление контроллером</h2>
    <div class="form-inline">
      <div class="form-column">
        <input
          type="text text-small"
          class="text text-mid"
          id="search_host"
          placeholder="Номер СО"
          v-model="searchValue"
          @input="handleInput"
        />

        <input
          type="text"
          id="ip_address"
          class="text text-mid"
          v-model="ip"
          placeholder="IP-адрес"
        />

        <select
          id="controller_type"
          class="select text-mid"
          v-model="protocol"
        >
          <option value="">Тип ДК</option>
          <option v-for="type in typesControllers" :key="type" :value="type">{{ type }}</option>
        </select>

        <input
          type="text"
          class="text text-mid"
          placeholder="."
        />

        <input
          type="text"
          class="text text-mid"
          placeholder="."
        />
      </div>

      <div class="form-column info-screen width-100">
        <!-- Блок для Swarco -->
        <div v-if="protocol === 'Swarco'">
          <p>{{ protocol }}</p>
          <div class="info-line width-100">
            <span class="lcd-1">Текущий режим: </span>
            <span class="lcd-2">{{ stateTestResponse?.current_mode || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">План: </span>
            <span class="lcd-2">{{ stateTestResponse?.current_plan || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Фаза: </span>
            <span class="lcd-2">{{ stateTestResponse?.current_stage || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Лампы (режим сигнализации): </span>
            <span class="lcd-2">{{ stateTestResponse?.current_status || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">FIXED TIME STATUS: </span>
            <span class="lcd-2">{{ stateTestResponse?.fixed_time_status || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Источник плана: </span>
            <span class="lcd-2">{{ stateTestResponse?.plan_source || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Софт входы 180/181: </span>
            <span class="lcd-2">{{ stateTestResponse?.status_soft_flag180_181 || "Нет данных" }}</span>
          </div>
        </div>

        <!-- Блок для Поток -->
        <div v-else-if="protocol === 'Поток (S)' || protocol ===  'Поток (P)'">
          <div class="info-line width-100">
            <span class="lcd-1">Поток </span>
          </div>
        </div>

        <!-- Блок для Peek -->
        <div v-else-if="protocol === 'Peek'">
          <div class="info-line width-100">
            <span class="lcd-1">Peek </span>
          </div>
        </div>

        <!-- Пусто -->
        <div v-else>
          <div class="info-line width-100"><span class="lcd-1">Ожидание ввода данных</span></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre>Этот инструмент пока на стадии разработки! </pre></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "ManageController",
  data() {
    return {
      searchValue: "",
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      ip: "",
      protocol: "",
      token: import.meta.env.VITE_API_TOKEN,
      stateTestResponse: null,
      intervalId: null,
      statusMessage: "Ожидание данных...",
      lastUpdateTime: "Нет данных",
    };
  },
  computed: {
    isFormValid() {
      return this.ip && this.protocol;
    },
  },
  methods: {
    handleInput() {
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      this.timeoutId = setTimeout(() => {
        this.searchHost();
      }, 1500);
    },
    async searchHost() {
      const searchValue = this.searchValue.trim();
      if (!searchValue) return;

      try {
        const serverIP = serverIPs[0];
        const url = `http://${serverIP}/api/v1/trafficlight-objects/${encodeURIComponent(searchValue)}`;
        console.log("Отправляем запрос по URL:", url);

        const response = await axios.get(url, {
          headers: {
            Authorization: `Token ${this.token}`,
          },
        });

        console.log("Ответ от сервера:", response.data);

        this.ip = response.data.ip_adress || "";
        this.protocol = response.data.type_controller || "";
        console.log("Протокол", protocol);
      } catch (error) {
        console.error("Ошибка при поиске по номеру СО:", error);
        if (error.response) {
          console.error("Данные ошибки:", error.response.data);
          console.error("Статус ошибки:", error.response.status);
        }
      }
    },
    async fetchStateTest() {
      if (!this.ip || !this.protocol) {
        this.stateTestResponse = null;
        this.statusMessage = "IP и тип контроллера не указаны";
        return;
      }

      try {
        const serverIP = serverIPs[0];
        const url = '/api/v1/traffic-lights/get-state';

        const requestData = {
          hosts: {
            [this.ip]: {
              type_controller: this.protocol,
            },
          },
        };

        console.log("Отправляемый JSON:", JSON.stringify(requestData, null, 2));

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        console.log("RES", response.data);
        console.log("PRTC", this.protocol);

        if (this.protocol === "Swarco") {
          this.stateTestResponse = response.data[this.ip].response.data;
        } else if (this.protocol === "Peek") {
          this.stateTestResponse = response.data[this.ip].response.data.streams_data[0];
        } else if (this.protocol === "Поток (P)") {
          this.stateTestResponse = response.data[this.ip].response.data;
        } else if (this.protocol === "Поток (S)") {
          this.stateTestResponse = response.data[this.ip].response.data;
        } else {
          this.stateTestResponse = null;
        }

        this.statusMessage = "Данные успешно получены";
        this.lastUpdateTime = new Date().toLocaleTimeString(); // Обновляем время последнего запроса
      } catch (error) {
        console.error("Ошибка при запросе данных:", error);
        this.statusMessage = "Ошибка при получении данных";
        this.stateTestResponse = null;
      }
    },
    startPolling() {
      this.stopPolling();
      this.intervalId = setInterval(() => {
        this.fetchStateTest();
      }, 1500);
    },
    stopPolling() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    },
  },
  watch: {
    ip() {
      this.startPolling();
    },
    protocol() {
      this.startPolling();
    },
  },
  beforeUnmount() {
    this.stopPolling();
  },
};
</script>

<style scoped>


.form-inline-media {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}


.info-screen {
  background-color: var(--display-bgc);
  border: 2px solid #000000;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Moscow2025', monospace;
}

.info-line {
  margin-bottom: 10px;
  font-size: 16px;
}

.lcd-1 {
  color: var(--display-txt-1);
}

.lcd-2 {
  color: var(--display-txt-2);
}
</style>