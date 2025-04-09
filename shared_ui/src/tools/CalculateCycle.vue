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
              style="width: 13ch; color: #999;"
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
              style="width: 11ch; color: #999;"
              @input="calculateShifts"
              min="0"
              max="300"
            >
          </div>
          
          <div class="col-md-4">
            <input
              type="text"
              class="_text_"
              :value="shouldShowShift(phase) ? phase.shift : ''"
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
      phaseCount: 8,
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
      return this.phases[this.phases.length - 1].shift.toFixed(0);
    }
  },
  mounted() {
    this.updatePhases();
  },
  methods: {
    shouldShowShift(phase) {
      return phase.time !== null && phase.promtakta !== null;
    },
    updatePhases() {
      const currentPhases = [...this.phases];
      
      const newPhases = [];
      for (let i = 0; i < this.phaseCount; i++) {
        if (currentPhases[i]) {
          newPhases.push({
            time: currentPhases[i].time,
            promtakta: currentPhases[i].promtakta,
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
      let prevShift = 0;
      this.phases.forEach(phase => {
        const time = phase.time || 0;
        const promtakta = phase.promtakta || 0;
        phase.shift = prevShift + time + promtakta;
        prevShift = phase.shift;
      });
    }
  }
};
</script>

<style scoped>

</style>