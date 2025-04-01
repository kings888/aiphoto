<template>
  <div class="home-container">
    <div class="steps-container">
      <el-steps :active="currentStep" finish-status="success">
        <el-step title="上传照片" />
        <el-step title="付款" />
        <el-step title="处理中" />
        <el-step title="完成" />
      </el-steps>
    </div>

    <el-card class="upload-card">
      <div class="step-content">
        <!-- 步骤1：上传照片 -->
        <div v-if="currentStep === 0">
          <el-upload
            class="upload-area"
            drag
            multiple
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
          </el-upload>

          <div class="style-selection" v-if="fileList.length > 0">
            <h3>选择风格</h3>
            <div class="style-cards">
              <div
                v-for="style in styleOptions"
                :key="style.id"
                class="style-card"
                :class="{ active: selectedStyle === style.id }"
                @click="selectStyle(style.id)"
              >
                <img :src="style.preview" :alt="style.name">
                <h4>{{ style.name }}</h4>
                <p>{{ style.description }}</p>
              </div>
            </div>
          </div>

          <div class="summary" v-if="fileList.length > 0">
            <p>已选择 {{ fileList.length }} 张图片</p>
            <p>总价：¥{{ totalPrice }}</p>
            <el-button type="primary" @click="nextStep" :disabled="!canProceed">
              下一步
            </el-button>
          </div>
        </div>

        <!-- 步骤2：付款 -->
        <div v-if="currentStep === 1" class="payment-step">
          <h3>确认订单</h3>
          <div class="order-summary">
            <p>处理图片数量：{{ fileList.length }}张</p>
            <p>选择风格：{{ getSelectedStyleName }}</p>
            <p class="total-price">总价：¥{{ totalPrice }}</p>
          </div>
          <el-button type="primary" @click="handlePayment" :loading="paymentLoading">
            立即支付
          </el-button>
        </div>

        <!-- 步骤3：处理中 -->
        <div v-if="currentStep === 2" class="processing-step">
          <el-progress type="circle" :percentage="processPercentage" />
          <p>正在处理您的图片，请稍候...</p>
        </div>

        <!-- 步骤4：完成 -->
        <div v-if="currentStep === 3" class="complete-step">
          <el-result
            icon="success"
            title="处理完成"
            sub-title="您的图片已经处理完成，请点击下方按钮下载"
          >
            <template #extra>
              <el-button type="primary" @click="downloadResults">下载处理结果</el-button>
              <el-button @click="startNew">开始新的处理</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createPaymentOrder, checkPaymentStatus } from '@/services/payment'

const currentStep = ref(0)
const fileList = ref([])
const selectedStyle = ref('')
const paymentLoading = ref(false)
const processPercentage = ref(0)

// 风格选项
const styleOptions = [
  {
    id: 'vintage',
    name: '复古风格',
    description: '温暖、怀旧的复古卡力风格',
    preview: '/styles/vintage.svg'
  },
  {
    id: 'modern',
    name: '现代动漫风格',
    description: '现代动漫的日式风格转换',
    preview: '/styles/modern.svg'
  },
  {
    id: 'watercolor',
    name: '水彩画风格',
    description: '清新唯美的水彩艺术风格',
    preview: '/styles/watercolor.svg'
  }
]

const totalPrice = computed(() => {
  return fileList.value.length * 5
})

const canProceed = computed(() => {
  return fileList.value.length > 0 && selectedStyle.value
})

const getSelectedStyleName = computed(() => {
  const style = styleOptions.find(s => s.id === selectedStyle.value)
  return style ? style.name : ''
})

const handleFileChange = (file) => {
  // 检查文件类型
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  // 检查文件大小（限制为5MB）
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB！')
    return false
  }
  return true
}

const handleFileRemove = (file) => {
  const index = fileList.value.indexOf(file)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

const selectStyle = (styleId) => {
  selectedStyle.value = styleId
}

const nextStep = () => {
  if (!canProceed.value) {
    ElMessage.warning('请上传图片并选择风格')
    return
  }
  currentStep.value++
}

const handlePayment = async () => {
  try {
    paymentLoading.value = true
    const order = await createPaymentOrder({
      files: fileList.value,
      styleId: selectedStyle.value,
      amount: totalPrice.value
    })
    
    // 打开支付页面
    window.open(order.payUrl, '_blank')
    
    // 开始轮询支付状态
    startPaymentCheck(order.orderId)
  } catch (error) {
    ElMessage.error('创建订单失败，请重试')
  } finally {
    paymentLoading.value = false
  }
}

const startPaymentCheck = async (orderId) => {
  const checkInterval = setInterval(async () => {
    try {
      const result = await checkPaymentStatus(orderId)
      if (result.status === 'success') {
        clearInterval(checkInterval)
        currentStep.value = 2
        startProcessing()
      } else if (result.status === 'failed') {
        clearInterval(checkInterval)
        ElMessage.error('支付失败，请重试')
      }
    } catch (error) {
      console.error('检查支付状态失败:', error)
    }
  }, 3000)
}

const startProcessing = () => {
  // 模拟处理进度
  const interval = setInterval(() => {
    if (processPercentage.value >= 100) {
      clearInterval(interval)
      currentStep.value = 3
    } else {
      processPercentage.value += 10
    }
  }, 1000)
}

const downloadResults = () => {
  // TODO: 实现下载处理结果的逻辑
  ElMessage.success('开始下载处理结果')
}

const startNew = () => {
  // 重置所有状态
  currentStep.value = 0
  fileList.value = []
  selectedStyle.value = ''
  processPercentage.value = 0
}
</script>

<style lang="scss" scoped>
.home-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.steps-container {
  margin-bottom: 30px;
}

.upload-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  
  .step-content {
    padding: 20px;
  }
}

.upload-area {
  margin: 20px 0;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  transition: all 0.3s;
  
  &:hover {
    border-color: #409EFF;
  }
  
  .el-upload__text {
    color: #606266;
    margin-top: 10px;
    
    em {
      color: #409EFF;
      font-style: normal;
    }
  }
}

.style-selection {
  margin: 30px 0;
  
  h3 {
    margin-bottom: 20px;
    color: #303133;
  }
  
  .style-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    
    .style-card {
      border: 2px solid #dcdfe6;
      border-radius: 8px;
      padding: 15px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
      }
      
      &.active {
        border-color: #409EFF;
        background: rgba(64,158,255,0.1);
      }
      
      img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 4px;
        margin-bottom: 10px;
      }
      
      h4 {
        margin: 10px 0;
        color: #303133;
      }
      
      p {
        color: #606266;
        font-size: 14px;
        margin: 0;
      }
    }
  }
}

.payment-step {
  text-align: center;
  padding: 20px;
  
  h3 {
    color: #303133;
    margin-bottom: 20px;
  }
  
  .order-summary {
    background: #f5f7fa;
    padding: 20px;
    border-radius: 6px;
    margin-bottom: 20px;
    
    p {
      margin: 10px 0;
      color: #606266;
      
      &.total-price {
        color: #409EFF;
        font-size: 18px;
        font-weight: bold;
      }
    }
  }
}

.processing-step {
  text-align: center;
  padding: 40px 0;
  
  .el-progress {
    margin-bottom: 20px;
  }
  
  p {
    color: #606266;
  }
}

.complete-step {
  text-align: center;
  padding: 40px 0;
  
  .el-result {
    padding: 0;
  }
}

.summary {
  text-align: center;
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 6px;
  
  p {
    margin: 10px 0;
    color: #606266;
    
    &:last-child {
      color: #409EFF;
      font-size: 18px;
      font-weight: bold;
    }
  }
}
</style>