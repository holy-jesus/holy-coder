<script setup lang="ts">
import { ref } from "vue";

const hover = ref(false);
const pressed = ref(false);
</script>

<template>
    <div class="h-full w-[99px] overflow-hidden" @mouseover="hover = true" @mouseleave="hover = false"
        @mousedown="pressed = !pressed">
        <TransitionGroup name="startbuttonbackground">
            <div class="absolute h-full w-[99px]" style="background-image: url(/src/assets/startbuttondefault.png);">
            </div>
            <div class="absolute h-full w-[99px]" style="background-image: url(/src/assets/startbuttonhover.png);"
                v-if="hover && !pressed">
            </div>
            <div class="absolute h-full w-[99px]" style="background-image: url(/src/assets/startbuttonpressed.png);"
                v-if="pressed">
            </div>
        </TransitionGroup>
    </div>
</template>

<style lang="css" scoped>
.startbuttonbackground-enter-active,
.startbuttonbackground-leave-active {
    transition: opacity 0.1s ease;
}

.startbuttonbackground-enter-from,
.startbuttonbackground-leave-to {
    opacity: 0;
}
</style>