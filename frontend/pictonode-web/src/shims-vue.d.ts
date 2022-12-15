// This file is a slightly modified version of https://github.com/microsoft/TypeScript-Vue-Starter/blob/master/src/vue-shims.d.ts

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
