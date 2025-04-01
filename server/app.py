from flask import Flask
from flask_cors import CORS
from payment import payment_bp
from gpt_service import gpt_bp
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置CORS
CORS(app)

# 注册蓝图
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(gpt_bp, url_prefix='/api/gpt')

# 配置应用
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

@app.route('/health')
def health_check():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)