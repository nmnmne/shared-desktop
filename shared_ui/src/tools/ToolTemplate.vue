<template>
  <div>
    <h2></h2>
  </div>
</template>

<script>
import { serverIPs } from '@/assets/js/config';
import axios from 'axios';

export default {
  name: "",
  data() {
    return {
      condition: "",
      functions: [],
      conditionResult: "",
      token: import.meta.env.VITE_API_TOKEN,
      apiPath: "",
      serverIPs: serverIPs,
    };
  },
  methods: {
    async createFunctions() {
      for (let ip of this.serverIPs) {
        const server = `http://${ip}${this.apiPath}`;

        try {
          const response = await axios.post(
            server,
            {
              options: {
                get_functions_from_condition_string: true,
                get_condition_result: false,
              },
              condition: this.condition,
              payload: {},
            },
            {
              headers: {
                "X-CSRFToken": this.getCookie("csrftoken"),
                Authorization: `Token ${this.token}`,
              },
            }
          );

          this.functions = response.data.functions;
          return;
        } catch (error) {
          console.warn(`Ошибка подключения к ${server}:`, error);
        }
      }

      console.error("Ошибка при подключении ко всем серверам.");
    },}}
</script>

<style scoped>

</style>
