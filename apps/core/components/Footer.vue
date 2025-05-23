
<template>
  <footer class="footer">
    <div class="container">
      <p>&copy; {{ currentYear }} The Envybase Team and its supporters/contributors</p>
    </div>
  </footer>
</template>

<script setup>
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.footer {
  padding: 1rem 0;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
  margin-top: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
}
</style>