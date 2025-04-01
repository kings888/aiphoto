<template>
  <div class="payment-container">
    <el-card class="payment-card">
      <template #header>
        <div class="card-header">
          <h2>支付中心</h2>
        </div>
      </template>
      
      <div class="service-options">
        <el-radio-group v-model="selectedService" class="service-radio-group">
          <el-radio-button label="basic">基础服务 (￥9.9)</el-radio-button>
          <el-radio-button label="premium">高级服务 (￥29.9)</el-radio-button>
          <el-radio-button label="unlimited">无限服务 (￥99.9)</el-radio-button>
        </el-radio-group>
      </div>

      <div class="service-description">
        <template v-if="selectedService === 'basic'">
          <h3>基础服务包含：</h3>
          <ul>
            <li>10次图片处理机会</li>
            <li>基础风格转换</li>
            <li>标准处理速度</li>
          </ul>
        </template>
        <template v-if="selectedService === 'premium'">
          <h3>高级服务包含：</h3>
          <ul>
            <li>50次图片处理机会</li>
            <li>高级风格转换</li>
            <li>优先处理速度</li>
          </ul>
        </template>
        <template v-if="selectedService === 'unlimited'">
          <h3>无限服务包含：</h3>
          <ul>
            <li>不限次数处理机会</li>
            <li>所有风格转换</li>
            <li>最高处理优先级</li>
          </ul>
        </template>
      </div>

      <div class="payment-action">
        <el-button type="primary" :loading="loading" @click="createOrder">
          立即支付
        </el-button>
      </div>

      <!-- 支付状态对话框 -->
      <el-dialog
        v-model="paymentDialogVisible"
        title="支付确认"
        width="30%"
        :close-on-click-modal="false"
      >
        <div class="payment-dialog-content">
          <div v-if="paymentStatus === 'pending'">
            <el-alert
              title="请在支付宝完成支付"
              type="info"
              :closable="false"
              show-icon
            >
              <p>订单金额：{{ getServicePrice }}</p>
              <p>订单编号：{{ orderId }}</p>
            </el-alert>
          </div>
          <div v-else-if="paymentStatus === 'success'">
            <el-alert
              title="支付成功！"
              type="success"
              :closable="false"
              show-icon
            >
              <p>您的服务已经开通</p>
            </el-alert>
          </div>
          <div v-else-if="paymentStatus === 'failed'">
            <el-alert
              title="支付失败"
              type="error"
              :closable="false"
              show-icon
            >
              <p>请稍后重试或联系客服</p>
            </el-alert>
          </div>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="closePaymentDialog">关闭</el-button>
            <el-button
              v-if="paymentStatus === 'failed'"
              type="primary"
              @click="retryPayment"
            >
              重试
            </el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const selectedService = ref('basic')
const paymentDialogVisible = ref(false)
const paymentStatus = ref('pending')
const orderId = ref('')

// 服务价格映射
const servicePrices = {
  basic: 9.9,
  premium: 29.9,
  unlimited: 99.9
}

// 计算当前选择服务的价格
const getServicePrice = computed(() => {
  return servicePrices[selectedService.value]
})

// 创建订单
const createOrder = async () => {
  try {
    loading.value = true
    const response = await axios.post('/api/payment/create', {
      serviceType: selectedService.value,
      amount: getServicePrice.value
    })
    
    orderId.value = response.data.orderId
    // 打开支付宝支付页面
    window.open(response.data.payUrl, '_blank')
    paymentDialogVisible.value = true
    
    // 开始轮询支付状态
    startPaymentStatusCheck()
  } catch (error) {
    console.error('创建订单失败:', error)
    paymentStatus.value = 'failed'
  } finally {
    loading.value = false
  }
}

// 轮询检查支付状态
const startPaymentStatusCheck = async () => {
  const checkStatus = async () => {
    try {
      const response = await axios.get(`/api/payment/status/${orderId.value}`)
      if (response.data.status === 'success') {
        paymentStatus.value = 'success'
        return true
      } else if (response.data.status === 'failed') {
        paymentStatus.value = 'failed'
        return true
      }
      return false
    } catch (error) {
      console.error('检查支付状态失败:', error)
      return false
    }
  }

  // 每3秒检查一次，最多检查20次（1分钟）
  let attempts = 0
  const maxAttempts = 20

  const intervalId = setInterval(async () => {
    if (attempts >= maxAttempts) {
      clearInterval(intervalId)
      paymentStatus.value = 'failed'
      return
    }

    const isDone = await checkStatus()
    if (isDone) {
      clearInterval(intervalId)
    }

    attempts++
  }, 3000)
}

// 关闭支付对话框
const closePaymentDialog = () => {
  paymentDialogVisible.value = false
  if (paymentStatus.value === 'success') {
    router.push('/') // 支付成功后返回首页
  }
}

// 重试支付
const retryPayment = () => {
  paymentStatus.value = 'pending'
  createOrder()
}
</script>

<style scoped>
.payment-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.payment-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-options {
  margin: 20px 0;
  text-align: center;
}

.service-radio-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.service-description {
  margin: 20px 0;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.service-description h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.service-description ul {
  list-style-type: none;
  padding: 0;
}

.service-description li {
  margin: 10px 0;
  padding-left: 20px;
  position: relative;
}

.service-description li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
}

.payment-action {
  text-align: center;
  margin-top: 30px;
}

.payment-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>