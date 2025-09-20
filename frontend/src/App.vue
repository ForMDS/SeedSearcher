<script setup></script>

<template>
  <el-container class="app-container">
    <el-container class="main-container">
      <el-header>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/weather-forecast">天气预测</RouterLink>
      </el-header>
      <el-container>
        <RouterView />
      </el-container>
    </el-container>
    <el-footer>
      页脚信息 SeedSearcher © 2024 Created
    </el-footer>
  </el-container>
</template>

<style scoped lang="scss">
.app-container {
  .main-container {
    height: 100vh;
  }
}
</style>
