<template>
  <div class="container">
    <h2 class="title">Управление фазой</h2>
    <div class="form-inline">
      <input
        type="text"
        class="text"
        id="search_host"
        placeholder="НомерСО"
        style="width: 9ch;"
        v-model="searchValue"
        @input="searchHost"
      />

      <select
        id="timeout"
        class="select"
        style="width: 10ch;"
        v-model="selectedTimeout"
        @change="startPolling"
      >
        <option v-for="timeout in timeouts" :key="timeout" :value="timeout">{{ timeout }} сек</option>
      </select>

      <select
        id="phase"
        class="select"
        style="width: 9ch;"
        v-model="selectedPhase"
      >
      <option v-for="(value, index) in phases" :key="index" :value="value">
        {{ index === 0 ? "LOCAL" : `${index} фаза` }}
      </option>
      </select>

      <button
        class="btn btn-primary"
        :disabled="!isFormValid"
        @click="setPhase"
      >
        Включить
      </button>
      
      <div v-if="responseData" class="form-inline">
        <pre class="text_">{{ responseData.countdown }}</pre>
        <pre class="text_" style="color: yellowgreen;">{{ countdownTimer }} сек</pre>
      </div>

    </div>
    <div style="margin-top: 30px;">
      <span @click="toggleVisibility" style="cursor: pointer; user-select: none; margin: 7px;">
        {{ isVisible ? 'Скрыть ^' : 'Если не получается по номеру СО >' }}
      </span>

      <div :class="{ hidden: !isVisible }">
        <input
          type="text"
          id="ip_address"
          class="text"
          v-model="ip"
          placeholder="IP-адрес"
          style="width: 17ch;"
        />

        <select
          id="controller_type"
          class="text"
          style="width: 10ch;"
          v-model="protocol"
        >
          <option value="">Тип ДК</option>
          <option v-for="type in typesControllers" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "PhaseControl",
  data() {
    return {
      countdownTimer: 0,
      countdownIntervalId: null,
      isVisible: false,
      searchValue: "",
      ip: "",
      protocol: "",
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      token: import.meta.env.VITE_API_TOKEN,
      responseData: null,
      intervalId: null,
      selectedTimeout: 60,
      timeouts: [10, 20, 30, 40, 60, 80, 100, 120, 140, 160, 180],
      selectedPhase: 0,
      phases: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
      16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
      46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
      61, 62, 63, 64, 65],
    };
  },
  computed: {
    isFormValid() {
      return this.ip && this.protocol;
    },
  },
  methods: {
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
      } catch (error) {
        console.error("Ошибка при поиске по номеру СО:", error);
        if (error.response) {
          console.error("Данные ошибки:", error.response.data);
          console.error("Статус ошибки:", error.response.status);
        }
      }
    },
    toggleVisibility() {
      this.isVisible = !this.isVisible;
    },

    async fetchData() {
      if (!this.ip || !this.protocol) {
        this.responseData = null;
        return;
      }

      try {
        const serverIP = serverIPs[0];
        const protocolMap = {
          "Swarco": "STCIP",
          "Поток (S)": "STCIP",
          "Поток (P)": "UG405",
          "Peek": "UTMC",
        };
        const selectedProtocol = protocolMap[this.protocol];

        const url = `http://${serverIP}/get_phase`;
        const params = {
          ip_address: this.ip,
          protocol: selectedProtocol,
        };

        const response = await axios.get(url, {
          params,
          headers: {
            Authorization: `Token ${this.token}`,
          },
        });

        if (this.responseData?.countdown !== response.data.countdown) {
          this.startCountdown();
        }

        this.responseData = response.data;
      } catch (error) {
        console.error("Ошибка при запросе данных:", error);
        this.responseData = { error: "Не удалось получить данные" };
      }
    },

    async setPhase() {
      if (!this.isFormValid) return;

      const serverIP = serverIPs[0];
      const protocolMap = {
        "Swarco": "STCIP",
        "Поток (S)": "STCIP",
        "Поток (P)": "UG405",
        "Peek": "UTMC",
      };
      const selectedProtocol = protocolMap[this.protocol];

      const url = `http://${serverIP}/set_phase`;
      const params = {
        ip_address: this.ip,
        protocol: selectedProtocol,
        phase_value: this.selectedPhase,
        timeout: this.selectedTimeout,
      };

      const response = await axios.get(url, {
        params,
        headers: {
          Authorization: `Token ${this.token}`,
        },
      });

    },

    startPolling() {
      this.stopPolling();
      this.intervalId = setInterval(() => {
        this.fetchData();
      }, this.selectedTimeout * 50);
    },

    stopPolling() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    },
    startCountdown() {
      this.stopCountdown();
      this.countdownTimer = 0;
      this.countdownIntervalId = setInterval(() => {
        this.countdownTimer += 1;
      }, 1000);
    },
    stopCountdown() {
      if (this.countdownIntervalId) {
        clearInterval(this.countdownIntervalId);
        this.countdownIntervalId = null;
      }
    },
  },
  watch: {
    searchValue() {
      this.updateScn();
    },
    ip() {
      this.startPolling();
    },
    protocol() {
      this.startPolling();
    },
    selectedTimeout() {
      this.startPolling();
    },
    selectedPhase() {
      this.fetchData();
    },
  },

  beforeUnmount() {
    this.stopPolling();
  },
};
</script>

<style scoped>
.hidden {
  display: none;
}
</style>