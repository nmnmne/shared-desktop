<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title margin-bottom">Расширенное управление дорожным контроллером</h2>
      
      <!-- Кнопка для показа/скрытия -->
      <div class='mb10'>
        <a class='preset_' href="#" @click.prevent="showSelect = !showSelect">
          {{ showSelect ? 'Скрыть выбор пресета' : 'Показать выбор пресета' }}
        </a>
      </div>

      <div v-show="showSelect">
        <!-- Выбор пресета -->
        <div>
          <select class="preset" style="padding: 2px 10px 1px 2px" v-model="selectedPresetId" @change="loadPreset">
            <option disabled value="">Выберите пресет</option>
            <option v-for="preset in presets" :key="preset.id" :value="preset.id">
              {{ preset.name }}
            </option>
          </select>

          <!-- Сохранение пресета -->
          <input class="preset" v-model="presetName" placeholder="Название сохроняемого" />
          <button class="preset" @click="savePreset">Сохранить как пресет</button>
        </div>
      </div>
  
      <!-- Выбор количества контроллеров -->
      <div class="form-inline">
        <div class="form-column mt controller-group">
          <select v-model="cloneCount" class="select text-mid">
            <option v-for="n in 16" :value="n" :key="n">
              {{ n }} {{ n === 1 ? 'контроллер' : n >= 2 && n <= 4 ? 'контроллера' : 'контроллеров' }}
            </option>
          </select>
        </div>
      </div>

      <!-- Блоки контроллеров -->
      <div v-for="(controller, index) in controllers" :key="index" class="controller-group">
        <h3 class="mb10">Контроллер {{ index + 1 }}</h3>
        
        <div class="form-inline">
          <div class="form-column mt">
            <input
              type="text"
              class="text text-mid"
              :placeholder="'Номер СО ' + (index + 1)"
              v-model="controller.searchValue"
              @input="handleInput(index)"
            />

            <input
              type="text"
              class="text text-mid"
              v-model="controller.ip"
              :placeholder="'IP-адрес ' + (index + 1)"
            />

            <select
              class="select text-mid"
              v-model="controller.type_controller"
              @change="fetchCommandsAndOptions(index)"
            >
              <option disabled value="">Тип ДК</option>
              <option v-for="type in typesControllers" :key="type" :value="type">{{ type }}</option>
            </select>

            <!-- Команда -->
            <select
              class="select text-mid"
              v-model="controller.command"
              @change="updateCommandFields(index)"
              v-if="controller.availableCommands"
            >
              <option disabled value="">Выберите команду</option>
              <option 
                v-for="(cmd, cmdName) in controller.availableCommands" 
                :key="cmdName" 
                :value="cmdName"
              >
                {{ cmd.command_name }}
              </option>
            </select>
            <input
              type="text"
              class="text text-mid"
              :placeholder="'command ' + (index + 1)"
              v-model="controller.command"
              v-else
            />

            <!-- Опции -->
            <select
              class="select text-mid"
              v-model="controller.options"
              v-if="controller.currentCommand && controller.currentCommand.options && controller.currentCommand.options.length > 0"
            >
              <option disabled value="">Выберите опцию</option>
              <option 
                v-for="option in controller.currentCommand.options" 
                :key="option" 
                :value="option"
              >
                {{ option }}
              </option>
            </select>
            <input
              type="text"
              class="text text-mid"
              :placeholder="'options ' + (index + 1)"
              v-model="controller.options"
              v-else
            />

            <!-- Значение -->
            <select
              class="select text-mid"
              v-model="controller.value"
              v-if="controller.currentCommand && controller.currentCommand.values_range && controller.currentCommand.values_range.length > 0"
            >
              <option disabled value="">Выберите значение</option>
              <option 
                v-for="val in controller.currentCommand.values_range" 
                :key="val" 
                :value="val"
              >
                {{ val }}
              </option>
            </select>
            <input
              type="text"
              class="text text-mid"
              :placeholder="'value ' + (index + 1)"
              v-model="controller.value"
              v-else
            />

            <!-- Источник -->
            <select
              class="select text-mid"
              v-model="controller.source"
              v-if="controller.currentCommand && controller.currentCommand.sources && controller.currentCommand.sources.length > 0"
            >
              <option disabled value="">Выберите источник</option>
              <option 
                v-for="src in controller.currentCommand.sources" 
                :key="src" 
                :value="src"
              >
                {{ src }}
              </option>
            </select>
            <input
              type="text"
              class="text text-mid"
              :placeholder="'source ' + (index + 1)"
              v-model="controller.source"
              v-else
            />

            <button
              class='text'
              style="background-color: var(--header-bcg); color: var(--text1);"
              @click="setCommand(index)"
            >
              set-command {{ index + 1 }}
            </button>
            
            <a
              :href="'http://' + controller.ip"
              target="_blank"
              class='text'
              style="background-color: var(--header-bcg); color: var(--text1); text-align: center;"
              v-if="controller.ip"
            >
              go-to-web {{ index + 1 }}
            </a>
          </div>

          <div class="form-column info-screen width-100">
            <!-- Блок для Swarco -->
            <div v-if="controller.type_controller === 'Swarco'">
              <div class="info-line width-100">
                <span class="lcd-1">Текущий режим: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_mode || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">План: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_plan || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Фаза: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_stage || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Лампы (режим сигнализации): </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_status || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">FIXED TIME: </span>
                <span class="lcd-2">{{ controller.stateResponse?.fixed_time_status || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Источник плана: </span>
                <span class="lcd-2">{{ controller.stateResponse?.plan_source || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Детекторы: </span>
                <span class="lcd-2">{{ controller.stateResponse?.num_detectors || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Софт входы 180/181: </span>
                <span class="lcd-2">{{ controller.stateResponse?.status_soft_flag180_181 || "Нет данных" }}</span>
              </div>
            </div>

            <!-- Блок для Поток (P)-->
            <div v-else-if="controller.type_controller === 'Поток (P)'">
              <div class="info-line width-100">
                <span class="lcd-1">Режим: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_mode || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">План: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_plan || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Фаза: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_stage || "Нет данных" }}</span>
              </div>

              <br>

              <div class="info-line width-100">
                <span class="lcd-1">Ошибки детекторов: </span>
                <span class="lcd-2">{{ controller.stateResponse?.has_det_faults === '1' ? 'Есть' : 'Нет' }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Количество детекторов: </span>
                <span class="lcd-2">{{ controller.stateResponse?.num_detectors || "Нет данных" }}</span>
              </div>

              <br>

              <div class="info-line width-100">
                <span class="lcd-1">ВПУ: </span>
                <span class="lcd-2">{{ controller.stateResponse?.is_mode_man }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Flash: </span>
                <span class="lcd-2">{{ controller.stateResponse?.flash }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Dark: </span>
                <span class="lcd-2">{{ controller.stateResponse?.dark}}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Лампы (режим сигнализации): </span>
                <span class="lcd-2">{{ controller.stateResponse?.curr_status_mode || "Нет данных" }}</span>
              </div>

              <br>

              <div class="info-line width-100">
                <span class="lcd-1">Operation mode: </span>
                <span class="lcd-2">{{ controller.stateResponse?.operation_mode || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Local adaptive status: </span>
                <span class="lcd-2">{{ controller.stateResponse?.local_adaptive_status === '1' ? 'Активно' : 'Не активно' || "Нет данных" }}</span>
              </div>
            </div>

            <!-- Блок для Поток (S) -->
            <div v-else-if="controller.type_controller === 'Поток (S)'">
              <div class="info-line width-100">
                <span class="lcd-1">Режим: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_mode || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">План: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_plan || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Фаза: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_stage || "Нет данных" }}</span>
              </div>

              <br>

              <div class="info-line width-100">
                <span class="lcd-1">Лампы (режим сигнализации): </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_status || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Количество детекторов: </span>
                <span class="lcd-2">{{ controller.stateResponse?.num_detectors || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">curr_status_mode: </span>
                <span class="lcd-2">{{ controller.stateResponse?.curr_status_mode || "Нет данных" }}</span>
              </div>
            </div>

            <!-- Блок для Peek -->
            <div v-else-if="controller.type_controller === 'Peek'">
              <div v-if="controller.stateResponse?.streams_data?.length > 0">
                <div v-for="(stream, streamIndex) in controller.stateResponse.streams_data" :key="streamIndex" class="info-line width-100">
                  <div class="info-line width-100">
                    <div v-if="controller.stateResponse?.streams_data?.length > 1">
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

              <div class="info-line width-100">
                <span class="lcd-1">План: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_plan || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Время: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_time || "Нет данных" }}</span>
              </div>

              <div class="info-line width-100">
                <span class="lcd-1">Ошибки: </span>
                <span class="lcd-2">{{ controller.stateResponse?.current_alarms || "Нет данных" }}</span>
              </div>
            </div>

            <div v-else>
              <div class="info-line width-100"><span class="lcd-1">Ожидание ввода данных</span></div>
              <div class="info-line width-100"><pre> </pre></div>
              <div class="info-line width-100"><pre> </pre></div>
              <div class="info-line width-100"><pre> </pre></div>
              <div class="info-line width-100"><pre> </pre></div>
            </div>
          </div>
        </div>

        <div class="description" v-if="controller.address !== ''">
          <span><strong>Адрес: </strong></span>
          <span>{{ controller.address || "" }}</span>
        </div>

        <div class="description" v-if="controller.description !== ''">
          <span><strong>Описание: </strong></span>
          <span>{{ controller.description || "" }}</span>
        </div>
      </div>
    </div>

    <div class="container tools-right">
      <p>Временный блок разработчика</p>

      <div class="response-block" v-if="activeController.setCommandRequest">
        <h3>Запрос на сервер (контроллер {{ activeControllerIndex + 1 }}):</h3>
        <pre>{{ activeController.setCommandRequest }}</pre>
      </div>

      <div class="response-block" v-if="activeController.commandResponse">
        <h3>Ответ от сервера (контроллер {{ activeControllerIndex + 1 }}):</h3>
        <pre>{{ activeController.commandResponse }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "TrafficPro",
  data() {
    return {
      showSelect: false,
      IP: serverIPs[0],
      cloneCount: 1,
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      controllers: [this.createNewController()],
      timeoutIds: {},
      activeControllerIndex: 0,
      presets: [],
      selectedPresetId: '',
      presetName: '',
    };
  },
  computed: {
    activeController() {
      return this.controllers[this.activeControllerIndex] || this.controllers[0];
    }
  },
  watch: {
    cloneCount(newVal, oldVal) {
      if (newVal > oldVal) {
        for (let i = oldVal; i < newVal; i++) {
          this.controllers.push(this.createNewController());
        }
      } else {
        this.controllers = this.controllers.slice(0, newVal);
      }
    }
  },
  mounted() {
    this.fetchPresets();
  },
  methods: {
    createNewController() {
      return {
        searchValue: "",
        ip: "",
        type_controller: "",
        address: "",
        description: "",
        stateResponse: null,
        intervalId: null,
        command: "",
        options: "",
        value: "",
        source: "",
        commandResponse: null,
        setCommandRequest: null,
        statusMessage: "Ожидание данных...",
        lastUpdateTime: "Нет данных",
        availableCommands: null,
        currentCommand: null
      };
    },
    
    async fetchCommandsAndOptions(index) {
      const controller = this.controllers[index];
      if (!controller.type_controller) return;
      
      try {
        const url = '/api/v1/traffic-lights/commands-and-options';
        const response = await axios.get(url);
        
        if (response.data && response.data[controller.type_controller]) {
          controller.availableCommands = response.data[controller.type_controller].services_entity;
          // Сбрасываем текущую команду при смене типа контроллера
          controller.command = "";
          controller.options = "";
          controller.value = "";
          controller.source = "";
          controller.currentCommand = null;
        }
      } catch (error) {
        console.error(`Ошибка при получении команд для контроллера ${index + 1}:`, error);
        controller.availableCommands = null;
        controller.currentCommand = null;
      }
    },
    
    updateCommandFields(index, commandName = null) {
      const controller = this.controllers[index];
      if (!commandName) commandName = controller.command;
      
      if (controller.availableCommands && controller.availableCommands[commandName]) {
        controller.currentCommand = controller.availableCommands[commandName];
        
        // Сбрасываем предыдущие значения
        controller.options = "";
        controller.value = "";
        controller.source = "";
        
        // Устанавливаем значения по умолчанию
        if (controller.currentCommand.default_source) {
          controller.source = controller.currentCommand.default_source;
        }
        
        // Если есть только одно значение в диапазоне, устанавливаем его
        if (controller.currentCommand.values_range && controller.currentCommand.values_range.length === 1) {
          controller.value = controller.currentCommand.values_range[0];
        }
        
        // Если есть только одна опция, устанавливаем ее
        if (controller.currentCommand.options && controller.currentCommand.options.length === 1) {
          controller.options = controller.currentCommand.options[0];
        }
      } else {
        controller.currentCommand = null;
      }
    },

    fetchPresets() {
      const baseURL = this.IP.startsWith('http') ? this.IP : `http://${this.IP}`;
      fetch(`${baseURL}/api/presets/`)
        .then(res => res.json())
        .then(data => {
          this.presets = data;
        })
        .catch(err => {
          console.error("Ошибка при получении пресетов:", err);
        });
    },

    loadPreset() {
      if (!this.selectedPresetId) return;
      const baseURL = this.IP.startsWith('http') ? this.IP : `http://${this.IP}`;
      fetch(`${baseURL}/api/presets/${this.selectedPresetId}/`)
        .then(res => res.json())
        .then(data => {
          this.controllers = data.controllers_data;
          this.presetName = data.name;
          // Загружаем команды для каждого контроллера после загрузки пресета
          this.controllers.forEach((controller, index) => {
            if (controller.type_controller) {
              this.fetchCommandsAndOptions(index);
            }
          });
        });
    },

    savePreset() {
      if (!this.presetName) {
        alert("Введите название пресета");
        return;
      }

      const payload = {
        name: this.presetName,
        controllers_data: this.controllers,
      };

      const baseURL = this.IP.startsWith('http') ? this.IP : `http://${this.IP}`;

      axios.post(`${baseURL}/api/presets/`, payload, {
        headers: { 'Content-Type': 'application/json' },
      })
        .then(() => {
          alert("Пресет сохранён");
          this.fetchPresets();
        })
        .catch((error) => {
          console.error("Ошибка при сохранении пресета:", error);
        });
    },

    handleInput(index) {
      this.clearFields(index);

      if (this.timeoutIds[index]) {
        clearTimeout(this.timeoutIds[index]);
      }

      this.timeoutIds[index] = setTimeout(() => {
        this.searchHost(index);
      }, 1500);
    },

    clearFields(index) {
      const controller = this.controllers[index];
      controller.ip = "";
      controller.type_controller = "";
      controller.address = "";
      controller.description = "";
      controller.stateResponse = null;
      controller.availableCommands = null;
      controller.currentCommand = null;
    },

    async searchHost(index) {
      const controller = this.controllers[index];
      const searchValue = controller.searchValue.trim();
      if (!searchValue) return;

      try {
        const url = '/api/v1/traffic-lights/properties';
        const requestData = {
          hosts: [searchValue],
        };

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        controller.ip = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.ip_adress || "";
        controller.type_controller = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.type_controller || "";
        controller.address = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.address || "";
        controller.description = response.data.results?.[0]?.[searchValue]?.db_records?.[0]?.description || "";

        // Загружаем команды после установки типа контроллера
        if (controller.type_controller) {
          this.fetchCommandsAndOptions(index);
        }

        this.startPolling(index);
      } catch (error) {
        console.error(`Ошибка при поиске контроллера ${index + 1}:`, error);
      }
    },

    async setCommand(index) {
      this.activeControllerIndex = index;
      const controller = this.controllers[index];

      if (!controller.ip || !controller.type_controller) {
        console.error(`IP и тип контроллера ${index + 1} обязательны для выполнения команды.`);
        return;
      }

      const requestData = {
        hosts: {
          [controller.ip]: {
            type_controller: controller.type_controller,
          },
        },
      };

      if (controller.command) requestData.hosts[controller.ip].command = controller.command;
      if (controller.options) requestData.hosts[controller.ip].options = controller.options;
      if (controller.value) requestData.hosts[controller.ip].value = Number(controller.value);
      if (controller.source) requestData.hosts[controller.ip].source = controller.source;

      controller.setCommandRequest = requestData;

      try {
        const url = '/api/v1/traffic-lights/set-command';
        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        controller.commandResponse = response.data;
        console.log(`Команда ${index + 1} успешно отправлена:`, response.data);
      } catch (error) {
        console.error(`Ошибка при отправке команды ${index + 1}:`, error);
        controller.commandResponse = error.response?.data || { error: "Ошибка сети или сервера" };
      }
    },

    async fetchStateTest(index) {
      const controller = this.controllers[index];
      if (!controller.ip || !controller.type_controller) {
        controller.stateResponse = null;
        controller.statusMessage = "IP и тип контроллера не указаны";
        return;
      }

      try {
        const url = '/api/v1/traffic-lights/get-state';
        const requestData = {
          hosts: {
            [controller.ip]: {
              type_controller: controller.type_controller,
            },
          },
        };

        const response = await axios.post(url, requestData, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        controller.stateResponse = response.data[controller.ip].response.data;
        controller.statusMessage = "Данные успешно получены";
        controller.lastUpdateTime = new Date().toLocaleTimeString();
      } catch (error) {
        console.error(`Ошибка при запросе данных контроллера ${index + 1}:`, error);
        controller.statusMessage = "Ошибка при получении данных";
        controller.stateResponse = null;
      }
    },

    startPolling(index) {
      this.stopPolling(index);
      this.fetchStateTest(index); // Сразу делаем первый запрос
      this.controllers[index].intervalId = setInterval(() => {
        this.fetchStateTest(index);
      }, 2000);
    },

    stopPolling(index) {
      if (this.controllers[index].intervalId) {
        clearInterval(this.controllers[index].intervalId);
        this.controllers[index].intervalId = null;
      }
    },
  },
  beforeUnmount() {
    this.controllers.forEach((_, index) => {
      this.stopPolling(index);
    });
  },
};
</script>
<style scoped>
.controller-group {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: var(--text-bcg-7);
}

.controller-group h3 {
  margin-top: 0;
  color: #333;
}

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
  margin-top: 20px;
}

.response-block {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.width-100 {
  width: 100%;
}

.preset {
  border: 1px solid var(--border);    
  font-size: 14px;
  padding: 3px 14px 2px 5px;
  border-radius: 6px;
  font-family: monospace;
  resize: vertical;
  height: auto;
  margin: 5px 5px 15px 5px;
}

.preset_ {
  font-size: 17px;
  color: var(--text6);
  width: 100%;
}

</style>