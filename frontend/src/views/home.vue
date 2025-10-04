<script setup>
import { ref } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import http from '@/utils/http.js'

const seedForm = ref(null)
const loading = ref(false)
const params = ref({
  use_legacy: true,
  seed_start: 0,
  seed_range: 5000,
  // 天气
  enable_weather: false,
  weather_clauses: [
    {
      'start': 1,        // 开始日期（游戏内绝对天数）
      'end': 28,         // 结束日期（游戏内绝对天数）
      'min_count': 5     // 该区间内最少出现天数
    }
  ],
  weather_targets: ['Rain', 'Storm', 'Green Rain'],
})
const rules = ref({
  seed_start: [
    { required: true, message: '请输入种子开始值', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value === '' || value === null || value === undefined) {
          callback(new Error('种子开始值不能为空'))
          return
        }
        const num = Number(value)
        if (isNaN(num) || !Number.isInteger(num)) {
          callback(new Error('种子开始值必须是整数'))
          return
        }
        const endValue = Number(params.value.seed_range)
        if (!isNaN(endValue) && num >= endValue) {
          callback(new Error('种子开始值必须小于结束值'))
          return
        }
        if (!isNaN(endValue) && (endValue - num) > 1000000) {
          callback(new Error('种子范围不能超过1000000'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ],
  seed_range: [
    { required: true, message: '请输入种子结束值', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value === '' || value === null || value === undefined) {
          callback(new Error('种子结束值不能为空'))
          return
        }
        const num = Number(value)
        if (isNaN(num) || !Number.isInteger(num)) {
          callback(new Error('种子结束值必须是整数'))
          return
        }
        const startValue = Number(params.value.seed_start)
        if (!isNaN(startValue) && num <= startValue) {
          callback(new Error('种子结束值必须大于开始值'))
          return
        }
        if (!isNaN(startValue) && (num - startValue) > 1000000) {
          callback(new Error('种子范围不能超过1000000'))
          return
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
})
const weatherOptions = [
  { label: '雨天', value: 'Rain' },
  { label: '雷雨天', value: 'Storm' },
  { label: '绿雨天', value: 'Green Rain' },
  { label: '大风天', value: 'Wind' },
  { label: '雪天', value: 'Snow' },
  { label: '晴天', value: 'Sun' },
]

function handleSeedRangeBlur() {
  const form = seedForm.value
  if (form) {
    form.validateField('seed_start')
    form.validateField('seed_range')
  }
}

function searchSeeds() {
  const form = seedForm.value
  if (!form) return
  form.validate(async (valid) => {
    if (!valid) return
    try {
      if (params.value.enable_weather && params.value.weather_clauses.length) {
        params.value.weather_clauses.forEach(item => {
          item.start = Number(item.start)
          item.end = Number(item.end)
          item.min_count = Number(item.min_count)
        })
      }
      const res = await http.post('/api/search', params.value)
      console.log('搜索结果：', res)
    } catch (error) {
      error.value = error?.response?.data?.message || error?.message || '搜索失败'
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <el-form :model="params" :rules="rules" ref="seedForm">
    <el-form-item label="是否启用旧随机：">
      <el-switch v-model="params.use_legacy" disabled />
    </el-form-item>
    <el-form-item label="种子范围：">
      <div class="flex-c">
        <el-form-item prop="seed_start" style="margin-bottom: 0;">
          <el-input v-model="params.seed_start" style="width: 150px;" placeholder="开始值" @blur="handleSeedRangeBlur" />
        </el-form-item>
        <span class="connectors">至</span>
        <el-form-item prop="seed_range" style="margin-bottom: 0;">
          <el-input v-model="params.seed_range" style="width: 150px;" placeholder="结束值" @blur="handleSeedRangeBlur" />
        </el-form-item>
      </div>
    </el-form-item>
    <el-form-item label="筛选天气：">
      <el-switch v-model="params.enable_weather" />
      <el-button text type="primary" @click="params.weather_clauses.push({ start: 1, end: 28, min_count: 5 })"
        v-if="params.enable_weather" class="mgl-8">添加筛选条件</el-button>
    </el-form-item>
    <div v-if="params.enable_weather" class="weather-clauses">
      <el-form-item label="天气类型：">
        <el-checkbox-group v-model="params.weather_targets" class="weather-targets">
          <el-checkbox v-for="option in weatherOptions" :key="option.value" :label="option.label"
            :value="option.value" />
        </el-checkbox-group>
      </el-form-item>

      <div class="clauses-container">
        <div class="clause-item" v-for="(clause, index) in params.weather_clauses" :key="index">
          <div class="clause-header">
            <span class="clause-title">筛选条件 {{ index + 1 }}</span>
            <el-button link type="danger" @click="params.weather_clauses.splice(index, 1)"
              v-if="params.weather_clauses.length > 1" size="small">
              <el-icon>
                <Delete />
              </el-icon>
              删除
            </el-button>
          </div>

          <div class="clause-content">
            <el-form-item label="开始日：" class="clause-field">
              <el-input v-model="clause.start" style="width: 80px;" placeholder="1"></el-input>
            </el-form-item>
            <span class="clause-separator">至</span>
            <el-form-item label="结束日：" class="clause-field">
              <el-input v-model="clause.end" style="width: 80px;" placeholder="28"></el-input>
            </el-form-item>
            <el-form-item label="最少天数：" class="clause-field">
              <div class="input-with-suffix">
                <el-input v-model="clause.min_count" style="width: 80px;" placeholder="5"></el-input>
                <span class="field-suffix">天</span>
              </div>
            </el-form-item>
          </div>
        </div>
      </div>
    </div>
    <el-form-item class="mgt-16">
      <el-button type="primary" @click="searchSeeds">搜索</el-button>
    </el-form-item>
  </el-form>
</template>

<style scoped lang="scss">
.flex-c {
  display: flex;
  gap: 8px;

  &.align-base {
    align-items: baseline;
  }
}

.mgl-8 {
  margin-left: 8px;
}

.mgt-8 {
  margin-top: 8px;
}

.mgt-16 {
  margin-top: 16px;
}

.connectors {
  font-size: 14px;
  color: #606266;
}

// 天气筛选样式
.weather-clauses {
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;

  .weather-targets {
    .el-checkbox {
      margin-right: 16px;
      margin-bottom: 8px;
    }
  }

  .clauses-container {
    margin-top: 16px;
  }

  .clause-item {
    margin-bottom: 16px;
    padding: 16px;
    background-color: white;
    border-radius: 6px;
    border: 1px solid #dcdfe6;
    transition: all 0.3s ease;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
    }

    &:last-child {
      margin-bottom: 0;
    }

    .clause-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #f0f0f0;

      .clause-title {
        font-weight: 500;
        color: #303133;
        font-size: 14px;
      }

      .el-button {
        font-size: 12px;

        .el-icon {
          margin-right: 4px;
        }
      }
    }

    .clause-content {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;

      .clause-field {
        margin-bottom: 0;

        .input-with-suffix {
          display: flex;
          align-items: center;
          gap: 8px;

          .field-suffix {
            font-size: 14px;
            color: #909399;
            white-space: nowrap;
          }
        }
      }

      .clause-separator {
        font-size: 14px;
        color: #606266;
        margin: 0 4px;
      }
    }
  }
}
</style>
