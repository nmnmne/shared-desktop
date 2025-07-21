<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Расчет конфликтов направлений</h2>
      
      <!-- Инструкция -->
      <div class="alert alert-light">
          <li>Введите направления для каждой фазы в отдельной строке.</li>
          <li>Отметьте опции для создания файлов конфигурации и конфликтов по необходимости.</li>
      </div>

      <!-- Тип контроллера -->
      <div class="calc_conflicts right-align gap mb10" id="controllers">
        <input class="radio" type="radio" value="common" v-model="controllerType" id="common">
        <label for="common">Общий</label>
        <input class="radio" type="radio" value="swarco" v-model="controllerType" id="swarco">
        <label for="swarco">Swarco</label>
        <input class="radio" type="radio" value="peek" v-model="controllerType" id="peek">
        <label for="peek">Peek</label>
      </div>

      <!-- Опции -->
      <fieldset>
        <legend>Опции</legend>
        <div>
          <input type="checkbox" v-model="createTxt" id="create_txt">
          <label class="calc_conflicts_optinos" for="create_txt">Создать txt файл с конфликтами:</label>
        </div>
        <div>
          <input type="checkbox" v-model="binvalSwarco" id="binval_swarco" :disabled="controllerType !== 'swarco'">
          <label class="calc_conflicts_optinos" for="binval_swarco">Матрица конфликтов и бинарные значения фаз для swarco</label>
        </div>
        <div>
          <input type="checkbox" v-model="makeConfig" id="make_config" :disabled="controllerType === 'common'">
          <label class="calc_conflicts_optinos" for="make_config">Создать файл конфигурации:</label>
          <input type="file" id="config_file" ref="configFile" multiple :disabled="!makeConfig || controllerType === 'common'" @change="handleFileChange">
        </div>
      </fieldset>
      <br>

      <!-- Контейнеры ввода данных -->
      <div class="input-container form-inline gap40">
        <div class="input-section right-align">
          <textarea v-model="stagesInput" @input="parseUserData" class="minitextarea"></textarea>
        </div>
        
        <div class="output-section">
          <div class="output-content" style="white-space: pre-line">{{ prettyOutputStages }}</div>
        </div>
        
      </div>

      <div class="right-align mt10">
        <button :disabled="!allowSend" @click="sendData" id="send_conflicts_data" type="button" :title="sendButtonTitle">Отправить</button>
      </div>
    </div>
    <div class="tools-right">
            <!-- Результаты расчета -->
      <div id="calculated_content" v-if="responseData">
        
        <!-- Ссылки для скачивания -->
        <div v-if="responseData.txt_file || responseData.config_file">
          <a v-if="responseData.txt_file" :href="responseData.txt_file.url_to_file" download>Скачать текстовый файл с расчётами</a>
          <br v-if="responseData.txt_file && responseData.config_file">
          <a v-if="responseData.config_file" :href="responseData.config_file.url_to_file" download>Скачать созданный конфигурауционный файл с расчитанными данными</a>
          <br><br>
        </div>
        
        <!-- Матрица конфликтов -->
        <table id="output_matrix">
          <caption>Матрица конфликтов:</caption>
          <tr v-for="(row, rowIndex) in responseData.base_matrix" :key="'row-'+rowIndex">
            <th v-if="rowIndex === 0" v-for="(cell, cellIndex) in row" :key="'header-'+cellIndex">{{ formatMatrixCell(cell) }}</th>
            <template v-else>
              <th>{{ row[0] }}</th>
              <td v-for="(cell, cellIndex) in row.slice(1)" :key="'cell-'+cellIndex" :style="{ backgroundColor: getCellColor(cell) }">
                {{ formatMatrixCell(cell) }}
              </td>
            </template>
          </tr>
        </table>
        
        <!-- Дополнительные данные для Swarco -->
        <div v-if="binvalSwarco && controllerType === 'swarco'">
          <br>
          <div>
            <b>Матрица конфликтов для F997 конфига Swarco:</b>
            <br v-for="(row, index) in responseData.matrix_F997" :key="'f997-'+index">
            {{ row.join("") }}
          </div>
          <br>
          <div>
            <b>Матрица конфликтных направления для F992 конфига Swarco:</b>
            <br v-for="(row, index) in responseData.numbers_conflicts_groups" :key="'f992-'+index">
            {{ row }}
          </div>
          <br>
          <div>
            <b>Бинарные значения фаз для F009 конфига Swarco:</b>
            <br>
            {{ responseData.stages_bin_vals_f009 }}
          </div>
        </div>
      </div>
      <div class="error-section" v-if="errorMessages">
        <h3>Ошибки ввода</h3>
        <br>
        <div class="error-content">{{ errorMessages }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "CalcConflicts",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath1: "/api/v1/conflicts/",
      
      // Данные формы
      controllerType: this.getControllerTypeFromUrl(),
      createTxt: false,
      binvalSwarco: false,
      makeConfig: false,
      configFile: null,
      stagesInput: '',
      
      // Ошибки и вывод
      errorMessages: '',
      prettyOutputStages: '',
      allowSend: false,
      sendButtonTitle: 'Введите фазы-направления',
      
      // Ответ сервера
      responseData: null,
      responseIsError: false,
      responseMessage: '',
      
      // Константы
      maxGroups: 48,
      separatorGroups: ',',
      separatorStages: '\n'
    };
  },
  methods: {
    getControllerTypeFromUrl() {
      const path = window.location.pathname;
      if (path.includes('/tools_peek/')) return 'peek';
      if (path.includes('/tools_swarco/')) return 'swarco';
      return 'common';
    },
    async sendData() {
      const formData = new FormData();
      
      if (this.configFile) {
        formData.append('file', this.configFile);
      }
      
      const userDataOptionsForCalculate = {
        stages: this.stagesInput,
        type_controller: this.controllerType,
        create_config: !!this.configFile,
        create_txt: this.createTxt,
        swarco_vals: this.binvalSwarco,
      };
      
      formData.append('data', JSON.stringify(userDataOptionsForCalculate));
      
      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath1}`;
        
        try {
          const response = await axios.post(server, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
              "Authorization": `Bearer ${this.token}`,
            }
          });
          
          this.responseData = response.data;
          this.responseIsError = false;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
          if (error.response) {
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
          }
        }
      }
      
      // Если ни один сервер не ответил
      this.responseMessage = "Ошибка при отправке данных ко всем серверам.";
      this.responseIsError = true;
    },
    
    handleFileChange(event) {
      this.configFile = event.target.files[0];
    },
    
    parseUserData() {
      const eMustMoreOneStage = 'Должно быть более 1 фазы';
      const mustBeNum = 'Группа должна быть целым числом или числом, представленным в виде десятичного числа. Пример: 1, 2, 10, 14, 8.1, 8.2';
      const mustBeLt48 = 'Максимальный номер группы не должен превышать 48';
      const mustBeOneComma = 'Должна быть одна запятая';
      
      let errors = new Set();
      const splitedStages = this.stagesInput.split(this.separatorStages);
      const numStages = splitedStages.length;
      
      if (numStages < 2) {
        errors.add(eMustMoreOneStage);
      }
      
      splitedStages.forEach((lineGroups, ind) => {
        const numCurrentStage = ind + 1;
        
        if (/,{2,}/.test(lineGroups)) {
          errors.add(`Строка ${numCurrentStage}(Фаза ${numCurrentStage}): ${mustBeOneComma}`);
          return;
        }
        
        lineGroups.split(this.separatorGroups).forEach((el) => {
          if (!el) return;
          
          const numGroupIsValid = this.checkValidNumGroup(el);
          if (!numGroupIsValid) {
            errors.add(`Строка ${numCurrentStage}(Фаза ${numCurrentStage}): ${mustBeNum}`);
          } else if (numGroupIsValid > this.maxGroups) {
            errors.add(`Строка ${numCurrentStage}(Фаза ${numCurrentStage}): ${mustBeLt48}`);
          }
        });
      });
      
      this.writeErrMsg(errors, splitedStages);
    },
    
    writeErrMsg(errors, splitedStages) {
      this.prettyOutputStages = '';
      this.errorMessages = '';
      let allowedSendRequestCalculate = false;
      
      if (errors.size) {
        this.errorMessages = Array.from(errors).join('\n');
      } else {
        this.prettyOutputStages = splitedStages.map((line, index) => 
          `Фаза ${index + 1}: ${line}`
        ).join('\n');
        allowedSendRequestCalculate = true;
      }
      
      this.allowSend = allowedSendRequestCalculate;
      this.sendButtonTitle = allowedSendRequestCalculate 
        ? 'Нажмите для отправки запроса' 
        : 'Устраните ошибки для отправки запроса';
    },
    
    checkValidNumGroup(group) {
      if (group.length < 4) {
        const isValidNumber = this.isInteger(group) || this.isFloat(group);
        if (isValidNumber && isValidNumber <= this.maxGroups) {
          return isValidNumber;
        }
      }
      return false;
    },
    
    isInteger(data) {
      const num = Number(data);
      return num && num % 1 === 0 ? num : false;
    },
    
    isFloat(data) {
      const num = Number(data);
      return num && num % 1 !== 0 ? num : false;
    },
    
    formatMatrixCell(cell) {
      const value = cell.replaceAll("|", "");
      if (value.includes('K')) return 'K';
      if (value.includes('O')) return 'O';
      if (Number.isInteger(+value)) return value;
      return '*';
    },
    
    getCellColor(cell) {
      const value = cell.replaceAll("|", "");
      if (value.includes('K')) return 'red';
      if (value.includes('O')) return 'green';
      return '';
    }
  }
};
</script>

<style scoped>

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #f9f9f9;
}

#stages_from_area {
  width: 100%;
  min-height: 150px;
}

#user_data {
  width: 100%;
  border-collapse: collapse;
}

#user_data th, #user_data td {
  border: 1px solid #ddd;
  padding: 8px;
  vertical-align: top;
}

#output_matrix {
  border-collapse: collapse;
  margin: 20px 0;
}

#output_matrix th, #output_matrix td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

fieldset {
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 4px;
}

legend {
  padding: 0 10px;
}
</style>