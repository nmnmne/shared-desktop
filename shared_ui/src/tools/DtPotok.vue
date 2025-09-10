<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Генерация простых условий вызова или продления</h2>

      <div class="form-inline">
        <input 
          type="text" 
          v-model="detRangesAndGroup" 
          placeholder="1-4, 7-7, 3" 
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

      <div class="instruction-box mt30">
        <p>Для генерации введите диапазоны номеров детекторов и номер группы в следующем формате:</p>
        <ul>
          <li>Диапазоны номеров детекторов указываются через дефис или плюс, например: <code>1-4, 7-12, 14-14</code></li>
          <li>Номер группы указывается отдельно после диапазонов детекторов, например: <code>3</code></li>
          <li>Пример корректного ввода: <code>1-4, 7-12, 3</code></li>
          <li>При использовании дефиса диапазон детекторов объединяется логическим OR, при использовании плюса логическим AND.</li>
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
  name: "DtPotok",
  data() {
    return {
      detRangesAndGroup: "",
      draft: "",
      response: null,
      error: null,
      servers: serverIPs.map(ip => `http://${ip}/tools/dt_potok_api/`),
    };
  },
  mounted() {
    const savedDraft = localStorage.getItem('dtPotokDraft');
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
            det_ranges_and_group: this.detRangesAndGroup,
          });

          if (res.data.condition_string) {
            this.response = res.data.condition_string;
            return;
          } else if (res.data.error) {
            this.error = res.data.error;
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
      localStorage.setItem('dtPotokDraft', this.draft);
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

      text = text.replace(/\b(and)\b/g, '<span class="op-and">$1</span>');
      text = text.replace(/\b(or)\b/g, '<span class="op-or">$1</span>');

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

.instruction-box ul {
  margin: 10px 0;
  padding-left: 20px;
}

.instruction-box li {
  margin-bottom: 5px;
  color: var(--text7);
}

.instruction-box code {
  background: var(--text-bcg);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: var(--text9);
  border: 1px solid var(--border-2);
}

.instruction-box p {
  color: var(--text7);
  margin-bottom: 10px;
}

.instruction-box p:last-child {
  margin-bottom: 0;
  font-style: italic;
  color: var(--text10);
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