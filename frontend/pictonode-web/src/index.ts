// GNU AGPL 3.0 License

// This file in its entirety was written by John Nunley and Grace Meredith.

import { createApp } from "vue";
import App from "./app/App.vue";
import Router from "./router";

import "vuetify/styles";
import { createVuetify } from "vuetify";

import "./style/basics.scss";
import "@mdi/font/css/materialdesignicons.css";

window.onload = () => {
  const instance = createApp(App);
  instance.use(createVuetify());
  instance.use(Router);
  instance.mount("#app");
};
