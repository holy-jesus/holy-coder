<script setup lang="ts">
import StartButton from "./StartButton.vue"


</script>

<template>
    <div class="task-bar w-screen">
        <StartButton />
    </div>
</template>

<style scoped>
.task-bar {
    font-family: "Trebuchet MS";
    background-image: url("/src/assets/taskbarbackground.png");
    background-size: contain;
    
    font-size: 13px;
    height: 31px;
}
</style>