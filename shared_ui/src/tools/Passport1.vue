<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Основные параметры паспорта</h2>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th rowspan="2" class="col-number">№ нап.</th>
              <th rowspan="2" class="col-type">Тип направления</th>
              <th rowspan="2" class="col-phases">Фазы, в кот. участ. направл.</th>
              <th rowspan="2" class="col-lights">Светофоры</th>
              <th colspan="4" class="col-prohibition">Запрет</th>
              <th colspan="3" class="col-permission">Разрешение</th>
              <th rowspan="2" class="col-constant">Пост. красн.</th>
              <th colspan="2" class="col-toov">ТООВ</th>
              <th rowspan="2" class="col-notes">Примечания</th>
            </tr>
            <tr>
              <th class="col-small">Тзд</th>
              <th class="col-small">Тзм</th>
              <th class="col-small">Тж</th>
              <th class="col-small">Тк</th>
              <th class="col-small">Ткж</th>
              <th class="col-small">Тз</th>
              <th class="col-small">Тзз</th>
              <th class="col-small">Красн.</th>
              <th class="col-small">Зелен.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td class="center-content">{{ row.directionNumber }}</td>
              <td>
                <select v-model="row.directionType" @change="updateInterstageValues(index)" class="table-input">
                  <option value=""></option>
                  <option value="Транспортное">Транспортное</option>
                  <option value="Поворотное">Поворотное</option>
                  <option value="Пешеходное">Пешеходное</option>
                  <option value="Общ. трансп.">Общ. трансп.</option>
                  <option value="Велосипедное">Велосипедное</option>
                </select>
              </td>
              <td class="center-content">
                <input type="text" v-model="row.participatingPhases" class="table-input read-only" readonly>
              </td>
              <td class="center-content"><input type="text" v-model="row.trafficLights" class="table-input"></td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.prohibition.Tzd" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.prohibition.Tzm" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.prohibition.Tzh" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.prohibition.Tk" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.permission.Tkzh" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.permission.Tz" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <select v-model="row.interstageIntervals.permission.Tzz" class="table-input">
                  <option v-for="n in 16" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
              </td>
              <td class="center-content">
                <input 
                  type="checkbox" 
                  v-model="row.constantRed" 
                  class="table-checkbox"
                  :disabled="!isTransport(row.directionType)"
                >
              </td>
              <td class="center-content">
                <input 
                  type="checkbox" 
                  v-model="row.TOOV.red" 
                  class="table-checkbox"
                  :disabled="!isTransportOrPedestrian(row.directionType)"
                >
              </td>
              <td class="center-content">
                <input 
                  type="checkbox" 
                  v-model="row.TOOV.green" 
                  class="table-checkbox"
                  :disabled="!isTransportOrPedestrian(row.directionType)"
                >
              </td>
              <td><input type="text" v-model="row.notes" class="table-input"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="container tools-right">
      <h2 class="title">Настройки</h2>
      
      <div class="user-info">
        <div class="user-name">Пользователь: {{ userName }}</div>
      </div>

      <div class="controls">
        <label for="directionCount">Количество направлений:</label>
        <select
          id="directionCount"
          class="minitext"
          v-model="directionCount"
          @change="updateTableData"
          style="width: 6ch;"
        >
          <option v-for="n in 90" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

    </div>

  </div>
</template>

<script>
export default {
  name: "Passport1",
  data() {
    return {
      directionCount: 1,
      tableData: [this.createEmptyRow(1)],
      userName: "неавторизован", // Получаем из AuthModal
      // Шаблоны значений для каждого типа направления
      directionTemplates: {
        "Транспортное": {
          prohibition: { Tzd: 0, Tzm: 3, Tzh: 3, Tk: 0 },
          permission: { Tkzh: 1, Tz: 0, Tzz: 0 }
        },
        "Поворотное": {
          prohibition: { Tzd: 0, Tzm: 3, Tzh: 0, Tk: 3 },
          permission: { Tkzh: 0, Tz: 0, Tzz: 0 }
        },
        "Пешеходное": {
          prohibition: { Tzd: 0, Tzm: 3, Tzh: 0, Tk: 3 },
          permission: { Tkzh: 0, Tz: 0, Tzz: 0 }
        },
        "Общ. трансп.": {
          prohibition: { Tzd: 0, Tzm: 3, Tzh: 0, Tk: 3 },
          permission: { Tkzh: 0, Tz: 0, Tzz: 0 }
        },
        "Велосипедное": {
          prohibition: { Tzd: 0, Tzm: 3, Tzh: 3, Tk: 0 },
          permission: { Tkzh: 1, Tz: 0, Tzz: 0 }
        }
      }
    };
  },
  mounted() {
    // Слушаем события изменения статуса авторизации
    window.addEventListener('auth-status-changed', this.handleAuthStatusChanged);
    
    // Запрашиваем текущий статус авторизации
    window.dispatchEvent(new CustomEvent('check-auth'));
  },
  beforeUnmount() {
    window.removeEventListener('auth-status-changed', this.handleAuthStatusChanged);
  },
  methods: {
    createEmptyRow(number) {
      return {
        directionNumber: number,
        directionType: "",
        participatingPhases: "",
        trafficLights: "",
        interstageIntervals: {
          prohibition: { Tzd: 0, Tzm: 0, Tzh: 0, Tk: 0 },
          permission: { Tkzh: 0, Tz: 0, Tzz: 0 }
        },
        constantRed: false,
        TOOV: { red: false, green: false },
        notes: ""
      };
    },
    
    updateTableData() {
      const currentLength = this.tableData.length;
      const newLength = this.directionCount;
      
      if (newLength > currentLength) {
        for (let i = currentLength; i < newLength; i++) {
          this.tableData.push(this.createEmptyRow(i + 1));
        }
      } else if (newLength < currentLength) {
        this.tableData.splice(newLength);
      }
      
      this.tableData.forEach((row, index) => {
        row.directionNumber = index + 1;
      });
    },
    
    updateInterstageValues(index) {
      const selectedType = this.tableData[index].directionType;
      const template = this.directionTemplates[selectedType];
      
      if (template) {
        this.tableData[index].interstageIntervals = JSON.parse(JSON.stringify(template));
      }
      
      if (!this.isTransport(selectedType)) {
        this.tableData[index].constantRed = false;
      }
      
      if (!this.isTransportOrPedestrian(selectedType)) {
        this.tableData[index].TOOV.red = false;
        this.tableData[index].TOOV.green = false;
      }
    },
    
    isTransport(directionType) {
      return directionType === "Транспортное";
    },
    
    isTransportOrPedestrian(directionType) {
      return directionType === "Транспортное" || directionType === "Пешеходное";
    },
    
    handleAuthStatusChanged(event) {
      this.userName = event.detail.userName;
    }
  }
};
</script>

<style scoped>
/* Все стили остаются без изменений */
.tools-left {
  width: 1200px;
}
.tools-right {
  width: 420px;
}
.controls {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.controls label {
  font-weight: 600;
  color: var(--text2);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  border: 1px solid var(--body-bcg);
  padding: 1px;
  text-align: center;
  border-radius: 7px;
}

.data-table th {
  background-color: var(--tb-1);
  color: var(--text7);
  font-weight: 600;
}

.table-input {
  width: 100%;
  padding: 5px;
  border: 0px solid var(--text-bcg-6);
  border-radius: 3px;
  box-sizing: border-box;
  background: var(--tb-2);
  color: var(--text2);
  font-size: 18px;
  text-align: center;
}

.table-input.read-only {
  background: var(--tb-2);
  color: var(--text2);
  opacity: 0.2;
  cursor: not-allowed;
  font-size: 18px;
}

.table-checkbox {
  transform: scale(1.2);
}

.table-checkbox:disabled {
  opacity: 0.1;
  cursor: not-allowed;
}

.table-checkbox:disabled:checked {
  background-color: var(--text-bcg-6);
}

.data-table tr:hover {
  background-color: var(--text-bcg-5);
}

.table-input[type="number"]::-webkit-outer-spin-button,
.table-input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

.col-number { width: 35px; }
.col-type { width: 110px; }
.col-phases { width: 110px; }
.col-lights { width: 110px; }
.col-prohibition { width: 10px; }
.col-permission { width: 10px; }
.col-constant { width: 45px; }
.col-toov { width: 100px; }
.col-notes { width: 200px; }
.col-small { width: 35px; }

.table-checkbox {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background-color: var(--text-bcg-6);
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.table-checkbox:checked {
  background-color: var(--tb-3);
  border-color: var(--button-1-bgc);
}

.table-checkbox:checked::after {
  content: "✓";
  position: absolute;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--text1);
  font-size: 18px;
  font-weight: bold;
}

.table-input {
  background: var(--tb-2) !important;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.table-input::-moz-focus-inner {
  border: 0;
}

.center-content {
  text-align: center;
  vertical-align: middle;
  font-size: 16px;
}

.center-content .table-input {
  text-align: center;
}

.center-content input,
.center-content select {
  text-align: center;
}

.user-name {
  font-weight: 600;
}

.user-info {
  margin: 10px 0px;
}
</style>