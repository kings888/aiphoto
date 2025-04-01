from flask import Blueprint, request, jsonify
from alipay import AliPay
import os
import time
import uuid

payment_bp = Blueprint('payment', __name__)

# 支付宝配置
alipay = AliPay(
    appid=os.getenv('ALIPAY_APP_ID'),
    app_notify_url=None,
    app_private_key_string=os.getenv('ALIPAY_PRIVATE_KEY'),
    alipay_public_key_string=os.getenv('ALIPAY_PUBLIC_KEY'),
    sign_type="RSA2",
    debug=True  # 沙箱模式
)

# 订单状态
ORDER_STATUS = {
    'PENDING': 'pending',
    'SUCCESS': 'success',
    'FAILED': 'failed'
}

# 模拟订单存储
orders = {}

@payment_bp.route('/create', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        service_type = data.get('serviceType')
        amount = data.get('amount')
        
        # 生成订单号
        order_id = str(uuid.uuid4())
        
        # 创建支付宝订单
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(amount),
            subject=f'AI Photo {service_type.capitalize()} Service',
            return_url=os.getenv('ALIPAY_RETURN_URL'),
            notify_url=os.getenv('ALIPAY_NOTIFY_URL')
        )
        
        # 存储订单信息
        orders[order_id] = {
            'service_type': service_type,
            'amount': amount,
            'status': ORDER_STATUS['PENDING'],
            'create_time': time.time()
        }
        
        # 生成支付链接
        pay_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}" if alipay.debug else \
                  f"https://openapi.alipay.com/gateway.do?{order_string}"
        
        return jsonify({
            'orderId': order_id,
            'payUrl': pay_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/status/<order_id>', methods=['GET'])
def check_order_status(order_id):
    try:
        if order_id not in orders:
            return jsonify({'error': 'Order not found'}), 404
            
        # 查询支付宝订单状态
        result = alipay.api_alipay_trade_query(out_trade_no=order_id)
        
        if result.get('trade_status', '') in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
            orders[order_id]['status'] = ORDER_STATUS['SUCCESS']
        elif result.get('trade_status', '') in ('TRADE_CLOSED', 'TRADE_FAILED'):
            orders[order_id]['status'] = ORDER_STATUS['FAILED']
            
        return jsonify({
            'status': orders[order_id]['status']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/notify', methods=['POST'])
def alipay_notify():
    try:
        data = request.form.to_dict()
        signature = data.pop('sign')
        
        # 验证签名
        if alipay.verify(data, signature):
            order_id = data.get('out_trade_no')
            if order_id in orders:
                if data.get('trade_status') in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
                    orders[order_id]['status'] = ORDER_STATUS['SUCCESS']
                elif data.get('trade_status') in ('TRADE_CLOSED', 'TRADE_FAILED'):
                    orders[order_id]['status'] = ORDER_STATUS['FAILED']
                    
            return 'success'
        return 'fail'
    except Exception as e:
        return 'fail'