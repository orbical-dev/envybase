<script setup lang="ts">

</script>

<template>
<div class="navbar">
  <ul class="list-none">
    <li><a href="/"><img src="https://raw.githubusercontent.com/orbical-dev/.github/refs/heads/main/envybase-logo.png" alt="Envybase Logo" width="40px" height="40px" /></a></li>
    <li><a href="/services">Services</a></li>
  </ul>
</div>
</template>

<style scoped>
  .navbar {
    border: 2px solid black;
    padding: 10px;
    border-radius: 20px;
  }
  .navbar ul {
    @apply flex;
  }
  .navbar ul li {
    padding-inline: 4px;
  }
  .navbar ul li a img {
    border-radius: 50%;
  }
  .navbar ul li a {

  }
</style>