<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps({
  error: Object as () => NuxtError
})

const handleError = () => clearError({ redirect: '/' })
const getErrorMessage = (statusCode) => {
  const messages = {
  }
  return messages[statusCode] || 'An error occurred'
}

const getErrorDescription = (statusCode) => {
  const descriptions = {
  }
  return descriptions[statusCode] || 'We apologize for the inconvenience.'
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <div class="bg-[#151515] p-8 rounded-lg shadow-lg max-w-lg w-full text-center">
        <h1 class="text-5xl font-bold mb-4">{{ error.statusCode }}</h1>
        <p class="text-xl mb-6">{{ error.message || getErrorMessage(error.statusCode) }}</p>
        <p class="mb-8 text-gray-400">{{ getErrorDescription(error.statusCode) }}</p>
        <button
            @click="handleError"
            class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200">
          Return to Home
        </button>
      </div>
    </div>
</template>
