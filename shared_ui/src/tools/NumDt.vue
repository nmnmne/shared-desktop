<template>
  <div class="tools">
    <div class="container tools-left">
      <!-- выпадающий список -->
      <div class="form-inline">
        <h2 class="title" style="width: 435px;">Номера входов детекторов</h2>
        <select id="type" class="select" style="width: 150px;" v-model="selectedType">
          <option value="potok">Поток</option>
          <option value="swarco">Swarco</option>
        </select>
      </div>

      <div class="table-container">
        <!-- Таблица Поток -->
        <table v-if="selectedType === 'potok'" class="detectors-table">
          <thead>
            <tr>
              <th colspan="2" class="column-space">Плата 1</th>
              <th colspan="2" class="column-space">Плата 2</th>
              <th colspan="2" class="column-space">Плата 3</th>
              <th colspan="2" class="column-space">Плата 4</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in 32" :key="i">
              <td>1.{{ i }}</td>
              <td class="column-space">{{ i }}</td>
              <td>2.{{ i }}</td>
              <td class="column-space">{{ i + 32 }}</td>
              <td>3.{{ i }}</td>
              <td class="column-space">{{ i + 64 }}</td>
              <td>4.{{ i }}</td>
              <td class="column-space">{{ i + 96 }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Таблица Swarco -->
        <table v-else class="detectors-table">
          <thead>
            <tr>
              <th colspan="2">Плата 0</th>
              <th colspan="2">Плата 1</th>
              <th colspan="2">Плата 2</th>
              <th colspan="2">Плата 3</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in 16" :key="i">
              <td>0.{{ i }}</td>
              <td>{{ 100 + i }}</td>
              <td>1.{{ i }}</td>
              <td>{{ 116 + i }}</td>
              <td>2.{{ i }}</td>
              <td>{{ 132 + i }}</td>
              <td>3.{{ i }}</td>
              <td>{{ 148 + i }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NumDt',
  data() {
    return {
      selectedType: 'potok' // по умолчанию Поток
    }
  },
  created() {
    this.selectedType = this.getControllerTypeFromUrl()
  },
  watch: {
    selectedType(newVal) {
      // при смене типа меняем URL (без перезагрузки страницы)
      if (newVal === 'potok') {
        window.history.replaceState({}, '', '/tools_potok/')
      } else if (newVal === 'swarco') {
        window.history.replaceState({}, '', '/tools_swarco/')
      }
    }
  },
  methods: {
    getControllerTypeFromUrl() {
      const path = window.location.pathname
      if (path.includes('/tools_potok/')) return 'potok'
      if (path.includes('/tools_swarco/')) return 'swarco'
      return 'potok' // значение по умолчанию
    }
  }
}
</script>

<style scoped>
.table-container {
  overflow-x: auto;
}

.detectors-table {
  border-collapse: collapse;
  font-size: 14px;
}

.detectors-table th,
.detectors-table td {
  padding: 1px 25px;
  text-align: center;
  border: 1px solid var(--text-bcg-6);
}

.detectors-table th {
  background-color: var(--header-bcg);
  color: var(--text7);
  font-weight: 600;
}

.detectors-table tr:nth-child(even) {
  background-color: var(--text-bcg-2);
}

.detectors-table td:hover,
.detectors-table th:hover {
  background-color: var(--text-bcg-6);
  font-weight: bold;
}

</style>
