<template>
  <div class="container">
    <div class="form-inline">
      <input
        type="text"
        class="minitext"
        id="search_host"
        placeholder="Номер СО"
        style="width: 10ch;"
        v-model="searchValue"
        @input="searchHost"
      />

      <input
        type="text"
        id="ip_address"
        class="minitext"
        v-model="ip"
        placeholder="IP-адрес"
        style="width: 20ch;"
      />

      <select
        id="controller_type"
        class="minitext"
        style="width: 20ch;"
        v-model="protocol"
        @change="updateScnVisibility"
      >
        <option value="">Тип контроллера</option>
        <option v-for="type in typesControllers" :key="type" :value="type">{{ type }}</option>
      </select>


      <div class="form-group" v-if="showScn">
        <input
          type="text"
          id="scn"
          class="minitext"
          v-model="scn"
          placeholder="SCN"
          style="width: 10ch;"
          readonly
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { serverIPs } from '@/assets/js/config';

export default {
  name: "SearchController",
  data() {
    return {
      searchValue: "",
      ip: "",
      protocol: "",
      scn: "",
      showScn: false,
      typesControllers: ["Swarco", "Поток (S)", "Поток (P)", "Peek"],
      token: import.meta.env.VITE_API_TOKEN,
    };
  },
  methods: {
    async searchHost() {
      const searchValue = this.searchValue.trim();
      if (!searchValue) return;

      try {

        const serverIP = serverIPs[0];
        const url = `http://${serverIP}/api/v1/trafficlight-objects/${encodeURIComponent(searchValue)}`;
        console.log("Отправляем запрос по URL:", url);

        const response = await axios.get(url, {
          headers: {
            Authorization: `Token ${this.token}`,
          },
        });

        console.log("Ответ от сервера:", response.data);

        this.ip = response.data.ip_adress || "";
        this.protocol = response.data.type_controller || "";

        this.updateScnVisibility();
      } catch (error) {
        console.error("Ошибка при поиске по номеру СО:", error);
        if (error.response) {
          console.error("Данные ошибки:", error.response.data);
          console.error("Статус ошибки:", error.response.status);
        }
      }
    },
    updateScnVisibility() {
      this.showScn = this.protocol === "Поток (P)" || this.protocol === "Peek";

      if (this.showScn) {
        this.updateScn();
      } else {
        this.scn = "";
      }
    },
    updateScn() {
      const searchValue = this.searchValue.trim();
      if (!searchValue) {
        this.scn = "";
        return;
      }

      if (this.protocol === "Peek") {
        this.scn = `CO${searchValue}`;
      } else if (this.protocol === "Поток (P)") {
        const paddedNumber = searchValue.slice(-4).padStart(4, "0"); // Берем последние 4 цифры и дополняем нулями
        this.scn = `CO${paddedNumber}`;
      } else {
        this.scn = "";
      }
    },
  },
  watch: {
    protocol() {
      this.updateScnVisibility();
    },
    searchValue() {
      this.updateScn();
    },
  },
};
</script>

<style scoped>

</style>