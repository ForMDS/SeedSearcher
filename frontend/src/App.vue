<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 判断当前路由是否激活
const isRouteActive = (path) => {
  return route.path === path
}

// 回到首页
const goHome = () => {
  router.replace('/')
}

</script>

<template>
  <el-scrollbar height="100vh">
    <el-container class="app-container">
      <el-container class="main-container">
        <el-header class="header">
          <div class="header-left" @click="goHome">
            <div class="header-brand">
              <span class="brand-icon">🌱</span>
              <span class="brand-name">SeedSearcher</span>
            </div>
          </div>
          <div class="header-nav">
            <button class="nav-button" :class="{ active: isRouteActive('/') }" @click="router.replace('/')">
              种子搜索
            </button>
            <button class="nav-button" :class="{ active: isRouteActive('/weather-forecast') }"
              @click="router.push('/weather-forecast')">
              天气预测
            </button>
          </div>
        </el-header>
        <el-container class="router-view-container">
          <RouterView />
        </el-container>
      </el-container>
      <el-footer class="footer" height="auto">
        <div class="footer-content">
          <div class="footer-main">
            <div class="footer-logo">
              <span class="logo-icon">🌱</span>
              <span class="logo-text">SeedSearcher</span>
            </div>
            <div class="footer-info">
              <span class="info-text">星露谷物语种子搜索工具</span>
              <span class="separator">•</span>
              <span class="info-text">Stardew Valley Seed Finder</span>
            </div>
          </div>
          <div class="footer-bottom">
            <div class="copyright">
              © 2025 SeedSearcher. All rights reserved.
            </div>
            <div class="footer-links">
              <a href="https://www.stardewvalley.net/" target="_blank" class="footer-link">
                <span class="link-icon">🎮</span>
                官网
              </a>
              <!-- <span class="separator">|</span>
              <span class="version">v1.0.0</span> -->
            </div>
          </div>
        </div>
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
      justify-content: space-between;
      padding: 0 50px;
      background-color: #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      height: 64px;

      .header-left {
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: transform 0.3s ease;

        &:active {
          transform: scale(0.98);
        }

        .header-brand {
          display: flex;
          align-items: baseline;
          gap: 10px;
          user-select: none;

          .brand-icon {
            font-size: 28px;
          }

          .brand-name {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 0.5px;
          }
        }
      }

      .header-nav {
        display: flex;
        align-items: center;
        gap: 8px;

        .nav-button {
          padding: 10px 24px;
          border: none;
          background-color: transparent;
          color: #606266;
          font-size: 15px;
          font-weight: 500;
          cursor: pointer;
          border-radius: 6px;
          transition: all 0.3s ease;
          position: relative;

          // 默认状态
          &:hover {
            background-color: #f5f7fa;
            color: #303133;
          }

          // 激活状态
          &.active {
            background-color: #409eff;
            color: #fff;
            box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);

            &:hover {
              background-color: #66b1ff;
              box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
            }
          }

          // 点击效果
          &:active {
            transform: scale(0.98);
          }
        }
      }
    }

    .router-view-container {
      padding: 20px 50px;
    }
  }

  .footer {
    background-color: #E6E8EB;
    padding: 32px 50px 24px;
    margin-top: auto;

    .footer-content {
      max-width: 1200px;
      margin: 0 auto;

      .footer-main {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;

        .footer-logo {
          display: flex;
          align-items: baseline;
          gap: 12px;
          margin-bottom: 12px;

          .logo-icon {
            font-size: 32px;
          }

          .logo-text {
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 1px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
          }
        }

        .footer-info {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          opacity: 0.9;

          .separator {
            opacity: 0.5;
          }

          .info-text {
            font-weight: 300;
          }
        }
      }

      .footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        font-size: 13px;

        .copyright {
          opacity: 0.8;
          font-weight: 300;
        }

        .footer-links {
          display: flex;
          align-items: center;
          gap: 12px;

          .footer-link {
            display: flex;
            align-items: baseline;
            gap: 6px;
            text-decoration: none;
            opacity: 0.9;
            transition: all 0.3s ease;
            padding: 4px 8px;
            border-radius: 4px;

            &:hover {
              opacity: 1;
              background-color: #F0F2F5;
            }

            .link-icon {
              font-size: 14px;
            }
          }

          .separator {
            opacity: 0.4;
          }

          .version {
            padding: 4px 12px;
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            opacity: 0.9;
          }
        }
      }
    }
  }
}
</style>
