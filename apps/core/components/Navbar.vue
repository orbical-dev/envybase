<template>
  <nav class="bg-[#151515] shadow-lg p-4">
    <div class="container mx-auto flex items-center justify-between">
      <NuxtLink to="/" class="text-white text-xl font-bold">
        Envybase
      </NuxtLink>
      <ul class="flex space-x-6">
        <li>
          <NuxtLink to="/dashboard" class="text-gray-300 hover:text-white transition">
            Dashboard
          </NuxtLink>
        </li>
        <li>
          <NuxtLink to="/services" class="text-gray-300 hover:text-white transition">
            Services
          </NuxtLink>
        </li>
      </ul>
    <NuxtLink to="/login" class="bg-white text-[#151515] px-4 py-2 rounded-lg shadow-md hover:bg-gray-200 transition">Login</NuxtLink>
    </div>
  </nav>
</template>

<script setup>
// No additional script needed for basic navbar.
</script>

<style>
/* Scoped styles if needed */
</style>
