<template>
  <div class="container">
    <h2 class="title">Подсчет длительности направлений Excel</h2>
  
    <div class="info">
      <p>
        Обработка "Дирижёр" отчета, суммирование фаз в которых участвует направление.<br>
        Установите флажок рядом с группой, включение которой будет обозначать новый цикл.
      </p>
    </div>
    <div style="margin-bottom: 18px;">
      <span @click="toggleVisibility" style="cursor: pointer; user-select: none; margin: 7px;">
        {{ isVisible ? 'Скрыть ^' : 'Сохранить новые настройки >' }}
      </span></div>
      <div class="form-inline" style="margin-bottom: 100px;" :class="{ hidden: !isVisible }">
        <input
          type="text"
          class="text"
          style="font-size: 23px; font-family: monospace;"
          v-model="name"
          placeholder="Введите номер СО, для сохранения настроек"
        />

        <button type="button" class="batton" style="width: 176px" @click="handleSubmit('save_button')">Сохранить</button>
      
    </div>
    <div id="main-form">
      <div class="form-inline">
        <select class="select" v-model="selectedParameterSet" @change="triggerUpload">
          <option value="" disabled>Выберите сохраненные настройки</option>
          <option v-for="set in parameterSets" :key="set.name" :value="set.name">
            {{ set.name }}
          </option>
        </select>
  
        <div style="width: 185px">
          <select class="select" v-model="interval">
            <option value="10">10 минут</option>
            <option value="15">15 минут</option>
            <option value="20">20 минут</option>
            <option value="30">30 минут</option>
            <option value="60" selected>60 минут</option>
          </select>
        </div>
      </div>
  
      <div class="form-inline" style="margin-bottom: 30px;">
        <input type="file" class="custom-file-input" @change="handleFileUpload" />
        <button type="button" class="batton" style="width: 176px" @click="handleSubmit('process_button')">Обработать</button>
      </div>
  
      <div class="row">
        <div class="col-9">
          <div id="warning" class="alert alert-info" v-if="showWarning">
            Пожалуйста, выберите основную группу, включение которой обозначает новый цикл.
          </div>
        </div>
      </div>
  
      <div id="phase-parameters">
        <div class="form-inline" v-for="i in 20" :key="i">
          <div class="centr">
            <input
              class="radio"
              type="radio"
              :name="`primary_group`"
              :value="`group${i}`"
              v-model="primaryGroup"
            />
          </div>

          <input
            type="text"
            class="minitext"
            style="width: 11ch;"
            :id="`group${i}`"
            :name="`group${i}`"
            placeholder="Сигнальная группа"
            v-model="groups[`group${i}`]"
          />

          <input
            type="text"
            class="minitext"
            style="width: 58ch;"
            :id="`phases${i}`"
            :name="`phases${i}`"
            placeholder="Фазы"
            v-model="phases[`phases${i}`]"
          />

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "ExcelProcessor",
  data() {
    return {
      isVisible: false,
      serverIPs: serverIPs,
      selectedParameterSet: "",
      parameterSets: [],
      interval: "60",
      name: "",
      primaryGroup: "",
      groups: {
        group1: "",
        group2: "",
        group3: "",
        group4: "",
        group5: "",
        group6: "",
        group7: "",
        group8: "",
        group9: "",
        group10: "",
        group11: "",
        group12: "",
        group13: "",
        group14: "",
        group15: "",
        group16: "",
        group17: "",
        group18: "",
        group19: "",
        group20: "",
      },
      phases: {
        phases1: "",
        phases2: "",
        phases3: "",
        phases4: "",
        phases5: "",
        phases6: "",
        phases7: "",
        phases8: "",
        phases9: "",
        phases10: "",
        phases11: "",
        phases12: "",
        phases13: "",
        phases14: "",
        phases15: "",
        phases16: "",
        phases17: "",
        phases18: "",
        phases19: "",
        phases20: "",
      },
      file: null,
      showWarning: false,
    };
  },
  methods: {
    toggleVisibility() {
      this.isVisible = !this.isVisible;
    },
    async triggerUpload() {
      if (this.selectedParameterSet) {
        for (let ip of this.serverIPs) {
          try {
            const server = `http://${ip}/api/parameter-sets/${encodeURIComponent(this.selectedParameterSet)}/`;
            const response = await axios.get(server);
            const data = response.data;

            if (data && data.data) {
              this.name = data.name;
              this.primaryGroup = data.data.primary_group;
              this.groups = {
                group1: data.data.group1 || "",
                group2: data.data.group2 || "",
                group3: data.data.group3 || "",
                group4: data.data.group4 || "",
                group5: data.data.group5 || "",
                group6: data.data.group6 || "",
                group7: data.data.group7 || "",
                group8: data.data.group8 || "",
                group9: data.data.group9 || "",
                group10: data.data.group10 || "",
                group11: data.data.group11 || "",
                group12: data.data.group12 || "",
                group13: data.data.group13 || "",
                group14: data.data.group14 || "",
                group15: data.data.group15 || "",
                group16: data.data.group16 || "",
                group17: data.data.group17 || "",
                group18: data.data.group18 || "",
                group19: data.data.group19 || "",
                group20: data.data.group20 || "",
              };
              this.phases = {
                phases1: data.data.phases1 || "",
                phases2: data.data.phases2 || "",
                phases3: data.data.phases3 || "",
                phases4: data.data.phases4 || "",
                phases5: data.data.phases5 || "",
                phases6: data.data.phases6 || "",
                phases7: data.data.phases7 || "",
                phases8: data.data.phases8 || "",
                phases9: data.data.phases9 || "",
                phases10: data.data.phases10 || "",
                phases11: data.data.phases11 || "",
                phases12: data.data.phases12 || "",
                phases13: data.data.phases13 || "",
                phases14: data.data.phases14 || "",
                phases15: data.data.phases15 || "",
                phases16: data.data.phases16 || "",
                phases17: data.data.phases17 || "",
                phases18: data.data.phases18 || "",
                phases19: data.data.phases19 || "",
                phases20: data.data.phases20 || "",
              };
            }
            break;
          } catch (error) {
            console.warn(`Ошибка при загрузке настроек с ${ip}:`, error);
          }
        }
      }
    },
    handleFileUpload(event) {
      this.file = event.target.files[0];
      console.log("Файл загружен:", this.file);
    },
    async handleSubmit(buttonClicked) {
      if (!this.primaryGroup && (buttonClicked === "process_button" || buttonClicked === "save_button")) {
        this.showWarning = true;
        return;
      }

      const formData = new FormData();
      formData.append("name", this.name);
      formData.append("primary_group", this.primaryGroup);
      formData.append("interval", this.interval);
      formData.append("file", this.file);


      if (buttonClicked === "save_button") {
        formData.append("save_button", "1");
      } else if (buttonClicked === "process_button") {
        formData.append("process_button", "1");
      }

      for (let i = 1; i <= 20; i++) {
        formData.append(`group${i}`, this.groups[`group${i}`] || "");
        formData.append(`phases${i}`, this.phases[`phases${i}`] || "");
      }

      try {
        const response = await axios.post(`http://${this.serverIPs[0]}/api/openpyxl/`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          responseType: buttonClicked === "process_button" ? "blob" : "json",
        });

        if (buttonClicked === "process_button" && response.data instanceof Blob) {

          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", "openpyxl.xlsx");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else if (buttonClicked === "save_button") {

          alert("Настройки успешно сохранены!");
        }
      } catch (error) {
        console.error("Ошибка при отправке данных:", error);
        alert("Произошла ошибка при обработке запроса.");
      }
    }
  },
  async created() {
    for (let ip of this.serverIPs) {
      try {
        const server = `http://${ip}/api/openpyxl/`;
        const response = await axios.get(server);
        this.parameterSets = response.data;
        console.log("Загруженные параметры:", this.parameterSets);
        break;
      } catch (error) {
        console.warn(`Ошибка при загрузке параметров с ${ip}:`, error);
      }
    }
  },
};
</script>

<style scoped>

</style>