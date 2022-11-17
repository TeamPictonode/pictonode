<!-- GNU AGPL v3 License -->

<script lang="ts">
import { CSSProperties, defineComponent } from "vue";
import { Connection, Edge, NodeProps, Handle, Position } from "@vue-flow/core";

export default defineComponent({
    components: { Handle },
    data: () => ({
        Position,
        targetHandleStyleA: {
            top: '10px',
        },
        targetHandleStyleB: {
            bottom: '10px',
            top: 'auto',
        },
        sourceHandleStyle: {
            background: '#555',
        }
    }),
    inheritAttrs: false,
});
</script>

<template>
    <Handle 
        type="target" 
        id="top"
        :position="Position.Left"
        :style="targetHandleStyleA"
    />
    <Handle
        type="target"
        id="bottom"
        :position="Position.Left"
        :style="targetHandleStyleB"
    />
    <div class="theNode">
        <p>Composite Images</p>
    </div> 
    <Handle
        type="source"
        id="output"
        :position="Position.Right"
        :style="sourceHandleStyle"
    />
</template>

<style>
.theNode {
    background: #555;
    border-radius: 5px;
    color: #fff;
    padding: 10px;
    text-align: center;
    border: 1px solid #333;
}
</style>