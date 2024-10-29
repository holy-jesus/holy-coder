<script setup lang="ts">
import { ref } from "vue";

const currentTime = ref("")

function updateTime() {
    const time = new Date();
    currentTime.value = `${time.getHours()}:${time.getMinutes().toString().padStart(2, '0')}`
}

updateTime()

setInterval(() => {
    updateTime()
}, 1000);
</script>

<template>
    <div class="flex items-center task-bar-tray h-full pl-6 pr-3 select-none"
        style="background-image: url(/src/assets/taskbartray.webp); background-size: cover;">
        <div class="text-white" style="font-size: 16px; font-smooth: none; contain: paint;">{{ currentTime }}</div>
    </div>
</template>

<style lang="css" scoped></style>