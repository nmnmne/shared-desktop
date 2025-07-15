<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Генерация условий вызова или продления 2</h2>
      <div class="form-inline">
        <input 
          type="text" 
          v-model="detRangesAndGroup" 
          placeholder="1-4, 7-7, 3" 
          class="text"
          style="width:28ch;"
          @keyup.enter="generateCondition"
        />
        <button @click="generateCondition" class="btn btn-primary mt-2">
          Сгенерировать
        </button>
      </div>

      <div v-if="response">
        <h4>Результат:</h4>
        <textarea class="minitext" rows="12">{{ response }}</textarea>
        <button v-if="response" @click="copyToClipboard" class="btn btn-copy mt-2">
          Скопировать
        </button>
      </div>

      <div v-if="error" class="alert alert-danger mt-3">
        <strong>Ошибка:</strong> {{ error }}
      </div>
    </div>

    <div class="tools-right">

        <textarea 
          class="mini-text" 
          rows="50"
          v-model="draft"
          @input="saveDraft"
        ></textarea>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "DtPotok2",
  data() {
    return {
      detRangesAndGroup: "",
      draft: "",
      response: null,
      error: null,
      servers: serverIPs.map(ip => `http://${ip}/tools/dt_potok2_api/`),
    };
  },
  mounted() {
    // Загружаем черновик из localStorage при загрузке компонента
    const savedDraft = localStorage.getItem('dtPotok2Draft');
    if (savedDraft) {
      this.draft = savedDraft;
    }
  },
  methods: {
    async generateCondition() {
      this.error = null;
      this.response = null;

      for (let server of this.servers) {
        try {
          const res = await axios.post(server, {
            user_condition_string: this.detRangesAndGroup,
            func_name: "ddr"
          });

          if (res.data.result_condition) {
            this.response = res.data.result_condition;
            return;
          } else if (res.data.errors) {
            this.error = res.data.errors;
            return;
          }
        } catch (err) {
          console.warn(`Ошибка подключения к ${server}:`, err);
        }
      }

      this.error = "Ошибка при подключении к серверам.";
    },

    copyToClipboard() {
      const textarea = this.$el.querySelector('.minitext');
      textarea.select();
      document.execCommand('copy');
    },
    
    saveDraft() {
      // Сохраняем черновик в localStorage при каждом изменении
      localStorage.setItem('dtPotok2Draft', this.draft);
    }
  },
};
</script>

<style scoped>

</style>