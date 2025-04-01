<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>AI Photo Style Transfer</h1>
      <div class="user-actions">
        <el-button type="primary" @click="showLoginDialog">登录</el-button>
        <el-button @click="showRegisterDialog">注册</el-button>
      </div>
    </el-header>

    <el-main>
      <router-view></router-view>
    </el-main>

    <el-footer class="app-footer">
      <p>&copy; 2023 AI Photo Style Transfer. All rights reserved.</p>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const showLoginDialog = () => {
  router.push('/login')
}

const showRegisterDialog = () => {
  router.push('/register')
}
</script>

<style lang="scss" scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;

  h1 {
    margin: 0;
    font-size: 1.5rem;
    color: #409EFF;
  }

  .user-actions {
    display: flex;
    gap: 10px;
  }
}

.app-footer {
  background-color: #f5f5f5;
  text-align: center;
  padding: 20px;
  margin-top: auto;

  p {
    margin: 0;
    color: #666;
  }
}
</style>