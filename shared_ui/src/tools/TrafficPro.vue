<template>
  <div class="tools">
  <div class="container tools-left">
    <h2 class="title margin-bottom">Расширенное управление дорожным контроллером</h2>
    <div class="form-inline">
      <div class="form-column mt">
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
          v-model="type_controller"
        >
          <option value="">Тип ДК</option>
          <option v-for="type in typesControllers" :key="type" :value="type">{{ type }}</option>
        </select>

        <input
          type="text"
          class="text text-mid"
          placeholder="command"
          v-model="command"
        />

        <input
          type="text"
          class="text text-mid"
          placeholder="options"
          v-model="options"
        />

        <input
          type="text"
          class="text text-mid"
          placeholder="value"
          v-model="value"
        />

        <button
          class='text'
          style="background-color: var(--header-bcg);
          color: var(--text1);"
          @click="setCommand"
        >
          set-command
        </button>
        <a
          :href="'http://' + ip"
          target="_blank"
          class='text'
          style="background-color: var(--header-bcg);
          color: var(--text1);
          text-align: center;"
          v-if="ip"
        >
          go-to-web
        </a>
      </div>

      <div class="form-column info-screen width-100">
        <!-- Блок для Swarco -->
        <div v-if="type_controller === 'Swarco'">
          <div class="info-line width-100">
            <span class="lcd-1">Текущий режим: </span>
            <span class="lcd-2">{{ stateResponse?.current_mode || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">План: </span>
            <span class="lcd-2">{{ stateResponse?.current_plan || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Фаза: </span>
            <span class="lcd-2">{{ stateResponse?.current_stage || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Лампы (режим сигнализации): </span>
            <span class="lcd-2">{{ stateResponse?.current_status || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">FIXED TIME: </span>
            <span class="lcd-2">{{ stateResponse?.fixed_time_status || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Источник плана: </span>
            <span class="lcd-2">{{ stateResponse?.plan_source || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Детекторы: </span>
            <span class="lcd-2">{{ stateResponse?.num_detectors || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Софт входы 180/181: </span>
            <span class="lcd-2">{{ stateResponse?.status_soft_flag180_181 || "Нет данных" }}</span>
          </div>
        </div>

        <!-- Блок для Поток (P)-->
        <div v-else-if="type_controller === 'Поток (P)'">
          <!-- Общая информация -->

          <div class="info-line width-100">
            <span class="lcd-1">Режим: </span>
            <span class="lcd-2">{{ stateResponse?.current_mode || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">План: </span>
            <span class="lcd-2">{{ stateResponse?.current_plan || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Фаза: </span>
            <span class="lcd-2">{{ stateResponse?.current_stage || "Нет данных" }}</span>
          </div>

          <br>

          <div class="info-line width-100">
            <span class="lcd-1">Ошибки детекторов: </span>
            <span class="lcd-2">{{ stateResponse?.has_det_faults === '1' ? 'Есть' : 'Нет' }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Количество детекторов: </span>
            <span class="lcd-2">{{ stateResponse?.num_detectors || "Нет данных" }}</span>
          </div>

          <br>

          <div class="info-line width-100">
            <span class="lcd-1">ВПУ: </span>
            <span class="lcd-2">{{ stateResponse?.is_mode_man }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Flash: </span>
            <span class="lcd-2">{{ stateResponse?.flash }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Dark: </span>
            <span class="lcd-2">{{ stateResponse?.dark}}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Лампы (режим сигнализации): </span>
            <span class="lcd-2">{{ stateResponse?.curr_status_mode || "Нет данных" }}</span>
          </div>

          <br>

          <div class="info-line width-100">
            <span class="lcd-1">Operation mode: </span>
            <span class="lcd-2">{{ stateResponse?.operation_mode || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Local adaptive status: </span>
            <span class="lcd-2">{{ stateResponse?.local_adaptive_status === '1' ? 'Активно' : 'Не активно' || "Нет данных" }}</span>
          </div>

        </div>

        <!-- Блок для Поток (S) -->
        <div v-else-if="type_controller === 'Поток (S)'">
          <!-- Общая информация -->
          <div class="info-line width-100">
            <span class="lcd-1">Режим: </span>
            <span class="lcd-2">{{ stateResponse?.current_mode || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">План: </span>
            <span class="lcd-2">{{ stateResponse?.current_plan || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Фаза: </span>
            <span class="lcd-2">{{ stateResponse?.current_stage || "Нет данных" }}</span>
          </div>

          <br>

          <div class="info-line width-100">
            <span class="lcd-1">Лампы (режим сигнализации): </span>
            <span class="lcd-2">{{ stateResponse?.current_status || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Количество детекторов: </span>
            <span class="lcd-2">{{ stateResponse?.num_detectors || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">curr_status_mode: </span>
            <span class="lcd-2">{{ stateResponse?.curr_status_mode || "Нет данных" }}</span>
          </div>

        </div>

        <!-- Блок для Peek -->
        <div v-else-if="type_controller === 'Peek'">

          <div v-if="stateResponse?.streams_data?.length > 0">
            <div v-for="(stream, index) in stateResponse.streams_data" :key="index" class="info-line width-100">
              <div class="info-line width-100">
                <div v-if="stateResponse?.streams_data?.length > 1">
                  <span class="lcd-1">XP </span>
                  <span class="lcd-2">{{ stream.xp }} </span>
                <br>
              </div>
                <span class="lcd-1">Режим:</span>
                <span class="lcd-2">{{ stream.current_mode || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Фаза: </span>
                <span class="lcd-2">{{ stream.current_stage || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Статус: </span>
                <span class="lcd-2">{{ stream.current_status || "Нет данных" }}</span>
              </div>
              <br>
            </div>
          </div>

          <!-- <div class="info-line width-100">
            <span class="lcd-1">Адрес: </span>
            <span class="lcd-2">{{ stateResponse?.current_address || "Нет данных" }}</span>
          </div> -->

          <div class="info-line width-100">
            <span class="lcd-1">План: </span>
            <span class="lcd-2">{{ stateResponse?.current_plan || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Время: </span>
            <span class="lcd-2">{{ stateResponse?.current_time || "Нет данных" }}</span>
          </div>

          <div class="info-line width-100">
            <span class="lcd-1">Ошибки: </span>
            <span class="lcd-2">{{ stateResponse?.current_alarms || "Нет данных" }}</span>
          </div>

        </div>

        <div v-else>
          <div class="info-line width-100"><span class="lcd-1">Ожидание ввода данных</span></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre> </pre></div>
          <div class="info-line width-100"><pre>Этот инструмент пока на стадии разработки! </pre></div>
        </div>
      </div>

    </div>

    <div class="description" v-if="address !== ''">
      <span><strong>Адрес: </strong></span>
      <span>{{ address || "" }}</span>
    </div>

    <div class="description" v-if="description !== ''">
      <span><strong>Описание: </strong></span>
      <span>{{ description || "" }}</span>
    </div>

  </div>
  <div class="container tools-right" >
    <p>Временный блок разработчика</p>

    <div class="response-block" v-if="setCommandRequest">
      <h3>Запрос на сервер:</h3>
      <pre>{{ setCommandRequest }}</pre>
    </div>

    <div class="response-block" v-if="commandResponse">
      <h3>Ответ от сервера:</h3>
      <pre>{{ commandResponse }}</pre>
    </div>

  </div>
  
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "TrafficPro",
  data() {
    return {
      searchValue: "",
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      ip: "",
      type_controller: "",
      address: "",
      description: "",
      stateResponse: null,
      intervalId: null,
      statusMessage: "Ожидание данных...",
      lastUpdateTime: "Нет данных",
      command: "",
      options: "",
      value: "",
      commandResponse: null,
      setCommandRequest: null,
    };
  },
  computed: {
    isFormValid() {
      return this.ip && this.type_controller;
    },
  },
  methods: {
    async setCommand() {
      if (!this.ip || !this.type_controller) {
        console.error("IP и тип контроллера обязательны для выполнения команды.");
        return;
      }

      const requestData = {
        hosts: {
          [this.ip]: {
            type_controller: this.type_controller,
          },
        },
      };

      if (this.command) {
        requestData.hosts[this.ip].command = this.command;
      }
      if (this.options) {
        requestData.hosts[this.ip].options = this.options;
      }
      if (this.value) {
        requestData.hosts[this.ip].value = Number(this.value);
      }
      console.log("Отправляемый JSON:", JSON.stringify(requestData, null, 2));
      this.setCommandRequest = requestData
      try {
        const url = '/api/v1/traffic-lights/set-command';
        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        this.commandResponse = response.data;
        console.log("Команда успешно отправлена:", response.data);
      } catch (error) {
        console.error("Ошибка при отправке команды:", error);
        if (error.response) {
          console.error("Данные ошибки:", error.response.data);
          console.error("Статус ошибки:", error.response.status);
          this.commandResponse = error.response.data;
        } else {
          this.commandResponse = { error: "Ошибка сети или сервера" };
        }
      }
    },
    handleInput() {
      this.clearFields();

      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      
      this.timeoutId = setTimeout(() => {
        this.searchHost();
      }, 1500);
    },
    clearFields() {
      this.ip = "";
      this.type_controller = "";
      this.address = "";
      this.description = "";
      this.stateResponse = null;
    },
    async searchHost() {
      const searchValue = this.searchValue.trim();
      if (!searchValue) return;

      try {
        const url = '/api/v1/traffic-lights/properties';

        const requestData = {
          hosts: [searchValue],
        };

        // console.log("Отправляемый JSON:", JSON.stringify(requestData, null, 2));

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });
        console.log('response properties:', response.data.results?.[0]?.[searchValue]?.db_records?.[0] || 'No IP address found');

        this.ip = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.ip_adress || "";
        this.type_controller = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.type_controller || "";
        this.address = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.address || "";
        this.description = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.description || "";
      } catch (error) {
        console.error("Ошибка при поиске по номеру СО:", error, '!!!');
        if (error.response) {
          console.error("Данные ошибки:", error.response.data);
          console.error("Статус ошибки:", error.response.status);
        }
      }
    },
    async fetchStateTest() {
      if (!this.ip || !this.type_controller) {
        this.stateResponse = null;
        this.statusMessage = "IP и тип контроллера не указаны";
        return;
      }

      try {
        const url = '/api/v1/traffic-lights/get-state';

        const requestData = {
          hosts: {
            [this.ip]: {
              type_controller: this.type_controller,
            },
          },
        };

        // console.log("Отправляемый JSON:", JSON.stringify(requestData, null, 2));

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        // console.log("RES", response.data[this.ip].response.data);
        // console.log("PRTC", this.type_controller);

        if (this.type_controller === "Swarco") {
          this.stateResponse = response.data[this.ip].response.data;
        } else if (this.type_controller === "Peek") {
          this.stateResponse = response.data[this.ip].response.data;
        } else if (this.type_controller === "Поток (P)") {
          this.stateResponse = response.data[this.ip].response.data;
        } else if (this.type_controller === "Поток (S)") {
          this.stateResponse = response.data[this.ip].response.data;
        } else {
          this.stateResponse = null;
        }

        this.statusMessage = "Данные успешно получены";
        this.lastUpdateTime = new Date().toLocaleTimeString();
      } catch (error) {
        console.error("Ошибка при запросе данных:", error);
        this.statusMessage = "Ошибка при получении данных";
        this.stateResponse = null;
      }
    },
    startPolling() {
      this.stopPolling();
      this.intervalId = setInterval(() => {
        this.fetchStateTest();
      }, 2000);
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
    type_controller() {
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
  border: 3px solid var(--body);
  border-radius: 6px;
  padding: 9px;
  font-family: 'Moscow2025', monospace;
  box-shadow: inset 1px 1px 1px rgba(0, 0, 0, 0.2);
  overflow: auto;
}

.info-line {
  margin-bottom: 4px;
  font-size: 16px;
}

.mt {
  margin: 1px 2px 8px 0px;
}

.lcd-1 {
  color: var(--display-txt-1);
}

.lcd-2 {
  color: var(--display-txt-2);
}

.description {
  margin-top: 20px ;
}




/* Временное */
.response-block {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
}

</style>