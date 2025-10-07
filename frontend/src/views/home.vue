<script setup>
import { ref } from 'vue'
import { Delete, QuestionFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http from '@/utils/http.js'

const seedForm = ref(null)
const loading = ref(false)
const params = ref({
  use_legacy: true,
  seed_start: 0,
  seed_range: 1000,
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
  // 矿井
  enable_mines: false,
  mines_start_day: 5,
  mines_end_day: 5,
  floor_start: 1,
  floor_end: 85,
  _require_no_infested: 1,
  require_no_infested: true,
  // 宝箱筛选
  enable_chests: false,
  chest_rules_mode: 'ALL', // ALL / ANY
  chest_rules: [],
  // 沙漠节筛选
  enable_desert: false,
  require_leah: true, // 是否需要莉亚
  require_jas: true, // 是否需要贾斯
  // 酒吧垃圾桶筛选
  enable_saloon: false,
  saloon_start_day: 1,
  saloon_end_day: 7,
  saloon_daily_luck: -0.1,
  saloon_has_book: false,
  saloon_require_min_hit: 1,
  // 夜间事件
  enable_night_event: false,
  night_check_day: 1,
  night_greenhouse_unlocked: false,
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
        if (!isNaN(endValue) && (endValue - num) > 5000) {
          callback(new Error('种子范围不能超过5000'))
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
        if (!isNaN(startValue) && (num - startValue) > 5000) {
          callback(new Error('种子范围不能超过5000'))
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

// 宝箱楼层配置
const chestLevels = [10, 20, 50, 60, 70, 80, 90, 110, 120]

// 宝箱物品配置（根据楼层）
const chestItems = {
  10: ['皮靴', '工作靴', '木剑', '铁制短剑', '疾风利剑', '股骨'],
  20: ['钢制轻剑', '木棒', '精灵之刃', '光辉戒指', '磁铁戒指'],
  50: ['冻土靴', '热能靴', '战靴', '镀银军刀', '海盗剑'],
  60: ['水晶匕首', '弯刀', '铁刃', '飞贼之胫', '木锤'],
  70: ['圣堂之刃'],
  80: ['蹈火者靴', '黑暗之靴', '双刃大剑', '圣堂之刃', '长柄锤', '暗影匕首'],
  90: ['黑曜石之刃', '淬火阔剑', '蛇形邪剑', '骨剑', '骨化剑'],
  110: ['太空之靴', '水晶鞋', '钢刀', '巨锤'],
  120: ['骷髅钥匙']
}

// 宝箱预设模板
const chestPresets = [
  {
    name: '20层磁铁戒指',
    description: '获取20层的磁铁戒指',
    mode: 'ALL',
    rules: [
      { type: 'atom', level: 20, item: '磁铁戒指' }
    ]
  },
  {
    name: '80+110层双套装',
    description: '(80层=长柄锤 且 110层=太空之靴) 或 (80层=蹈火者靴 且 110层=巨锤)',
    mode: 'ALL',
    rules: [
      {
        type: 'or_group',
        items: [
          [
            { level: 80, item: '长柄锤' },
            { level: 110, item: '太空之靴' }
          ],
          [
            { level: 80, item: '蹈火者靴' },
            { level: 110, item: '巨锤' }
          ]
        ]
      }
    ]
  },
  {
    name: '完整配置示例',
    description: '20层=磁铁戒指 且 (80+110层双套装)',
    mode: 'ALL',
    rules: [
      { type: 'atom', level: 20, item: '磁铁戒指' },
      {
        type: 'or_group',
        items: [
          [
            { level: 80, item: '长柄锤' },
            { level: 110, item: '太空之靴' }
          ],
          [
            { level: 80, item: '蹈火者靴' },
            { level: 110, item: '巨锤' }
          ]
        ]
      }
    ]
  }
]

function handleSeedRangeBlur() {
  const form = seedForm.value
  if (form) {
    form.validateField('seed_start')
    form.validateField('seed_range')
  }
}

function addWeatherClause() {
  if (params.value.weather_clauses.length >= 5) {
    ElMessage.error('最多只能添加5个天气筛选条件')
    return
  }
  params.value.weather_clauses.push({ start: 1, end: 28, min_count: 5 })
}

function handleNoInfestedChange(val) {
  params.value.require_no_infested = val === 1
}

// 宝箱规则相关函数
function addSimpleChestRule() {
  params.value.chest_rules.push({
    type: 'atom',
    level: 20,
    item: '磁铁戒指'
  })
}

function addOrGroupChestRule() {
  params.value.chest_rules.push({
    type: 'or_group',
    items: [
      [{ level: 80, item: '长柄锤' }]
    ]
  })
}

function removeChestRule(index) {
  params.value.chest_rules.splice(index, 1)
}

function addAndSubGroup(rule) {
  if (rule.type === 'or_group') {
    rule.items.push([{ level: 80, item: '长柄锤' }])
  }
}

function removeAndSubGroup(rule, subIndex) {
  if (rule.type === 'or_group' && rule.items.length > 1) {
    rule.items.splice(subIndex, 1)
  }
}

function addAtomToSubGroup(subGroup) {
  subGroup.push({ level: 80, item: '长柄锤' })
}

function removeAtomFromSubGroup(subGroup, atomIndex) {
  if (subGroup.length > 1) {
    subGroup.splice(atomIndex, 1)
  }
}

function applyChestPreset(preset) {
  params.value.chest_rules_mode = preset.mode
  params.value.chest_rules = JSON.parse(JSON.stringify(preset.rules))
  ElMessage.success(`已应用预设：${preset.name}`)
}

function getItemsByLevel(level) {
  return chestItems[level] || []
}

// 楼层变更处理函数 - 检查并清空不匹配的物品选择
function handleLevelChange(rule, newLevel) {
  if (rule.item) {
    // 检查当前选择的物品是否在新楼层的物品列表中
    const newItems = getItemsByLevel(newLevel)
    if (!newItems.includes(rule.item)) {
      // 如果当前物品不在新楼层的列表中，清空选择
      rule.item = ''
      ElMessage.info('楼层已变更，请重新选择物品')
    }
  }
}

function handleAtomLevelChange(atom, newLevel) {
  if (atom.item) {
    const newItems = getItemsByLevel(newLevel)
    if (!newItems.includes(atom.item)) {
      atom.item = ''
      ElMessage.info('楼层已变更，请重新选择物品')
    }
  }
}

function validateChestRules() {
  if (!params.value.enable_chests) return true

  if (params.value.chest_rules.length === 0) {
    ElMessage.error('请至少添加一个宝箱规则')
    return false
  }

  // 收集所有使用的楼层（注意：不同顶层规则可以使用相同楼层）
  // 只检查规则本身的有效性
  for (const rule of params.value.chest_rules) {
    if (rule.type === 'atom') {
      if (!rule.level || !rule.item) {
        ElMessage.error('简单条件必须选择楼层和物品')
        return false
      }
    } else if (rule.type === 'or_group') {
      if (!rule.items || rule.items.length === 0) {
        ElMessage.error('OR 组至少需要一个 AND 子组')
        return false
      }
      for (const subGroup of rule.items) {
        if (subGroup.length === 0) {
          ElMessage.error('AND 子组至少需要一个条件')
          return false
        }
        for (const atom of subGroup) {
          if (!atom.level || !atom.item) {
            ElMessage.error('所有条件必须选择楼层和物品')
            return false
          }
        }
      }
    }
  }

  return true
}

// 转换前端数据格式为后端格式
function formatChestRulesForBackend(rules) {
  return rules.map(rule => {
    if (rule.type === 'atom') {
      // 简单条件: { type: 'atom', level: 20, item: '磁铁戒指' } -> [20, '磁铁戒指']
      return [rule.level, rule.item]
    } else if (rule.type === 'or_group') {
      // OR 组: { type: 'or_group', items: [[{level, item}]] } -> [[[level, item]]]
      return rule.items.map(subGroup =>
        subGroup.map(atom => [atom.level, atom.item])
      )
    }
    return rule
  })
}

function searchSeeds() {
  const form = seedForm.value
  if (!form) return
  form.validate(async (valid) => {
    if (!valid) return

    // 验证宝箱规则
    if (!validateChestRules()) return

    try {
      // 准备请求数据
      const requestData = { ...params.value }

      // 格式化天气筛选数据
      if (requestData.enable_weather && requestData.weather_clauses.length) {
        requestData.weather_clauses.forEach(item => {
          item.start = Number(item.start)
          item.end = Number(item.end)
          item.min_count = Number(item.min_count)
        })
      }

      // 格式化宝箱筛选数据
      if (requestData.enable_chests && requestData.chest_rules.length) {
        requestData.chest_rules = formatChestRulesForBackend(requestData.chest_rules)
      }

      loading.value = true
      const res = await http.post('/api/search', requestData)
      console.log('搜索结果：', res)
      // ElMessage.success(`搜索完成！找到 ${res.data?.results?.length || 0} 个符合条件的种子`)
    } catch (error) {
      const errorMsg = error?.response?.data?.message || error?.message || '搜索失败'
      ElMessage.error(errorMsg)
      console.error('搜索错误：', error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <el-container>
    <el-aside width="600px">
      <el-form :model="params" :rules="rules" ref="seedForm">
        <el-form-item label="是否启用旧随机：">
          <el-switch v-model="params.use_legacy" disabled />
        </el-form-item>
        <el-form-item label="种子范围：">
          <div class="flex-c">
            <el-form-item prop="seed_start" style="margin-bottom: 0;">
              <el-input v-model="params.seed_start" style="width: 150px;" placeholder="开始值"
                @blur="handleSeedRangeBlur" />
            </el-form-item>
            <span class="connectors">至</span>
            <el-form-item prop="seed_range" style="margin-bottom: 0;">
              <el-input v-model="params.seed_range" style="width: 150px;" placeholder="结束值"
                @blur="handleSeedRangeBlur" />
            </el-form-item>
          </div>
        </el-form-item>
        <el-form-item label="天气筛选：">
          <el-switch v-model="params.enable_weather" />
          <el-button text type="primary" @click="addWeatherClause" v-if="params.enable_weather"
            class="mgl-8">添加筛选条件</el-button>
        </el-form-item>
        <div v-if="params.enable_weather" class="filter-card weather-clauses">
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
                <el-form-item label="开始日" class="clause-field">
                  <el-input v-model="clause.start" style="width: 80px;" placeholder="1"></el-input>
                </el-form-item>
                <span class="clause-separator">至</span>
                <el-form-item label="结束日" class="clause-field">
                  <el-input v-model="clause.end" style="width: 80px;" placeholder="28"></el-input>
                </el-form-item>
                <el-form-item label="最少天数" class="clause-field">
                  <div class="input-with-suffix">
                    <el-input v-model="clause.min_count" style="width: 80px;" placeholder="5"></el-input>
                    <span class="field-suffix">天</span>
                  </div>
                </el-form-item>
              </div>
            </div>
          </div>
        </div>
        <el-form-item label="矿井筛选：">
          <el-switch v-model="params.enable_mines" />
        </el-form-item>
        <div v-if="params.enable_mines" class="filter-card mines-clauses">
          <el-checkbox v-model="params._require_no_infested" label="要求‘完全没有怪物/史莱姆层’" :true-value="1" :false-value="0"
            @change="handleNoInfestedChange" />
          <div class="flex-c align-base">
            <el-form-item label="开始日" style="margin-bottom: 0;">
              <el-input v-model="params.mines_start_day" style="width: 80px;" placeholder="开始日"></el-input>
            </el-form-item>
            <span class="connectors">至</span>
            <el-form-item label="结束日" style="margin-bottom: 0;">
              <el-input v-model="params.mines_end_day" style="width: 80px;" placeholder="结束日"></el-input>
            </el-form-item>
            <el-form-item label="起始层" style="margin-bottom: 0;" class="mgl-8">
              <el-input v-model="params.floor_start" style="width: 80px;" placeholder="起始层"></el-input>
            </el-form-item>
            <span class="connectors">至</span>
            <el-form-item label="结束层" style="margin-bottom: 0;">
              <el-input v-model="params.floor_end" style="width: 80px;" placeholder="结束层"></el-input>
            </el-form-item>
          </div>
        </div>
        <el-form-item label="宝箱筛选：">
          <el-switch v-model="params.enable_chests" />
        </el-form-item>
        <div v-if="params.enable_chests" class="filter-card chests-clauses">
          <!-- 预设模板 -->
          <div class="preset-section">
            <div class="section-title">
              <span>快速选择预设</span>
              <el-tooltip content="点击应用预设配置" placement="top">
                <el-icon :size="16" style="margin-left: 4px; color: #909399; cursor: pointer;">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
            <div class="preset-list">
              <div v-for="(preset, index) in chestPresets" :key="index" class="preset-card"
                @click="applyChestPreset(preset)">
                <div class="preset-name">📦 {{ preset.name }}</div>
                <div class="preset-desc">{{ preset.description }}</div>
              </div>
            </div>
          </div>

          <el-divider />

          <!-- 自定义规则 -->
          <div class="custom-section">
            <div class="section-title">自定义规则</div>

            <el-form-item label="顶层模式：">
              <el-radio-group v-model="params.chest_rules_mode">
                <el-radio :value="'ALL'">全部满足 (AND)</el-radio>
                <el-radio :value="'ANY'">满足任一 (OR)</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 规则列表 -->
            <div class="rules-container">
              <div v-for="(rule, ruleIndex) in params.chest_rules" :key="ruleIndex" class="rule-card">
                <div class="rule-header">
                  <span class="rule-title">
                    规则 {{ ruleIndex + 1 }}
                    <el-tag :type="rule.type === 'atom' ? 'success' : 'warning'" size="small" style="margin-left: 8px;">
                      {{ rule.type === 'atom' ? '简单条件' : 'OR 组' }}
                    </el-tag>
                  </span>
                  <el-button link type="danger" @click="removeChestRule(ruleIndex)" size="small">
                    <el-icon>
                      <Delete />
                    </el-icon>
                    删除
                  </el-button>
                </div>

                <!-- 简单条件 (atom) -->
                <div v-if="rule.type === 'atom'" class="rule-content">
                  <el-form-item label="楼层" style="margin-bottom: 0;">
                    <el-select v-model="rule.level" placeholder="选择楼层" style="width: 100px;"
                      @change="(newLevel) => handleLevelChange(rule, newLevel)">
                      <el-option v-for="level in chestLevels" :key="level" :label="`${level}层`" :value="level" />
                    </el-select>
                  </el-form-item>
                  <span class="rule-separator">=</span>
                  <el-form-item label="物品" style="margin-bottom: 0;">
                    <el-select v-model="rule.item" placeholder="选择物品" style="width: 140px;">
                      <el-option v-for="item in getItemsByLevel(rule.level)" :key="item" :label="item" :value="item" />
                    </el-select>
                  </el-form-item>
                </div>

                <!-- OR 组 -->
                <div v-else-if="rule.type === 'or_group'" class="or-group-content">
                  <div v-for="(subGroup, subIndex) in rule.items" :key="subIndex" class="and-subgroup">
                    <div class="subgroup-header">
                      <span class="subgroup-title">AND 子组 {{ subIndex + 1 }}</span>
                      <el-button link type="danger" @click="removeAndSubGroup(rule, subIndex)"
                        v-if="rule.items.length > 1" size="small">
                        <el-icon>
                          <Delete />
                        </el-icon>
                      </el-button>
                    </div>

                    <div class="subgroup-atoms">
                      <div v-for="(atom, atomIndex) in subGroup" :key="atomIndex" class="atom-item">
                        <el-select v-model="atom.level" placeholder="楼层" style="width: 100px;"
                          @change="(newLevel) => handleAtomLevelChange(atom, newLevel)">
                          <el-option v-for="level in chestLevels" :key="level" :label="`${level}层`" :value="level" />
                        </el-select>
                        <span class="atom-separator">=</span>
                        <el-select v-model="atom.item" placeholder="物品" style="width: 140px;">
                          <el-option v-for="item in getItemsByLevel(atom.level)" :key="item" :label="item"
                            :value="item" />
                        </el-select>
                        <el-button link type="danger" @click="removeAtomFromSubGroup(subGroup, atomIndex)"
                          v-if="subGroup.length > 1" size="small" style="margin-left: 8px;">
                          <el-icon>
                            <Delete />
                          </el-icon>
                        </el-button>
                      </div>
                      <el-button text type="primary" @click="addAtomToSubGroup(subGroup)" size="small"
                        style="margin-top: 8px;">
                        + 添加条件
                      </el-button>
                    </div>
                  </div>

                  <el-button text type="primary" @click="addAndSubGroup(rule)" style="margin-top: 12px;">
                    + 添加 AND 子组
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 添加规则按钮 -->
            <div class="add-rule-buttons">
              <el-button @click="addSimpleChestRule" type="primary" plain>
                + 添加简单条件
              </el-button>
              <el-button @click="addOrGroupChestRule" type="warning" plain>
                + 添加 OR 组
              </el-button>
            </div>
          </div>
        </div>
        <el-form-item label="沙漠节筛选：">
          <el-switch v-model="params.enable_desert" />
        </el-form-item>
        <div v-if="params.enable_desert" class="filter-card desert-clauses">
          <el-checkbox v-model="params.require_leah" label='需要"莉亚"' />
          <el-checkbox v-model="params.require_jas" label='需要"贾斯"' />
        </div>
        <el-form-item label="酒吧垃圾桶筛选：">
          <el-switch v-model="params.enable_saloon" />
        </el-form-item>
        <div v-if="params.enable_saloon" class="filter-card saloon-clauses">
          <el-form-item label="检查日期范围：">
            <div class="flex-c align-base">
              <el-form-item label="开始" style="margin-bottom: 0;">
                <el-input-number v-model="params.saloon_start_day" :min="1" :max="112" :step="1"
                  controls-position="right" style="width: 120px;" />
              </el-form-item>
              <span class="connectors">至</span>
              <el-form-item label="结束" style="margin-bottom: 0;">
                <el-input-number v-model="params.saloon_end_day" :min="1" :max="112" :step="1" controls-position="right"
                  style="width: 120px;" />
              </el-form-item>
              <el-tooltip placement="top" effect="dark">
                <template #content>
                  1-28 = 春季<br />
                  29-56 = 夏季<br />
                  57-84 = 秋季<br />
                  85-112 = 冬季
                </template>
                <el-icon :size="16" style="margin-left: 8px; color: #909399; cursor: help;">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </el-form-item>

          <el-form-item label="运势值：">
            <div class="flex-c align-base">
              <el-slider v-model="params.saloon_daily_luck" :min="-0.1" :max="0.1" :step="0.01"
                :format-tooltip="(val) => val.toFixed(2)" style="width: 200px;" />
              <span class="value-display">{{ params.saloon_daily_luck.toFixed(2) }}</span>
              <el-tooltip placement="top" effect="dark">
                <template #content>
                  运势影响命中概率：<br />
                  -0.1（最低）→ 10% 基础概率<br />
                  0.0（中等）→ 20% 基础概率<br />
                  +0.1（最高）→ 30% 基础概率
                </template>
                <el-icon :size="16" style="margin-left: 8px; color: #909399; cursor: help;">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </el-form-item>

          <el-form-item label="垃圾之书：">
            <el-switch v-model="params.saloon_has_book" />
            <span class="field-tip">（已读书可使命中概率 +20%）</span>
          </el-form-item>

          <el-form-item label="至少命中天数：">
            <div class="flex-c align-base">
              <el-input-number v-model="params.saloon_require_min_hit" :min="1" :max="28" controls-position="right"
                style="width: 120px;" />
              <span class="field-unit">天</span>
              <el-tooltip placement="top" effect="dark">
                <template #content>
                  在指定日期范围内，至少几天能从<br />
                  酒吧垃圾桶获得"今日特供"才算合格
                </template>
                <el-icon :size="16" style="margin-left: 8px; color: #909399; cursor: help;">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </el-form-item>

          <div class="info-card">
            <div class="info-title">💡 功能说明</div>
            <div class="info-content">
              • <strong>筛选目标</strong>：只统计"今日特供 (Dish of the Day)"，其他物品不计入<br />
              • <strong>概率机制</strong>：基础 20% + 运势值 + (垃圾书 20%)<br />
              • <strong>日期范围</strong>：1-112 对应游戏内春夏秋冬四季（每季28天）<br />
              • <strong>推荐配置</strong>：春季前7天，运势 -0.1，已读书，至少命中 2 天
            </div>
          </div>
        </div>
        <el-form-item label="夜间事件：">
          <el-switch v-model="params.enable_night_event" />
        </el-form-item>
        <div v-if="params.enable_night_event" class="filter-card night-event-clauses">
          <el-form-item label="检查日期">
            <el-input-number v-model="params.night_check_day" :min="1" :max="28" :step="1" controls-position="right"
              style="width: 120px;" />
          </el-form-item>
          <el-form-item label="温室是否解锁：">
            <el-switch v-model="params.night_greenhouse_unlocked" />
          </el-form-item>
        </div>
        <el-form-item class="mgt-16">
          <el-button type="primary" @click="searchSeeds" :loading="loading">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-aside>
    <el-main>

    </el-main>
  </el-container>

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
.filter-card {
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.weather-clauses {
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

// 宝箱筛选样式
.chests-clauses {
  .preset-section {
    margin-bottom: 16px;

    .section-title {
      display: flex;
      align-items: center;
      font-weight: 500;
      font-size: 14px;
      color: #303133;
      margin-bottom: 12px;
    }

    .preset-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 12px;

      .preset-card {
        padding: 12px 16px;
        background: #667eea;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .preset-name {
          font-size: 15px;
          font-weight: 600;
          margin-bottom: 6px;
        }

        .preset-desc {
          font-size: 12px;
          opacity: 0.9;
          line-height: 1.4;
        }
      }
    }
  }

  .custom-section {
    .section-title {
      font-weight: 500;
      font-size: 14px;
      color: #303133;
      margin-bottom: 12px;
    }

    .rules-container {
      margin-top: 16px;
      margin-bottom: 16px;

      .rule-card {
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

        .rule-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid #f0f0f0;

          .rule-title {
            font-weight: 500;
            color: #303133;
            font-size: 14px;
            display: flex;
            align-items: center;
          }
        }

        .rule-content {
          display: flex;
          align-items: center;
          gap: 12px;

          .rule-separator {
            font-size: 16px;
            font-weight: 600;
            color: #409eff;
          }
        }

        .or-group-content {
          .and-subgroup {
            margin-bottom: 16px;
            padding: 12px;
            background-color: #fef9e7;
            border-radius: 6px;
            border: 1px solid #f9e79f;

            &:last-child {
              margin-bottom: 0;
            }

            .subgroup-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;

              .subgroup-title {
                font-size: 13px;
                font-weight: 500;
                color: #856404;
              }
            }

            .subgroup-atoms {
              .atom-item {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;

                &:last-child {
                  margin-bottom: 0;
                }

                .atom-separator {
                  font-size: 14px;
                  font-weight: 600;
                  color: #e67e22;
                }
              }
            }
          }
        }
      }
    }

    .add-rule-buttons {
      display: flex;
      gap: 12px;
      margin-top: 16px;
    }
  }
}

// 酒吧垃圾桶筛选样式
.saloon-clauses {
  .date-tip {
    font-size: 12px;
    color: #909399;
    margin-left: 12px;
  }

  .value-display {
    min-width: 50px;
    text-align: center;
    font-weight: 500;
    color: #409eff;
    margin-left: 12px;
  }

  .field-tip {
    font-size: 13px;
    color: #909399;
    margin-left: 12px;
  }

  .field-unit {
    font-size: 14px;
    color: #606266;
    margin-left: 8px;
  }

  .info-card {
    margin-top: 16px;
    padding: 12px 16px;
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
    border-radius: 8px;
    border-left: 4px solid #4caf50;

    .info-title {
      font-size: 14px;
      font-weight: 600;
      color: #2e7d32;
      margin-bottom: 8px;
    }

    .info-content {
      font-size: 13px;
      line-height: 1.8;
      color: #424242;

      strong {
        color: #1b5e20;
      }
    }
  }

  .el-slider {
    margin-right: 0;
  }
}
</style>
