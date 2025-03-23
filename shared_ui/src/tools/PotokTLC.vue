<template>
  <div class="container tools-left">
    <h2 class="title">Работа с Traffic Light Configurator</h2>
      <div class="form-inline">
        <input
          v-model="condition"
          class="text"
          type="text"
          maxlength="2000"
          placeholder="Условие продления/перехода"
          autocomplete="off"
        />
        <button @click="createFunctions">
          Создать
        </button>
      </div>
      <div v-if="functions.length > 0" class="functions-container">
        <div v-for="func in functions" :key="func" class="function-item">
          <input type="checkbox" :id="func" />
          <label :for="func">{{ func }}</label>
        </div>
      </div>
      <div class="form-inline">
      <button v-if="functions.length > 0" @click="getConditionResult">
        Тестировать сочетание
      </button>
      <label :class="{'green-text': conditionResult === 'TRUE', 'red-text': conditionResult === 'FALSE'}" class="result-label">
        {{ conditionResult }}
      </label>
      </div>

  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "PotokTLC",
  data() {
    return {
      condition: "",
      functions: [],
      conditionResult: "",
      token: import.meta.env.VITE_API_TOKEN,
      apiPath: "/api/v1/potok-tlc/",
      serverIPs: serverIPs,
    };
  },
  methods: {
    async createFunctions() {
      for (let ip of this.serverIPs) {
        const server = `http://${ip}${this.apiPath}`;

        try {
          const response = await axios.post(
            server,
            {
              options: {
                get_functions_from_condition_string: true,
                get_condition_result: false,
              },
              condition: this.condition,
              payload: {},
            },
            {
              headers: {
                "X-CSRFToken": this.getCookie("csrftoken"),
                Authorization: `Token ${this.token}`,
              },
            }
          );

          this.functions = response.data.functions;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }

      console.error("Ошибка при подключении ко всем серверам.");
    },

    async getConditionResult() {
      for (let ip of this.serverIPs) {
        const server = `http://${ip}${this.apiPath}`;

        try {
          const funcValues = this.collectDataGetResultCondition();
          const response = await axios.post(
            server,
            {
              options: {
                get_functions_from_condition_string: false,
                get_condition_result: true,
              },
              condition: this.condition,
              payload: {
                get_condition_result: funcValues,
              },
            },
            {
              headers: {
                "X-CSRFToken": this.getCookie("csrftoken"),
                Authorization: `Token ${this.token}`,
              },
            }
          );

          this.conditionResult = `${response.data.result
            .toString()
            .toUpperCase()}`;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }

      console.error("Ошибка при подключении ко всем серверам.");
    },

    collectDataGetResultCondition() {
      const funcValues = {};
      const checkboxes = this.$el.querySelectorAll(
        ".functions-container input[type='checkbox']"
      );
      checkboxes.forEach((checkbox) => {
        funcValues[checkbox.id] = Number(checkbox.checked);
      });
      return { func_values: funcValues };
    },

    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === name + "=") {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },
  },
};
</script>

<style scoped>

.functions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 20px 0px 20px;
}

.result-label {
  margin: 0 10px;
  font-size: 27px;
}

.green-text {
  color: green;
}

.red-text {
  color: red;
}
</style>