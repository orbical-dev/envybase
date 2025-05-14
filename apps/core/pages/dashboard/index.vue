<script setup lang="ts">

import Navbar from "~/components/Navbar.vue";
</script>

<template>
  <body class="text-white flex flex-col min-h-screen">
  <NuxtLayout>
    <NuxtPage />
    <Navbar></Navbar>
    <div class="content">
    <h1 class="text-4xl">Dashboard</h1>
    <p class="">Hi</p>
    </div>
  </NuxtLayout>
  </body>
</template>

<style scoped>
  body {
    background-color: #212121;
  }
  .content {
    margin: 1.5rem;
  }
</style>
