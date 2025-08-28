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
        <div 
          class="code-output" 
          contenteditable="true" 
          v-html="highlightedResponse"
        ></div>
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
    const savedDraft = localStorage.getItem('dtPotok2Draft');
    if (savedDraft) {
      this.draft = savedDraft;
    }

    this.$nextTick(() => {
      this.setupBracketHover();
    });
  },
  updated() {
    this.$nextTick(() => {
      this.setupBracketHover();
    });
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
      const tempEl = document.createElement("textarea");
      tempEl.value = this.response;
      document.body.appendChild(tempEl);
      tempEl.select();
      document.execCommand("copy");
      document.body.removeChild(tempEl);
    },

    saveDraft() {
      localStorage.setItem('dtPotok2Draft', this.draft);
    },

    setupBracketHover() {
      const brackets = this.$el.querySelectorAll('.bracket');
      brackets.forEach(bracket => {
        const id = bracket.dataset.id;
        bracket.addEventListener('mouseenter', () => {
          const pair = this.$el.querySelectorAll(`.bracket[data-id="${id}"]`);
          pair.forEach(el => el.classList.add('bracket-hover'));
        });
        bracket.addEventListener('mouseleave', () => {
          const pair = this.$el.querySelectorAll(`.bracket[data-id="${id}"]`);
          pair.forEach(el => el.classList.remove('bracket-hover'));
        });
      });
    }
  },
  computed: {
    highlightedResponse() {
      if (!this.response) return '';

      let text = this.response
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // Подсветка операторов
      text = text.replace(/\b(and)\b/g, '<span class="op-and">$1</span>');
      text = text.replace(/\b(or)\b/g, '<span class="op-or">$1</span>');

      // Подсветка только ddo красным
      text = text.replace(/\bddo\b/g, '<span class="op-ddo">$&</span>');

      // Подсветка скобок с парной идентификацией
      let result = '';
      let stack = [];
      let pairId = 0;

      for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char === '(') {
          pairId++;
          stack.push(pairId);
          result += `<span class="bracket" data-id="${pairId}">(</span>`;
        } else if (char === ')') {
          const id = stack.pop();
          result += `<span class="bracket" data-id="${id}">)</span>`;
        } else {
          result += char;
        }
      }

      return result;
    }
  }
};
</script>

<style>
.code-output {
  background: var(--text-bcg-2); 
  color: var(--text7);
  font-family: monospace;
  white-space: pre-wrap;
  border: 1px solid #ccc;
  padding: 6px 2px 2px 6px;
  min-height: 250px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 14px;
}

.code-output .op-and {
  color: #4ec9b0;
  font-weight: bold;
}

.code-output .op-or {
  color: #c586c0;
  font-weight: bold;
}

.code-output .op-ddo {
  color: #569cd6;
  font-weight: bold;
}

.code-output .bracket {
  color: var(--text7);
  transition: background 0.2s, color 0.2s;
}

.code-output .bracket-hover {
  color: var(--bracket);
  background-color: var(--header-bcg);
  border-radius: 3px;
  font-weight: bold;
}
</style>
