<template>
  <div class="tools">
    <div class="container tools-left">
      <h2 class="title">Генератор таблицы детекторов</h2>
      
      <div class="input-section">
        <label for="detectors-input">
          <div class="input-instructions">

            <div class="format-block">
              <p><strong>Формат ввода:</strong></p>

              <ul>
                <li>Вводите только <strong>последний детектор</strong> для каждого направления</li>
                <li>Допустимые детекторы <strong>TVP, D, DO</strong></li>
                <li>Разделяйте детекторы <strong>запятыми</strong> или <strong>переносами строк</strong></li>
              </ul>
            </div>

            <div class="examples-block">
              <pre> </pre>
              <p><strong>Пример ввода:</strong></p>
              <div class="example">

                <pre>TVP3.10, D1.5, D2.10, DO2.2</pre>
                <pre> </pre>
                <p><strong>Будет сгенерировано:</strong></p>
                <ul>
                  <li>10 кнопок ТВП 3 направления</li>
                  <li>5 детекторов 1 направления</li>
                  <li>10 детекторов 2 направления</li>
                  <li>2 петли завершения 2 направления</li>
                </ul>
              </div>
            </div>
          </div>
        </label>
        <textarea 
          id="detectors-input" 
          v-model="detectorsInput" 
          @input="handleInput"
          placeholder="TVP4.4, D1.12, DO2.2..."
          rows="5"
          class="minitextarea"
        ></textarea>
      </div>

      <!-- <div class="json-preview">
        <h3>Формируемый JSON:</h3>
        <pre>{{ jsonPreview }}</pre>
      </div> -->

      <button class="generate-btn" @click="sendData" :disabled="!detectorsInput.trim()">
        Сгенерировать таблицу
      </button>

      <div v-if="responseMessage" class="response-message" :class="{ error: responseIsError }">
        {{ responseMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "TabDtGen",
  data() {
    return {
      token: import.meta.env.VITE_API_TOKEN,
      serverIPs: serverIPs,
      apiPath1: "/generate-detector-table/",
      detectorsInput: "",
      jsonPreview: '{\n  "detectors": []\n}',
      responseMessage: "",
      responseIsError: false,
      responseData: null
    };
  },
  methods: {
    handleInput(event) {
    // Сохраняем позицию курсора
    const cursorPosition = event.target.selectionStart;
    
    // Преобразуем текст к верхнему регистру
    this.detectorsInput = event.target.value.toUpperCase();
    
    // Восстанавливаем позицию курсора после обновления значения
    this.$nextTick(() => {
      event.target.setSelectionRange(cursorPosition, cursorPosition);
    });
    
    // Обновляем JSON-превью
    this.updateJsonPreview();
  },
    updateJsonPreview() {
      const detectorsArray = this.parseDetectorsInput();
      // Формируем JSON с компактным массивом detectors
      this.jsonPreview = `{
  "detectors": [${detectorsArray.map(d => `"${d}"`).join(',')}]
}`;
    },
    
    parseDetectorsInput() {
      return this.detectorsInput
        .split(/[,\n]/)
        .map(item => item.trim().toUpperCase())
        .filter(item => item.length > 0);
    },

    async sendData() {
      const detectors = this.parseDetectorsInput();
      
      if (detectors.length === 0) {
        this.responseMessage = "Пожалуйста, введите хотя бы один детектор";
        this.responseIsError = true;
        return;
      }

      this.responseMessage = "Отправка данных...";
      this.responseIsError = false;

      const requestData = {
        detectors: detectors
      };

      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath1}`;
        
        try {
          // 1. Логируем данные перед отправкой
          console.log("Отправляемые данные:", JSON.stringify(requestData));
          
          // 2. Отправка через axios с явными настройками
          const response = await axios({
            method: 'post',
            url: server,
            data: requestData, // axios сам сериализует в JSON
            headers: {
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'application/json',
            },
            responseType: 'blob' // Важно для получения бинарных данных
          });

          // 3. Проверяем успешность запроса
          if (response.status !== 200) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          // 4. Создаем ссылку для скачивания
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'detectors_table.docx');
          document.body.appendChild(link);
          link.click();
          
          // 5. Убираем ссылку после скачивания
          setTimeout(() => {
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
          }, 100);
          
          this.responseMessage = "Таблица успешно сгенерирована и скачана!";
          this.responseIsError = false;
          return;
          
        } catch (error) {
          console.error(`Ошибка при подключении к ${server}:`, error);
          
          // Детализация ошибки
          let errorMessage = error.message;
          if (error.response) {
            errorMessage += ` (Status: ${error.response.status})`;
            if (error.response.data) {
              try {
                const errorData = await error.response.data.text();
                errorMessage += ` - ${errorData}`;
              } catch (e) {
                console.error("Ошибка чтения тела ошибки:", e);
              }
            }
          }
          
          this.responseMessage = `Ошибка: ${errorMessage}`;
          this.responseIsError = true;
        }
      }
    }
  }
};
</script>

<style scoped>

.input-instructions {
  background-color: var(--inf);
  border-left: 4px solid var(--green1);
  padding: 10px 15px;
  margin: 10px 0;
  border-radius: 4px;
}

.input-instructions ul {
  padding-left: 20px;
  margin: 5px 0;
}

.input-instructions code {
  background-color: #e9ecef;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

.examples {
  background-color: #f1f1f1;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.examples pre {
  margin: 5px 0;
  font-family: monospace;
  white-space: pre-wrap;
}

.note {
  font-style: italic;
  color: #6c757d;
  margin-top: 10px;
}

.tools {
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: var(--container);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}


.input-section {
  margin-bottom: 20px;
}

.input-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text2);
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
  resize: vertical;
}

.json-preview {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
  border-left: 4px solid #42b983;
}

.json-preview h3 {
  margin-top: 0;
  color: #2c3e50;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: monospace;
}

.generate-btn {
  background: var(--button-1-bgc);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.generate-btn:hover {
  background: var(--button-2-bgc);
}

.generate-btn:disabled {
  background: var(--button-5-bgc);
  cursor: not-allowed;
}

.response-message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.response-message:not(.error) {
  background: #d4edda;
  color: var(--green1)
}

.response-message.error {
  background: #f8d7da;
  color: #721c24;
}
</style>