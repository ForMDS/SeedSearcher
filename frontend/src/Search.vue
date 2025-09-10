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
  <div class="page">
    <h1>种子批量搜索</h1>
    
    <p class="desc">
      设置种子范围和筛选条件，搜索满足所有条件的种子。启用的条件必须同时满足才会被筛选出来。
    </p>

    <div class="form">
      <!-- 种子范围 -->
      <div class="section">
        <h3>种子范围</h3>
        <label>
          起始种子：
          <input type="number" v-model.number="seedStart" />
        </label>
        <label>
          搜索数量：
          <input type="number" v-model.number="seedRange" max="1000" />
        </label>
      </div>

      <!-- 天气筛选 -->
      <div class="section">
        <h3>
          <input type="checkbox" v-model="enableWeather" id="weather" />
          <label for="weather">天气筛选</label>
        </h3>
        <div v-if="enableWeather" class="sub-form">
          <label>开始日：<input type="number" v-model.number="weatherStart" /></label>
          <label>结束日：<input type="number" v-model.number="weatherEnd" /></label>
          <label>最少天数：<input type="number" v-model.number="weatherMinCount" /></label>
          <label class="full">天气类型：<input type="text" v-model="weatherTargets" placeholder="Rain,Storm" /></label>
        </div>
      </div>

      <!-- 矿井筛选 -->
      <div class="section">
        <h3>
          <input type="checkbox" v-model="enableMines" id="mines" />
          <label for="mines">矿井筛选</label>
        </h3>
        <div v-if="enableMines" class="sub-form">
          <label>开始日：<input type="number" v-model.number="minesStartDay" /></label>
          <label>结束日：<input type="number" v-model.number="minesEndDay" /></label>
          <label>起始层：<input type="number" v-model.number="floorStart" /></label>
          <label>结束层：<input type="number" v-model.number="floorEnd" /></label>
          <label class="checkbox">
            <input type="checkbox" v-model="requireNoInfested" />
            要求无怪物层
          </label>
        </div>
      </div>

      <!-- 宝箱筛选 -->
      <div class="section">
        <h3>
          <input type="checkbox" v-model="enableChests" id="chests" />
          <label for="chests">宝箱筛选</label>
        </h3>
        <div v-if="enableChests" class="sub-form">
          <label>层数：<input type="number" v-model.number="chestLevel" /></label>
          <label>物品：<input type="text" v-model="chestItem" placeholder="磁铁戒指" /></label>
          <label>
            模式：
            <select v-model="chestRulesMode">
              <option value="ALL">全部满足</option>
              <option value="ANY">任一满足</option>
            </select>
          </label>
        </div>
      </div>

      <!-- 沙漠节筛选 -->
      <div class="section">
        <h3>
          <input type="checkbox" v-model="enableDesert" id="desert" />
          <label for="desert">沙漠节筛选</label>
        </h3>
        <div v-if="enableDesert" class="sub-form">
          <label class="checkbox">
            <input type="checkbox" v-model="requireLeah" />
            要求 Leah 出现
          </label>
          <label class="checkbox">
            <input type="checkbox" v-model="requireJas" />
            要求 Jas 出现
          </label>
        </div>
      </div>

      <button :disabled="loading" @click="searchSeeds" class="search-btn">
        {{ loading ? '搜索中...' : '开始搜索' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result">
      <div class="summary">
        <h3>搜索结果</h3>
        <p>
          种子范围：{{ result.seed_start }} - {{ result.seed_start + result.seed_range }}<br>
          检查总数：{{ result.total_checked }}<br>
          <strong>命中数量：{{ result.hit_count }}</strong>
        </p>
        
        <div class="conditions">
          <span>启用条件：</span>
          <span v-if="result.conditions.weather" class="tag">天气</span>
          <span v-if="result.conditions.mines" class="tag">矿井</span>
          <span v-if="result.conditions.chests" class="tag">宝箱</span>
          <span v-if="result.conditions.desert" class="tag">沙漠节</span>
          <span v-if="result.conditions.saloon" class="tag">垃圾桶</span>
          <span v-if="result.conditions.night_event" class="tag">夜间事件</span>
        </div>
      </div>

      <div v-if="result.hit_seeds.length" class="seeds">
        <h4>命中种子列表：</h4>
        <div class="seed-list">
          <span v-for="seed in result.hit_seeds" :key="seed" class="seed">{{ seed }}</span>
        </div>
      </div>
      
      <div v-else class="no-results">
        <p>没有找到满足所有条件的种子，请尝试：</p>
        <ul>
          <li>放宽筛选条件</li>
          <li>扩大种子搜索范围</li>
          <li>减少启用的筛选项</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 1000px;
  margin: 24px auto;
  padding: 0 16px;
}
.desc { color: #666; margin-bottom: 24px; }

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.section {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
}

.section h3 {
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sub-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.sub-form label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sub-form label.full {
  grid-column: 1 / -1;
}

.sub-form label.checkbox {
  justify-self: start;
}

.sub-form input, .sub-form select {
  flex: 1;
  padding: 6px 8px;
  min-width: 100px;
}

.search-btn {
  padding: 12px 24px;
  background: #007acc;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.search-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  color: #c00;
  background: #ffe6e6;
  padding: 12px;
  border-radius: 6px;
  margin: 12px 0;
}

.result {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
}

.summary h3 {
  margin: 0 0 12px 0;
  color: #333;
}

.conditions {
  margin-top: 12px;
}

.tag {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 0 4px;
  font-size: 12px;
}

.seeds h4 {
  margin: 16px 0 8px 0;
}

.seed-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.seed {
  background: #f0f8ff;
  border: 1px solid #b3d9ff;
  padding: 6px 10px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: bold;
  color: #0066cc;
}

.no-results {
  margin-top: 16px;
  padding: 16px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
}

.no-results ul {
  margin: 8px 0 0 20px;
}
</style>
