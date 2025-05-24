<template>
  <div>
    <NuxtRouteAnnouncer />
    <Navbar />
  </div>
</template>

<script setup>
onMounted(() => {
  const colorMode = useColorMode()

  watchEffect(() => {
    if (colorMode.preference === 'dark') {
      document.documentElement.style.setProperty('--bg-color', '#212121')
    } else {
      document.documentElement.style.setProperty('--bg-color', '#f5f5f5')
    }
  })
})
</script>