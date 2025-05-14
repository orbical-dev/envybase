<script setup lang="ts">

import Navbar from "~/components/Navbar.vue";
</script>

<template>
  <body class="text-white flex flex-col min-h-screen">
  <NuxtLayout>
    <NuxtPage />
    <Navbar></Navbar>
  </NuxtLayout>
  </body>
</template>

<style scoped>

</style>
