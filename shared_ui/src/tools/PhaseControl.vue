<template>
  <div class="container">
    <h2 class="title">Управление фазой</h2>
    <div class="form-inline">
      <input
        type="text"
        class="text"
        id="search_host"
        placeholder="Номер СО"
        style="width: 11ch;"
        v-model="searchValue"
        @input="searchHost"
      />

      <div class="form-group" v-if="showScn" style="display: none;">
        <input
          type="text"
          id="scn"
          class="minitext"
          v-model="scn"
          placeholder="SCN"
          style="width: 10ch;"
          readonly
        />
      </div>

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
        :disabled="!isFormValid || isButtonDisabled"
        @click="setPhase"
      >
        {{ buttonText }}
      </button>

      <div v-if="responseData" class="response-block">
        <pre class="text_">{{ responseData.countdown }}</pre>
      </div>

    </div>
    <div style="margin-top: 30px;">
      <span @click="toggleVisibility" style="cursor: pointer; user-select: none; margin: 7px;">
        {{ isVisible ? 'Скрыть ^' : 'Показать >' }}
      </span>

      <!-- Контейнер с элементами -->
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
          @change="updateScnVisibility"
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
      isVisible: false,
      searchValue: "",
      ip: "",
      protocol: "",
      scn: "",
      showScn: false,
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      token: import.meta.env.VITE_API_TOKEN,
      responseData: null,
      intervalId: null,
      selectedTimeout: 30,
      timeouts: [10, 20, 30, 40, 60, 80, 100, 120, 140, 160, 180],
      selectedPhase: 0,
      phases: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
      16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
      46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
      61, 62, 63, 64, 65],
      isButtonDisabled: false,
      countdown: 0,
      countdownInterval: null,
    };
  },
  computed: {

    isFormValid() {
      return this.ip && this.protocol;
    },

    buttonText() {
      return this.isButtonDisabled ? `${this.countdown} сек` : "Включить";
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

        this.updateScnVisibility();
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
    updateScnVisibility() {
      this.showScn = this.protocol === "Поток (P)" || this.protocol === "Peek";

      if (this.showScn) {
        this.updateScn();
      } else {
        this.scn = "";
      }
    },
    updateScn() {
      const searchValue = this.searchValue.trim();
      if (!searchValue) {
        this.scn = "";
        return;
      }

      if (this.protocol === "Peek") {
        this.scn = `CO${searchValue}`;
      } else if (this.protocol === "Поток (P)") {
        const paddedNumber = searchValue.slice(-4).padStart(4, "0");
        this.scn = `CO${paddedNumber}`;
      } else {
        this.scn = "";
      }
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

        this.responseData = response.data;
      } catch (error) {
        console.error("Ошибка при запросе данных:", error);
        this.responseData = { error: "Не удалось получить данные" };
      }
    },

    async setPhase() {
      if (!this.isFormValid || this.isButtonDisabled) return;

      this.startCountdown();

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

    startCountdown() {
      this.isButtonDisabled = true;
      this.countdown = this.selectedTimeout;

      this.countdownInterval = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--;
        } else {
          clearInterval(this.countdownInterval);
          this.isButtonDisabled = false;
        }
      }, 1000);
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
  },
  watch: {
    protocol() {
      this.updateScnVisibility();
      this.isButtonDisabled = false;
      clearInterval(this.countdownInterval);
    },
    searchValue() {
      this.updateScn();
    },
    ip() {
      this.startPolling();
      this.isButtonDisabled = false;
      clearInterval(this.countdownInterval);
    },
    protocol() {
      this.startPolling();
    },
    selectedTimeout() {
      this.startPolling();
    },
    selectedPhase() {
      this.fetchData();
      this.isButtonDisabled = false;
      clearInterval(this.countdownInterval);
    },
  },

  beforeUnmount() {
    this.stopPolling();
    clearInterval(this.countdownInterval);
  },
};
</script>

<style scoped>
.hidden {
  display: none;
}
</style>