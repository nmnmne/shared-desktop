<template>
  <div class="container tools-left">
    <h2 class="title margin-bottom">Управление фазой</h2>
    <div class="form-inline-media">
      <input
        type="text text-small"
        class="text"
        id="search_host"
        placeholder="Номер СО"
        v-model="searchValue"
        @input="handleInput"
      />

      <select
        id="timeout"
        class="select text-small"
        v-model="selectedTimeout"
        @change="startPolling"
      >
        <option v-for="timeout in timeouts" :key="timeout" :value="timeout">{{ timeout }} сек</option>
      </select>

      <select
        id="phase"
        class="select text-small margin-bottom"
        v-model="selectedPhase"
      >
        <option v-for="(value, index) in phases" :key="index" :value="value">
          {{ index === 0 ? "LOCAL" : `${index} фаза` }}
        </option>
      </select>

      <button
        class="margin-bottom"
        :disabled="!isFormValid"
        @click="setPhase"
      >
        Включить
      </button>

      <div v-if="responseData" class="form-inline">
        <pre class="text_">{{ responseData.countdown }}</pre>
        <pre class="text_" style="color: goldenrod;">{{ stateResponse }}</pre>
        <pre class="text_" style="color: yellowgreen;">{{ countdownTimer }} сек</pre>
      </div>
    </div>

    <div class="margin-top">
      <span @click="toggleVisibility" style="cursor: pointer; user-select: none; margin: 7px;">
        {{ isVisible ? 'Скрыть ^' : 'Показать >' }}
      </span>

      <div style="margin-top: 25px;" :class="{ hidden: !isVisible }">
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
      stateResponse: null,
      stateTestResponse: null,
      intervalId: null,
      selectedTimeout: 60,
      timeouts: [10, 20, 30, 40, 60, 80, 100, 120, 140, 160, 180],
      selectedPhase: 0,
      phases: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
      16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
      46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
      61, 62, 63, 64, 65],
      timeoutId: null,
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
      }, 1000);
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
    async fetchStateTest() {
      if (!this.ip || !this.protocol) {
        this.stateResponse = null;
        return;
      }

      try {
        const serverIP = serverIPs[0];
        const url = `http://${serverIP}/api/v1/manage-controller/`;

        const requestData = {
          hosts: {
            [this.ip]: {
              host_id: 1,
              type_controller: this.protocol,
              request_entity: ["get_state"]
            }
          },
          num_hosts_in_request: 1,
          type_request: "get_state"
        };

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        console.log("/RES-manage-controller/", response.data)
        if (this.protocol === "Swarco") {
          this.stateResponse = response.data[this.ip].responce_entity.raw_data.current_states.basic.current_mode;
        } else if (this.protocol === "Peek") {
          this.stateResponse = response.data[this.ip].responce_entity.raw_data.current_states.basic.stream_info["1"].current_mode;
        } else if (this.protocol === "Поток (P)") {
          this.stateResponse = response.data[this.ip].responce_entity.raw_data.current_states.basic.current_mode;
        } else if (this.protocol === "Поток (S)") {
          this.stateResponse = response.data[this.ip].responce_entity.raw_data.current_states.basic.current_mode;
        } else {
          this.stateResponse = null; 
        }
    
    //     const url = '/api/v1/traffic-lights/get-state-test';

    // const requestData = {
    //   hosts: {
    //     [this.ip]: {
    //       type_controller: this.protocol,
    //     },
    //   },
    // };

    //     console.log("Отправляемый JSON:", JSON.stringify(requestData, null, 2));

    //     const response = await axios.post(url, requestData, {
    //       headers: {
    //         "Content-Type": "application/json",
    //       },
    //     });

    //     console.log("RES", response.data)
    //     console.log("PRTC", this.protocol)
    //     if (this.protocol === "Swarco") {
    //       this.stateTestResponse = response.data[this.ip].response.data.current_mode;
    //     } else if (this.protocol === "Peek") {
    //       this.stateTestResponse = response.data[this.ip].response.data.streams_data[0].current_mode;
    //     } else if (this.protocol === "Поток (P)") {
    //       this.stateTestResponse = response.data[this.ip].response.data.current_mode;
    //     } else if (this.protocol === "Поток (S)") {
    //       this.stateTestResponse = response.data[this.ip].response.data.current_mode;
    //     } else {
    //       this.stateTestResponse = null; 
    //     }

      } catch (error) {
        console.error("Ошибка при запросе данных:", error);
        this.stateResponse = "";
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
        this.fetchStateTest();
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