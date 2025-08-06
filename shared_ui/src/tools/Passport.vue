<template>
  <div class="tools" style="width: 1400px;">
    <div class="container tools-left">
      <h2 class="title">Работа с паспортом</h2>
      <div id="main_div">
        <select id="choose_option" class="select mr" v-model="selectedOption">
          <option value="-">-</option>
          <option value="compare_groups">Сравнить направления</option>
          <option value="calc_groups_in_stages">Рассчитать направления в фазах</option>
        </select>
        <button id="calculate" @click="sendData">{{ buttonText }}</button>

        <table id="table_compare_groups" v-show="showCompareTables">
          <thead>
            <tr>
              <th scope="col" class="centr-align">Таблица направлений</th>
              <th scope="col" class="centr-align">Таблица фаз(Временная программа)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <textarea 
                  class="minitext"
                  id="table_groups" 
                  v-model="tableGroupsContent"
                  :disabled="selectedOption === 'calc_groups_in_stages'"
                  :placeholder="placeholderTableGroups"
                ></textarea>
              </td>
              <td>
                <textarea  начала
                  class="minitext"
                  id="table_stages" 
                  v-model="tableStagesContent"
                  :placeholder="placeholderTableStages"
                ></textarea>
              </td>
            </tr>
          </tbody>
        </table>
        <br><br>
        <table class="result_table" id="table_result_calc_groups_in_stages" v-show="selectedOption === 'calc_groups_in_stages'">
          <caption>Результат расчёта привязки направлений к фазам:</caption>
          <tbody>
            <tr>
              <td>
                <textarea 
                  readonly 
                  class="minitext"
                  id="textarea_result_calc_groups_in_stages"
                  v-model="calcGroupsResult"
                  :placeholder="placeholderGroupsInStagesResult"
                ></textarea>
              </td>
            </tr>
          </tbody>
        </table>
        <table class="result_table" id="table_result_compare_groups" v-show="selectedOption === 'compare_groups'">
          <caption class="mb10">Результат сравнения групп:</caption>
          <thead>
            <tr>
              <th scope="col" class="centr-align"> Номер направления </th>
              <th scope="col" class="centr-align"> Тип направления </th>
              <th scope="col" class="centr-align"> Фазы в которых участвует направление </th>
              <th scope="col" class="centr-align"> Ошибки </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(group, index) in compareGroupsResult" :key="index">
              <td>{{ group.num_group }}</td>
              <td>{{ group.type_group }}</td>
              <td>{{ group.stages }}</td>
              <td :class="{ 'errors_content': group.errors.length > 0 }" 
                  :bgcolor="group.errors.length > 0 ? 'red' : ''">
                <span v-for="(error, errorIndex) in group.errors" :key="errorIndex">
                  {{ errorIndex + 1 }}. {{ error }}<br>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "Passport",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath: "/api/v1/compare-groups/",
      
      // Options
      selectedOption: "-",
      
      // Placeholders
      placeholderTableGroups: `Номер направления / название / участие в фазах
1	Транспортное	1,2,6
2	Транспортное	1,2,3,6
3	Общ. трансп.	1,2,3,6
4	Транспортное	1,2,3,4,6
5	Поворотное	1,2
6	Пешеходное	1,2,3,6
7	Транспортное	4,5
8	Пешеходное	4,5
9	Пешеходное	4,5
10	Пешеходное	3,6
11	Пешеходное	5
12	Транспортное	Пост. красное`,
      
      placeholderTableStages: `Номер фазы / направления в этой фазе
1	1,2,3,4,5,6
2	1,2,3,4,5,6
3	2,3,4,6,10
4	4,7,8,9
5	7,8,9,11
6	1,2,3,4,6,10`,
      
      placeholderGroupsInStagesResult: `В данном поле будет выведен результат расчёта привязки направлений к фазам, для "Таблицы направлений"`,
      
      // Form data
      tableGroupsContent: "",
      tableStagesContent: "",
      
      // Results
      calcGroupsResult: "",
      compareGroupsResult: [],
      
      // Error handling
      responseIsError: false,
      responseMessage: ""
    };
  },
  computed: {
    showCompareTables() {
      return this.selectedOption !== "-";
    },
    buttonText() {
      return this.selectedOption === "compare_groups" 
        ? "Сравнить" 
        : this.selectedOption === "calc_groups_in_stages" 
          ? "Рассчитать" 
          : "Выполнить";
    }
  },
  methods: {
    async sendData() {
      if (this.selectedOption === "-") {
        alert("Для отправки запроса выберите опцию");
        return;
      }
      
      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath}`;
        
        try {
          const response = await axios.post(server, {          
            options: [this.selectedOption],
            content_table_groups: this.tableGroupsContent,
            content_table_stages: this.tableStagesContent
          }, {
            headers: {
              "Authorization": `Token ${this.token}`
            }
          });

          this.processResponse(response.data);
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
    
    processResponse(responseData) {
      if (this.selectedOption === 'compare_groups') {
        this.displayResultCompareGroups(responseData);
      } else if (this.selectedOption === 'calc_groups_in_stages') {
        this.displayResultCalcGroupsInStages(responseData);
      }
    },
    
    displayResultCompareGroups(responseData) {
      const groups_info = responseData.compare_groups.groups_info;
      const userDataIsValid = responseData.compare_groups.error_in_user_data;
      
      if (typeof userDataIsValid === 'string') {
        alert('Проверьте корректность данных:\n' + userDataIsValid);
        return false;
      }

      this.compareGroupsResult = [];
      for (const group in groups_info) {
        this.compareGroupsResult.push({
          num_group: group,
          type_group: groups_info[group].type_group,
          stages: groups_info[group].stages,
          errors: groups_info[group].errors || []
        });
      }
    },
    
    displayResultCalcGroupsInStages(responseData) {
      const userDataIsValid = responseData.make_groups_in_stages.error_in_user_data;
      if (typeof userDataIsValid === 'string') {
        alert('Проверьте корректность данных:\n' + userDataIsValid);
        return false;
      }

      const result = responseData.make_groups_in_stages.calculate_result;
      this.calcGroupsResult = '';
      
      for(const key in result) {
        this.calcGroupsResult += `${key}\tНаправление\t${result[key].join(',')}\n`;
      }
    }
  }
};
</script>

<style scoped>

textarea {
  width: 100%;
  min-height: 240px;
  padding: 10px;
  box-sizing: border-box;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

th, td {
  border: 1px solid var(--border);
  padding: 8px;
  text-align: left;
}

th {
  background-color: var(--text-bcg-4);
}

.errors_content {
  color: var(--div);
}

.result_table {
  margin-top: 20px;
}

.input-group {
  display: flex;
  align-items: center; 
  gap: 10px; 
}

.select, #calculate {
  font-family: inherit;
  font-size: inherit;

}

#choose_option {
  width: 420px;
  padding: 6px 12px;
}

</style>