<template>
  <div class="home">
    <div class="container-large">
      <h2 class="title media-100">Добро пожаловать на главную страницу</h2>

      <div class="form-inline-media" style="display: flex; gap: 20px;">

        <!-- Левая часть (60%) -->
        <div class="width-60">

          <div v-if="loading">Загрузка...</div>
          <div v-else>
            <div v-for="rule in rules" :key="rule.id" class="rule-item" @click="toggleRule(rule.id)">
              <p class="rules-name">{{ rule.name }}</p>
              <div class="items">
                <pre style="margin-bottom: 15px;">{{ rule.text }}</pre>

                <div style="margin-bottom: 15px; font-size: 12px;" v-if="expandedRules.includes(rule.id)">
                  <p><strong>Ответственный:</strong> {{ rule.responsible }}</p>
                  <p><strong>Комментарий:</strong> {{ rule.comment }}</p>
                  <p><strong>Дата публикации:</strong> {{ formatDate(rule.pub_date) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Форма для добавления новой записи -->
          <div>
            <div style="text-align: right; margin-bottom: 15px;">
              <h3 class="txt-btn" @click="toggleForm">Добавить новую запись</h3>
            </div>
            <div>
              <form @submit.prevent="addRule" v-if="showForm">
                <div>
                  <textarea id="text" class="minitextarea mt" placeholder="Текст" v-model="newRule.text" required></textarea>
                </div>

                <div>
                  <input type="text" class="minitext mt" placeholder="Комментарий" id="comment" v-model="newRule.comment">
                </div>

                <div class="form-inline">
                  <input type="text" class="minitext mt" style="width: 40%;" placeholder="Название" id="name" v-model="newRule.name" required>
                  <input type="text" class="minitext mt" placeholder="Ответственный" id="responsible" v-model="newRule.responsible" required>
                  <button type="submit">Добавить</button>
                </div>
              </form>
            </div>
          </div>

        </div>

        <!-- Правая часть (40%) - Доска для заметок -->
        <div class="width-40">

          <div class="rule-item">
            <p class="notes">Доска для заметок</p>
            <textarea
              v-model="notes"
              class="notes-textarea"
              placeholder="Введите ваши заметки здесь..."
              spellcheck="false"
            ></textarea>
          </div>
          <div style="text-align: right; margin-bottom: 15px;">
            <h3 class="txt-btn" @click="downloadNotesAsTxt">Сохранить в .txt</h3>
          </div>

        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "Home",
  data() {
    return {
      rules: [],
      loading: true,
      newRule: {
        name: '',
        responsible: '',
        comment: '',
        text: '',
        username: 'token_api'
      },
      showForm: false,
      expandedRules: [],
      notes: ''
    };
  },
  mounted() {
    this.fetchRules();
    this.loadNotesFromLocalStorage();
  },
  methods: {

    async fetchRules() {
      try {
        const serverIP = serverIPs[0];
        const url = `http://${serverIP}/index/api/rules/`;
        const response = await axios.get(url);
        this.rules = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
      } finally {
        this.loading = false;
      }
    },

    async addRule() {
      try {
        const serverIP = serverIPs[0];
        const url = `http://${serverIP}/index/api/rules/`;
        const response = await axios.post(url, this.newRule);
        this.rules.unshift(response.data);
        this.newRule = { name: '', responsible: '', comment: '', text: '' };
      } catch (error) {
        console.error('Ошибка при добавлении записи:', error);
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },

    toggleForm() {
      this.showForm = !this.showForm;
    },

    toggleRule(ruleId) {
      if (this.expandedRules.includes(ruleId)) {
        this.expandedRules = this.expandedRules.filter(id => id !== ruleId);
      } else {
        this.expandedRules.push(ruleId);
      }
    },

    loadNotesFromLocalStorage() {
      const savedNotes = localStorage.getItem('notes');
      if (savedNotes) {
        this.notes = savedNotes;
      }
    },

    downloadNotesAsTxt() {
      const blob = new Blob([this.notes], { type: 'text/plain' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'Мои заметки.txt';
      link.click();
      URL.revokeObjectURL(link.href);
    }
  },
  watch: {
    notes(newNotes) {
      localStorage.setItem('notes', newNotes);
    }
  }
};
</script>

<style scoped>
.home {
  padding: 20px;
}

.content-wrapper {
  display: flex;
  gap: 20px;
}

.rule-item {
  margin-bottom: 4px;
  border: 1px solid var(--border);
  border-radius: 9px;
  background-color: var(--div);
  cursor: pointer;
}

.items {
  padding: 2px 1px 2px 6px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.txt-btn {
  margin-top: 10px;
  background-color: var(--div);
  cursor: pointer;
  display: inline-block;
  padding: 1px 16px;
  border-radius: 9px;
}

.notes-textarea {
  width: 100%;
  height: 406px;
  font-size: 16px;
  padding: 10px;
  border: 0px solid var(--border);
  border-radius: 9px;
  background-color: var(--div);
  resize: vertical;
  line-height: 1.1;
  color: var(--text-1);
  font-family: Arial, Helvetica, sans-serif;
}

.notes-textarea:focus {
  outline: none;
}
</style>