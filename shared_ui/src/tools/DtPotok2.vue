<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Генерация сложных условий вызова или продления</h2>

      <div class="form-inline">
        <input 
          type="text" 
          v-model="detRangesAndGroup" 
          placeholder="1-5 & 5-6" 
          class="text"
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

      <!-- Инструкция для расширенного генератора -->
      <div class="instruction-box mt30">
        <ul>
          <li>Диапазон детекторов обозначаем через дефис <code>-</code></li>
          <li>Круглые скобки: <code>()</code> для группировки условий</li>
          <li>Оператор <code>&</code> для "and" или <code>|</code> для "or" между условиями</li>
        </ul>

        <h5>Примеры сложных выражений:</h5>
        <ul>
          <li><code>1-5 & 5-6</code><br>
          <small>(ddr(D1) or ddr(D2) or ddr(D3) or ddr(D4) or ddr(D5)) and (ddr(D5) or ddr(D6))</small></li>
             
          <li><code>1-5 & 5-6 & 7-9</code><br>
          <small>(ddr(D1) or ddr(D2) or ddr(D3) or ddr(D4) or ddr(D5)) and (ddr(D5) or ddr(D6)) and (ddr(D7) or ddr(D8) or ddr(D9))</small></li>

          <li><code>((1-3) & (5-6)) & (8-9 | 10-11)</code><br>
          <small>((ddr(D1) or ddr(D2) or ddr(D3)) and (ddr(D5) or ddr(D6))) and (ddr(D8) or ddr(D9) or ddr(D10) or ddr(D11))</small></li>
        </ul>

        <div class="hints-section">
          <h4>Подсказки:</h4>
          <div class="hint-item">
            <code>() and mr(G)</code>
            <span class="hint-description">Продление по ТМакс</span>
          </div>
          <div class="hint-item">
            <code>dde(D1) or dde(D2)</code>
            <span class="hint-description">True если детекторы в ошибке</span>
          </div>
          <div class="hint-item">
            <code>(ddr(D18) or ddr(D19) or ddr(D20)) and (fctg(G4)<35)</code>
            <span class="hint-description">продление по таймеру</span>
          </div>
          <div class="hint-item">
            <code>(fctg(G11) <= 70) and (ddr(D127) or ddr(D128))</code>
            <span class="hint-description">Переходы по таймеру</span>
          </div>
          <div class="hint-item">
            <code>(ddr(D11) or ddr(D19)) and not(ddr(D14)) and not(ddr(D20))</code>
            <span class="hint-description">Инверсия</span>
          </div>
          <div class="hint-item">
            <code>(ddr(D1) or ddr(D2)) and (stgp()!=1)</code>
            <span class="hint-description">Предыдущая фаза</span>
          </div>
        </div>

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

<style scoped>
.instruction-box {
  background: var(--text-bcg-2);
  border: 1px solid var(--border-2);
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--text7);
}

.instruction-box h4 {
  margin-top: 0;
  color: var(--text7);
  border-bottom: 1px solid var(--border-2);
  padding-bottom: 8px;
}

.instruction-box h5 {
  color: var(--text7);
  margin: 15px 0 8px 0;
  font-size: 13px;
}

.instruction-box ul {
  margin: 8px 0;
  padding-left: 20px;
}

.instruction-box li {
  margin-bottom: 10px;
  color: var(--text7);
  font-size: 13px;
  line-height: 1.4;
}

.instruction-box li small {
  color: var(--text10);
  font-size: 12px;
  display: block;
  margin-top: 3px;
  font-family: monospace;
}

.instruction-box code {
  background: var(--text-bcg);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: var(--text9);
  border: 1px solid var(--border-2);
  font-size: 12px;
}

/* Стили для секции с подсказками */
.hints-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid var(--border-2);
}

.hints-section h4 {
  color: var(--text7);
  margin-bottom: 12px;
  font-size: 15px;
}

.hint-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: var(--text-bcg-3);
  border-radius: 4px;
  border-left: 3px solid var(--button-3-bgc);
}

.hint-item code {
  flex: 0 0 auto;
  margin-right: 12px;
  background: var(--text-bcg-1);
  color: var(--text9);
}

.hint-description {
  color: var(--text7);
  font-size: 13px;
}

.code-output {
  background: var(--text-bcg-2); 
  color: var(--text7);
  font-family: monospace;
  white-space: pre-wrap;
  border: 1px solid var(--border-2);
  padding: 6px 2px 2px 6px;
  min-height: 250px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 14px;
}

.code-output ::v-deep .op-and {
  color: var(--green1);
  font-weight: bold;
}

.code-output ::v-deep .op-or {
  color: var(--yellow);
  font-weight: bold;
}

.code-output ::v-deep .op-ddo {
  color: #569cd6;
  font-weight: bold;
}

.code-output ::v-deep .bracket {
  color: var(--text7);
  transition: background 0.2s, color 0.2s;
}

.code-output ::v-deep .bracket-hover {
  color: var(--bracket);
  background-color: var(--header-bcg);
  border-radius: 3px;
  font-weight: bold;
}

.alert-danger {
  background-color: var(--button-4-bgc);
  border-color: var(--border);
  color: var(--text4);
}

.btn-primary {
  background-color: var(--button-1-bgc);
  border-color: var(--border);
  color: var(--text4);
}

.btn-primary:hover {
  background-color: var(--hover-sbr);
  border-color: var(--border);
}

.btn-copy {
  background-color: var(--button-2-bgc);
  border-color: var(--border);
  color: var(--text4);
}

.btn-copy:hover {
  background-color: var(--hover-sbr);
  border-color: var(--border);
}

.text {
  background-color: var(--text-bcg-2);
  color: var(--text7);
  border: 1px solid var(--border-2);
}

.text::placeholder {
  color: var(--text10);
}

.mini-text {
  background-color: var(--text-bcg-2);
  color: var(--text7);
  border: 1px solid var(--border-2);
}
</style>