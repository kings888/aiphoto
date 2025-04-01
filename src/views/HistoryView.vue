<template>
  <div class="history-container">
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <h2>处理历史</h2>
        </div>
      </template>

      <el-table :data="historyList" style="width: 100%">
        <el-table-column prop="date" label="处理时间" width="180" />
        <el-table-column prop="style" label="风格描述" />
        <el-table-column prop="count" label="图片数量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              :disabled="row.status !== 'completed'"
              @click="handlePreview(row)"
            >
              预览
            </el-button>
            <el-button
              type="primary"
              link
              :disabled="row.status !== 'completed'"
              @click="handleDownload(row)"
            >
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog
        v-model="previewVisible"
        title="图片预览"
        width="80%"
        destroy-on-close
      >
        <el-carousel height="400px">
          <el-carousel-item v-for="(image, index) in currentImages" :key="index">
            <div class="image-comparison">
              <div class="image-item">
                <h4>原图</h4>
                <img :src="image.original" alt="原图" />
              </div>
              <div class="image-item">
                <h4>处理后</h4>
                <img :src="image.processed" alt="处理后" />
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 模拟历史记录数据
const historyList = ref([
  {
    id: 1,
    date: '2023-08-20 10:30:00',
    style: '梵高星空风格',
    count: 3,
    status: 'completed',
    images: [
      {
        original: 'path/to/original1.jpg',
        processed: 'path/to/processed1.jpg'
      },
      {
        original: 'path/to/original2.jpg',
        processed: 'path/to/processed2.jpg'
      },
      {
        original: 'path/to/original3.jpg',
        processed: 'path/to/processed3.jpg'
      }
    ]
  },
  {
    id: 2,
    date: '2023-08-20 11:15:00',
    style: '赛博朋克风格',
    count: 2,
    status: 'processing'
  }
])

const previewVisible = ref(false)
const currentImages = ref([])

const handlePreview = (row) => {
  currentImages.value = row.images
  previewVisible.value = true
}

const handleDownload = (row) => {
  // TODO: 实现批量下载功能
  ElMessage.success('开始下载处理后的图片')
}
</script>

<style lang="scss" scoped>
.history-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-header {
  h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #303133;
  }
}

.image-comparison {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 100%;
  padding: 20px;

  .image-item {
    text-align: center;
    
    h4 {
      margin: 0 0 10px;
      color: #606266;
    }

    img {
      max-height: 300px;
      max-width: 100%;
      object-fit: contain;
    }
  }
}
</style>