<script setup lang="ts">
defineProps({ id: String, icon: String, name: String })

</script>

<template>
    <div class="absolute max-w-20 flex flex-col justify-center items-center select-none gap-1" draggable="true">
        <img class="slight-shadow h-8" :src="icon" draggable="false">
        <div class="slight-shadow text-white text-[16px] text-center leading-4">{{ name }}</div>
    </div>
</template>