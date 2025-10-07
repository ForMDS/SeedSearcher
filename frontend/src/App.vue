<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

</script>

<template>
  <el-scrollbar height="100vh">
    <el-container class="app-container">
      <el-container class="main-container">
        <el-header class="header">
          <el-button text type="primary" @click="router.replace('/')">种子搜索</el-button>
          <el-button text type="primary" @click="router.push('/weather-forecast')">天气预测</el-button>
        </el-header>
        <el-container class="router-view-container">
          <RouterView />
        </el-container>
      </el-container>
      <el-footer>
        页脚信息 SeedSearcher © 2025 Created
      </el-footer>
    </el-container>
  </el-scrollbar>
</template>

<style scoped lang="scss">
.app-container {
  .main-container {
    min-height: 100vh;
    background-color: #F2F3F5;
    .header {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding: 0 50px;
      background-color: #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      gap: 16px;
    }
    .router-view-container {
      padding: 20px 50px;
    }
  }
}
</style>
