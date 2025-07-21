<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Калькулятор фиксированного времени цикла</h2>

      <div class="mb10">
        <label for="phaseCount" class="form-label mr">Количество фаз:</label>
        <select 
          id="phaseCount" 
          class="minitext" 
          v-model.number="phaseCount"
          style="width: 6ch;"
        >
          <option 
            v-for="n in 14" 
            :key="n" 
            :value="n"
          >
            {{ n }}
          </option>
        </select>
      </div>
      <div class="mb10">
        <div v-for="(phase, index) in phases" :key="index" class="form-inline mb4">
          <div class="col-md-4">
            <input
              type="number"
              class="text"
              v-model.number="phase.time"
              :placeholder="`Время фазы`"
              style="width: 14ch;"
              @input="calculateShifts"
              min="0"
              max="300"
            >
          </div>
          
          <div class="col-md-4">
            <input
              type="number"
              class="text"
              v-model.number="phase.promtakta"
              :placeholder="`Промтакт`"
              style="width: 11ch;"
              @input="calculateShifts"
              min="0"
              max="300"
            >
          </div>
          
          <div class="col-md-4">
            <input
              type="text"
              class="_text_"
              :value="shouldShowShift(index) ? phase.shift : ''"
              style="width: 10ch"
              readonly
            >
          </div>
        </div>
      </div>
      <div class="form-inline" style="font-size: 30px">
        Общее время цикла
        <input
          type="text"
          class="_text_"
          :value="totalCycleTime"
          style="font-size: 30px; width: 10ch;"
          readonly
        >
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CalculateCycle",
  data() {
    return {
      phaseCount: 4,
      phases: []
    };
  },
  watch: {
    phaseCount(newVal, oldVal) {
      if (newVal > 0 && newVal <= 14) {
        this.updatePhases();
      } else {
        this.phaseCount = oldVal > 14 ? 14 : oldVal < 1 ? 1 : oldVal;
      }
    }
  },
  computed: {
    totalCycleTime() {
      if (this.phases.length === 0) return 0;
      return this.phases.reduce((sum, phase) => {
        const time = phase.time || 0;
        const promtakta = phase.promtakta !== null ? phase.promtakta : 0;
        return sum + time + promtakta;
      }, 0).toFixed(0);
    }
  },
  mounted() {
    this.updatePhases();
  },
  methods: {
    shouldShowShift(index) {
      // Показываем сдвиг для первой фазы (0) и для фаз, где введено время
      return index === 0 || this.phases[index].time !== null;
    },
    updatePhases() {
      const currentPhases = [...this.phases];
      
      const newPhases = [];
      for (let i = 0; i < this.phaseCount; i++) {
        if (currentPhases[i]) {
          newPhases.push({
            time: currentPhases[i].time,
            promtakta: currentPhases[i].promtakta !== null ? currentPhases[i].promtakta : null,
            shift: 0
          });
        } else {
          newPhases.push({
            time: null,
            promtakta: null,
            shift: 0
          });
        }
      }
      this.phases = newPhases;
      this.calculateShifts();
    },
    calculateShifts() {
      this.phases.forEach((phase, index) => {
        if (index === 0) {
          phase.shift = 0;
        } else {
          const prevPhase = this.phases[index - 1];
          const prevTime = prevPhase.time || 0;
          // Если промтакт null или undefined, считаем как 0
          const prevPromtakta = prevPhase.promtakta !== null ? prevPhase.promtakta : 0;
          phase.shift = this.phases[index - 1].shift + prevTime + prevPromtakta;
        }
      });
    }
  }
};
</script>

<style scoped>
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  background: var(--text-bcg) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="24" viewBox="0 0 16 24"><path fill="%23ffffff" d="M8 5l4 5H4z"/><path fill="%23ffffff" d="M8 19l4-5H4z"/></svg>') no-repeat center center;
  opacity: 0.8;
  width: 16px;
  height: 33px;
  cursor: pointer;
  margin-right: 2px;
}

input[type="number"]::-webkit-inner-spin-button:hover {
  opacity: 1;
}
</style>