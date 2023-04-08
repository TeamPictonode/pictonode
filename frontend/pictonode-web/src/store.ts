import { createStore } from "vuex";
import { checkLogin, setRegister } from "./api";

const store = createStore({
  state: {
    user: {
      loggedIn: false,
      data: null,
    },
  },

  getters: {
    user(state) {
      return state.user;
    },
  },

  mutations: {
    SET_LOGGED_IN(state, value) {
      state.user.loggedIn = value;
    },
    SET_USER(state, data) {
      state.user.data = data;
    },
  },

  actions: {
    async register(context, { user }) {
      setRegister(user)
        .then(() => {
          context.commit("SET_USER", Response);
          console.log("Registration completed");
        })
        .catch((error) => {
          const errorCode = error.code;
          const errorMessage = error.message;
          console.log(errorCode);
          console.log(errorMessage);
        });
    },

    async login(context, { user }) {
      checkLogin(user)
        .then(() => {
          context.commit("SET_USER", Response);
          context.commit("SET_LOGGED_IN", true);
        })
        .catch((error) => {
          const errorCode = error.code;
          const errorMessage = error.message;
          console.log(errorCode);
          console.log(errorMessage);
        });
    },

    async logout(context) {
      //need to add api call to log out
      context.commit("SET_USER", null);
      context.commit("SET_LOGGED_IN", false);
    },
  },
});

export default store;
