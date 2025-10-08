# SeedSearcher Frontend

🌱 星露谷物语种子搜索工具 - 前端项目

## 🛠️ 技术栈

### 核心框架
- **Vue 3.5.18**
- **Vite 7.1.2**
- **Vue Router 4.5.1**

### UI 组件库
- **Element Plus 2.11.3**
- **unplugin-auto-import**
- **unplugin-vue-components**

### 网络请求
- **Axios 1.11.0**

### 样式处理
- **Sass 1.92.1**
- **normalize.css 8.0.1**

## 📦 环境要求

### 必需环境
- **Node.js**: >= 18.0.0 （推荐 18.x 或 20.x LTS 版本）
- **npm**: >= 9.0.0 或 **pnpm**: >= 8.0.0 或 **yarn**: >= 1.22.0

### 推荐开发工具
- **VS Code** + **Volar**
- **Chrome** 或 **Edge**

## 🚀 快速开始

### 1. 安装依赖

使用 npm:
```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

启动成功后，浏览器访问 `http://localhost:5173`

**注意**：确保后端服务已启动（默认运行在 `http://127.0.0.1:5000`）

## 📜 可用命令

### 生产构建
构建生产环境代码，输出到 `dist/` 目录：
```bash
npm run build
```

构建完成后，`dist/` 目录包含：
- 优化压缩后的 HTML、CSS、JS 文件
- 代码分割（Code Splitting）
- Tree Shaking（移除未使用代码）
- 资源哈希命名（用于缓存）

## 📁 项目结构

```
frontend/
├── public/              # 静态资源目录
│   └── favicon.png     # 网站图标
├── src/                # 源代码目录
│   ├── assets/         # 资源文件
│   ├── components/     # 全局组件
│   ├── router/         # 路由配置
│   │   └── index.js
│   ├── style/          # 全局样式
│   │   └── main.css
│   ├── utils/          # 工具函数
│   │   └── http.js    # Axios 封装
│   ├── views/          # 页面组件
│   │   ├── home/       # 种子搜索页面
│   │   └── weather-forecast.vue      # 天气预测页面
│   ├── App.vue         # 根组件
│   └── main.js         # 应用入口
├── index.html          # HTML 模板
├── vite.config.js      # Vite 配置
├── package.json        # 项目配置
└── README.md           # 项目文档
```

## 🏗️ 架构设计

### 模块化重构
项目采用 **constants / composables / components** 三层架构：

1. **constants/** - 配置数据层
   - 存放静态配置数据（天气选项、宝箱配置等）
   
2. **composables/** - 业务逻辑层（Composition API）
   - 封装可复用的业务逻辑
   - 管理响应式状态
   - 返回状态和方法供组件使用
   
3. **components/** - 展示组件层
   - 专注 UI 渲染
   - 通过 props 接收数据
   - 通过 emits 向上通信

### 代码优化
- ✅ 从单文件 1042 行重构为 15+ 个模块文件
- ✅ 主文件精简至 216 行（-79%）
- ✅ 符合 Vue 3 Composition API 最佳实践
- ✅ 支持前端分页（性能优化）

## 🔌 API 接口

前端通过 Axios 与后端 Flask API 通信：

### 基础配置
- **开发环境**: `http://127.0.0.1:5000/api`
- **生产环境**: 根据部署配置动态调整

### 主要接口
- `POST /api/search` - 种子搜索（批量筛选）
- `POST /api/weather` - 天气预测
- `POST /api/mines` - 矿井怪物层预测
- `POST /api/chests/check` - 宝箱规则检查
- `POST /api/desert` - 沙漠节预测
- `POST /api/saloon_trash` - 酒吧垃圾桶预测
- `POST /api/night_event` - 夜间事件预测
