<script setup>
import http from '@/utils/http.js'

http.post('/api/weather', {
  "seed": 12345,
  "clauses": [
    { "start": 1, "end": 28, "min_count": 5 }
  ],
  "targets": ["Rain", "Storm"]
}).then(res => {
  console.log(res)
})
</script>

<template>
  
</template>

<style scoped>

</style>
