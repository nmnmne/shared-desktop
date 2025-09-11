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

      <div v-if="responseData" class="download-section">
        <button class="download-btn" @click="downloadFile">
          📥 Скачать DOCX файл
        </button>
      </div>

      <div v-if="responseMessage" class="response-message" :class="{ error: responseIsError }">
        {{ responseMessage }}
      </div>
    </div>

    <div class="tools-right">
      <div v-if="responseData && responseData.table_data" class="table-preview">
        <h3>Предпросмотр таблицы</h3>
        <div class="table-container">
          <table class="detectors-table" ref="tableToCopy">
            <thead>
              <tr>
                <th v-for="header in headers" :key="header">{{ header }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in responseData.table_data" :key="index">
                <td v-for="key in tableKeys" :key="key">{{ row[key] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <button class="copy-table-btn" @click="copyTableToClipboard">
          📋 Скопировать таблицу (без заголовков)
        </button>
        <div v-if="copyMessage" class="copy-message" :class="{ error: copyIsError }">
          {{ copyMessage }}
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>Здесь будет отображаться предпросмотр таблицы после генерации</p>
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
      responseData: null,
      copyMessage: "",
      copyIsError: false,
      headers: [
        'Детектор', '№ Входа платы IO/входа ДК', 'КИ ПД-2', 'КИ ПД-16',
        '№ Направления', 'Вынос, м', 'Запрос', 'Разрыв, с',
        'Авария незанят, мин', 'Авария занят, мин'
      ],
      tableKeys: [
        'name', 'io_board_input', 'ki_pd_2', 'ki_pd_16', 
        'direction_number', 'offset', 'request', 'gap', 
        'unoccupied_alarm', 'occupied_alarm'
      ]
    };
  },
  methods: {
    handleInput(event) {
      const cursorPosition = event.target.selectionStart;
      this.detectorsInput = event.target.value.toUpperCase();
      this.$nextTick(() => {
        event.target.setSelectionRange(cursorPosition, cursorPosition);
      });
      this.updateJsonPreview();
    },
    
    updateJsonPreview() {
      const detectorsArray = this.parseDetectorsInput();
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
      this.responseData = null;

      const requestData = {
        detectors: detectors
      };

      for (let ip of this.serverIPs) {
        let server = `http://${ip}${this.apiPath1}`;
        
        try {
          console.log("Отправляемые данные:", JSON.stringify(requestData));
          
          const response = await axios({
            method: 'post',
            url: server,
            data: requestData,
            headers: {
              'Authorization': `Token ${this.token}`,
              'Content-Type': 'application/json',
            },
            responseType: 'json'
          });

          if (response.status !== 200) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          this.responseData = response.data;
          this.responseMessage = "Таблица успешно сгенерирована!";
          this.responseIsError = false;
          return;
          
        } catch (error) {
          console.error(`Ошибка при подключении к ${server}:`, error);
          
          let errorMessage = error.message;
          if (error.response) {
            errorMessage += ` (Status: ${error.response.status})`;
            if (error.response.data) {
              try {
                if (typeof error.response.data === 'object') {
                  errorMessage += ` - ${JSON.stringify(error.response.data)}`;
                } else {
                  errorMessage += ` - ${error.response.data}`;
                }
              } catch (e) {
                console.error("Ошибка чтения тела ошибки:", e);
              }
            }
          }
          
          this.responseMessage = `Ошибка: ${errorMessage}`;
          this.responseIsError = true;
        }
      }
    },

    downloadFile() {
      if (!this.responseData || !this.responseData.file || !this.responseData.file.base64) {
        this.responseMessage = "Нет данных файла для скачивания";
        this.responseIsError = true;
        return;
      }

      try {
        const binaryString = atob(this.responseData.file.base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', this.responseData.file.filename || 'detectors_table.docx');
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);
        
        this.responseMessage = "Файл успешно скачан!";
        this.responseIsError = false;
        
      } catch (error) {
        this.responseMessage = `Ошибка при скачивании файла: ${error.message}`;
        this.responseIsError = true;
      }
    },

    copyTableToClipboard() {
      if (!this.responseData || !this.responseData.table_data) {
        this.copyMessage = "Нет данных таблицы для копирования";
        this.copyIsError = true;
        return;
      }

      try {
        // Создаем HTML-таблицу без заголовков
        let htmlContent = `<table style="font-family: 'Times New Roman', serif; font-size: 12pt; border-collapse: collapse; width: 100%;">`;
        
        // Добавляем только строки с данными (без заголовков)
        this.responseData.table_data.forEach(row => {
          htmlContent += `<tr style="border: 1px solid black;">`;
          this.tableKeys.forEach(key => {
            htmlContent += `<td style="border: 1px solid black; padding: 4px; text-align: center;">${row[key] || ''}</td>`;
          });
          htmlContent += `</tr>`;
        });
        
        htmlContent += `</table>`;

        // Создаем временный элемент для копирования
        const tempElement = document.createElement('div');
        tempElement.innerHTML = htmlContent;
        document.body.appendChild(tempElement);

        // Выбираем содержимое
        const range = document.createRange();
        range.selectNode(tempElement);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        // Копируем в буфер обмена
        const successful = document.execCommand('copy');
        
        // Удаляем временный элемент
        document.body.removeChild(tempElement);
        selection.removeAllRanges();

        if (successful) {
          this.copyMessage = "Таблица скопирована в буфер обмена! Теперь вставьте её в Word.";
          this.copyIsError = false;
        } else {
          throw new Error('Не удалось скопировать таблицу');
        }
      } catch (error) {
        this.copyMessage = `Ошибка при копировании таблицы: ${error.message}`;
        this.copyIsError = true;
      }
    }
  }
};
</script>

<style scoped>
.tools {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
}

.tools-left {
  grid-column: 1;
}

.tools-right {
  grid-column: 2;
  background: var(--container);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-height: 80vh;
  overflow-y: auto;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: var(--container);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

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

.input-section {
  margin-bottom: 20px;
}

.input-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text2);
}

.minitextarea {
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

.download-section {
  margin-top: 20px;
}

.download-btn {
  background: var(--button-3-bgc);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.download-btn:hover {
  background: var(--button-4-bgc);
}

.copy-table-btn {
  background: var(--button-2-bgc);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 15px;
  transition: background 0.3s;
  width: 100%;
}

.copy-table-btn:hover {
  background: var(--button-1-bgc);
}

.copy-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.copy-message:not(.error) {
  background: var(--green2);
  color: var(--green1);
}

.copy-message.error {
  background: #f8d7da;
  color: #721c24;
}

.table-preview h3 {
  margin-top: 0;
  color: var(--text2);
  border-bottom: 2px solid var(--green1);
  padding-bottom: 10px;
}

.table-container {
  overflow-x: auto;
  max-height: none;
  transition: max-height 0.3s ease;
}

.detectors-table {
  border-collapse: collapse;
  font-size: 14px;
}

.detectors-table th,
.detectors-table td {
  padding: 1px 5px;
  text-align: center;
  border: 1px solid var(--text-bcg-6);
}

.detectors-table th {
  background-color: var(--text-bcg-9);
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

.empty-state {
  text-align: center;
  color: #666;
  padding: 40px 20px;
  font-style: italic;
}

.response-message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.response-message:not(.error) {
  background: var(--green2);
  color: var(--green1);
}

.response-message.error {
  background: #f8d7da;
  color: #721c24;
}
</style>