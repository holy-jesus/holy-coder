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
    <!--tslint:disable-->
    <div class="start-button h-full w-[99px] flex-shrink-0 flex flex-row items-center justify-center pr-3 select-none"
        @mousedown="mousedown()"
        :style="{ 'background-image': pressed ? 'url(/src/assets/startbuttonpressed.webp)' : '' }">
        <img src="/src/assets/startbuttonflag.webp" class="sshadow h-[22px]" />
        <div class="sshadow text-white text-lg font-semibold italic h-[32px]" style="font-stretch: 50%;">пуск</div>

    </div>
    <!--tslint:enable-->
</template>

<style lang="css" scoped>
.start-button {
    font-family: "Tahoma", "Windows XP Tahoma", ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    background-image: url(/src/assets/startbuttondefault.webp);
}

.start-button:hover {
    background-image: url(/src/assets/startbuttonhover.webp)
}

.sshadow {
    filter: drop-shadow(rgba(0, 0, 0, 0.5) 1px 1px 1px);
}
</style>