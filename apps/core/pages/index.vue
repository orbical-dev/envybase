<script setup lang="ts">

import Navbar from "~/components/Navbar.vue";
</script>

<template>
  <div class="body text-white flex flex-col min-h-screen">
  <NuxtLayout>
    <NuxtPage />
    <Navbar></Navbar>
  </NuxtLayout>
  </div>
</template>

<style scoped>

</style>
