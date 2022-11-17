// GNU AGPL v3 License

import Canvas from "./app/Canvas.vue";
import Homepage from "./app/Homepage.vue";
import Login from "./app/Login.vue";
import Register from "./app/Register.vue";
import * as VueRouter from "vue-router";

const ROUTES = [
    { path: "/", component: Homepage, },
    { path: "/canvas", component: Canvas },
    { path: "/login", component: Login },
    { path: "/register", component: Register },
]

export default VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: ROUTES,
});