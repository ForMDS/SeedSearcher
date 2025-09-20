<script setup>
import { ref } from 'vue'
import http from '@/utils/http.js'

// 种子范围
const seedStart = ref(0)
const seedRange = ref(100)

// 天气筛选
const enableWeather = ref(false)
const weatherStart = ref(1)
const weatherEnd = ref(28)
const weatherMinCount = ref(5)
const weatherTargets = ref('Rain,Storm')

// 矿井筛选
const enableMines = ref(false)
const minesStartDay = ref(5)
const minesEndDay = ref(5)
const floorStart = ref(1)
const floorEnd = ref(85)
const requireNoInfested = ref(true)

// 宝箱筛选
const enableChests = ref(false)
const chestRulesMode = ref('ALL')
const chestLevel = ref(20)
const chestItem = ref('磁铁戒指')

// 沙漠节筛选
const enableDesert = ref(false)
const requireLeah = ref(false)
const requireJas = ref(false)

const loading = ref(false)
const error = ref('')
const result = ref(null)

async function searchSeeds() {
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const payload = {
      seed_start: Number(seedStart.value),
      seed_range: Number(seedRange.value),

      enable_weather: enableWeather.value,
      weather_clauses: enableWeather.value ? [{
        start: Number(weatherStart.value),
        end: Number(weatherEnd.value),
        min_count: Number(weatherMinCount.value)
      }] : [],
      weather_targets: enableWeather.value && weatherTargets.value ?
        weatherTargets.value.split(',').map(s => s.trim()).filter(Boolean) : [],

      enable_mines: enableMines.value,
      mines_start_day: Number(minesStartDay.value),
      mines_end_day: Number(minesEndDay.value),
      floor_start: Number(floorStart.value),
      floor_end: Number(floorEnd.value),
      require_no_infested: requireNoInfested.value,

      enable_chests: enableChests.value,
      chest_rules_mode: chestRulesMode.value,
      chest_rules: enableChests.value && chestLevel.value && chestItem.value ?
        [[Number(chestLevel.value), String(chestItem.value)]] : [],

      enable_desert: enableDesert.value,
      require_leah: requireLeah.value,
      require_jas: requireJas.value,
    }

    const res = await http.post('/api/search', payload)
    result.value = res
  } catch (e) {
    error.value = e?.response?.data?.message || e?.message || '搜索失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-aside width="400px">
    
  </el-aside>
  <el-main>Main</el-main>
</template>

<style scoped lang="scss"></style>
