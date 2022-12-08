<!-- GNU AGPL v3 License -->
<script lang="ts">
import { defineComponent } from "vue";

function update(canvas: HTMLCanvasElement, img: HTMLCanvasElement | undefined) {
    const ctx = canvas.getContext("2d");
    if (ctx) {
        console.log(`got img: ${img}`);
        if (img) {
            console.log('drawing image');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        } else {
            ctx.fillStyle = "red";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
    }
}

export default defineComponent({
    props: ["img", "ticks"],
    mounted() {
        // @ts-ignore
        update(this.$refs.inner, this.img);
    },
    watch: {
        img() {
            // @ts-ignore
            update(this.$refs.inner, this.img);
        },
        ticks() {
            // This is a bogus hack, please fix!

            // @ts-ignore
            update(this.$refs.inner, this.img);
        }
    }
});
</script>

<template>
    <v-card ref="toplevel" class="mx-auto" id="rendered-view" tile>
        <p>Image View</p>
        <canvas ref="inner" width="200" height="100" />
    </v-card>
</template>

<style scoped lang="scss">
#rendered-view {
    padding: 1rem;
    margin: 1rem;
}
</style>
