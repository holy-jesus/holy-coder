<script setup lang="ts">
import { ref } from "vue";

const pressed = ref(false);

function mousedown() {
    pressed.value = !pressed.value
}

function preloadImages() {
    let image;
    for (image of ["/src/assets/startbuttonhover.webp", "/src/assets/startbuttonpressed.webp"]) {
        (new Image()).src = image;
    }
}

preloadImages()
</script>

<template>
    <div class="start-button h-full w-[99px] flex-shrink-0 flex flex-row items-center justify-center pr-3 select-none"
        @mousedown="mousedown()"
        :style="{ 'background-image': pressed ? 'url(/src/assets/start-button-pressed.webp)' : '' }">
        <img src="/src/assets/start-button-flag.webp" class="slight-shadow h-[22px]" />
        <div class="slight-shadow text-white text-lg font-semibold italic h-[32px]" style="font-stretch: 50%;">пуск
        </div>
    </div>
</template>

<style lang="css" scoped>
.start-button {
    font-family: "Tahoma", "Windows XP Tahoma", ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    background-image: url(/src/assets/start-button-default.webp);
}

.start-button:hover {
    background-image: url(/src/assets/start-button-hover.webp)
}
</style>