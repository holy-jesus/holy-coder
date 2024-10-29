<script setup lang="ts">
import StartButton from "./StartButton.vue"
import TaskBarApps from "./TaskBarApps.vue";
import TaskBarTray from "./TaskBarTray.vue";


</script>

<template>
    <div class="task-bar w-screen flex flex-row">
        <StartButton />
        <TaskBarApps />
        <TaskBarTray />
    </div>
</template>

<style scoped>
.task-bar {
    background-image: url("/src/assets/taskbarbackground.webp");
    background-size: contain;
    font-size: 13px;
    height: 31px;
}
</style>