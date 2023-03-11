// GNU AGPL v3 License

// This file in its entirety was written by John Nunley and Grace Meredith.

import Canvas from "./app/Canvas.vue";
import Homepage from "./app/Homepage.vue";
import Login from "./app/Login.vue";
import Register from "./app/Register.vue";
import Aboutpage from "./app/Aboutpage.vue";
import BaklavaTest from "./app/BaklavaTest.vue";
import * as VueRouter from "vue-router";

const ROUTES = [
  { path: "/", component: Homepage },
  { path: "/canvas", component: Canvas },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/about", component: Aboutpage },
  { path: "/baklava", component: BaklavaTest },
];

export default VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes: ROUTES,
});
