<script setup lang="ts">

function mousedown() {
    console.log("I'm being clicked")
}

</script>

<template>
    <div class="window" style="width: 300px">
        <div class="title-bar">
            <div class="title-bar-text">A Window With Stuff In It</div>
            <div class="title-bar-controls">
                <button aria-label="Minimize"></button>
                <button aria-label="Maximize"></button>
                <button aria-label="Close"></button>
            </div>
        </div>
        <div class="window-body">
            <p>There's so much room for activities!</p>
        </div>
    </div>
</template>

<style lang="css" scoped></style>