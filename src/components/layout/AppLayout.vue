<script setup lang="ts">
import Sidebar from './Sidebar.vue'
</script>

<template>
  <el-container class="app-shell">
    <el-aside :width="'var(--sidebar-width)'" class="app-sidebar">
      <Sidebar />
    </el-aside>
    <el-container class="app-main">
      <slot />
    </el-container>
  </el-container>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  background: var(--sidebar-bg);
  z-index: 100;
  overflow-y: auto;
  overflow-x: hidden;
}

.app-main {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  background: var(--bg-page);
}

.app-main::-webkit-scrollbar {
  width: 6px;
}

.app-main::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}
</style>
