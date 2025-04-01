import axios from 'axios';
import { ElMessage } from 'element-plus';

// 支付服务配置
const API_BASE_URL = '/api';

// 创建支付订单
export const createPaymentOrder = async (serviceType, amount) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/payment/create`, {
      serviceType,
      amount
    });
    return response.data;
  } catch (error) {
    console.error('创建支付订单失败:', error);
    ElMessage.error('创建支付订单失败，请稍后重试');
    throw error;
  }
};

// 查询支付状态
export const checkPaymentStatus = async (orderId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/payment/status/${orderId}`);
    return response.data;
  } catch (error) {
    console.error('查询支付状态失败:', error);
    throw error;
  }
};

// 处理支付成功
export const handlePaymentSuccess = async (orderId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/payment/success`, { orderId });
    return response.data;
  } catch (error) {
    console.error('处理支付成功失败:', error);
    throw error;
  }
};

// 取消支付
export const cancelPayment = async (orderId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/payment/cancel`, { orderId });
    return response.data;
  } catch (error) {
    console.error('取消支付失败:', error);
    ElMessage.error('取消支付失败，请稍后重试');
    throw error;
  }
};