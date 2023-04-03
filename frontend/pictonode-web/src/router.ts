// GNU AGPL v3 License

// This file in its entirety was written by John Nunley and Grace Meredith.

import Homepage from "./app/Homepage.vue";
import Login from "./app/Login.vue";
import Register from "./app/Register.vue";
import Aboutpage from "./app/Aboutpage.vue";
import NodeEditor from "./app/NodeEditor.vue";
import Tutorial from "./app/Tutorial.vue";
import * as VueRouter from "vue-router";

const ROUTES = [
  { path: "/", component: Homepage },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/about", component: Aboutpage },
  { path: "/editor", component: NodeEditor },
  { path: "/Tutorial", component: Tutorial },
];

export default VueRouter.createRouter({
  history: VueRouter.createWebHashHistory(),
  routes: ROUTES,
});
