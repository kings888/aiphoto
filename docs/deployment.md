# AI Photo 项目部署文档

## 目录
- [环境要求](#环境要求)
- [前端部署](#前端部署)
- [后端部署](#后端部署)
- [数据库配置](#数据库配置)
- [第三方服务配置](#第三方服务配置)
- [常见问题](#常见问题)
- [性能优化](#性能优化)

## 环境要求

### 前端环境
- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0
- Vue.js 3.x
- Vite >= 4.0.0
- 现代浏览器（支持ES6+）

### 后端环境
- Python >= 3.8
- pip >= 21.0
- MySQL >= 8.0
- Redis >= 6.0（用于缓存和会话管理）
- 支持HTTPS的Web服务器（推荐Nginx）
- 足够的磁盘空间用于存储图片（建议至少10GB）

## 前端部署

### 开发环境

1. 克隆项目并进入目录
```bash
git clone <repository-url>
cd aiphoto
```

2. 安装依赖
```bash
npm install
# 或
yarn
```

3. 配置环境变量
创建.env.development文件：
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_PAYMENT_RETURN_URL=http://localhost:3000/payment/result
```

4. 启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

### 生产环境

1. 配置生产环境变量
创建.env.production文件：
```env
VITE_API_BASE_URL=https://api.your-domain.com
VITE_PAYMENT_RETURN_URL=https://your-domain.com/payment/result
```

2. 构建项目
```bash
npm run build
# 或
yarn build
```

3. 部署dist目录
- 将生成的dist目录部署到Web服务器（如Nginx）的静态资源目录下
- 确保所有静态资源都启用了适当的缓存策略
- 配置正确的CSP（Content Security Policy）头以增强安全性

### Nginx配置示例
```nginx
server {
    listen 0.0.0.0:80;
    listen 0.0.0.0:443 ssl;
    server_name your-domain.com;

    # SSL配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /path/to/dist;
    index index.html;

    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 安全配置
    # 限制连接数
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    limit_conn addr 100;

    # 限制请求速率
    limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

    # 基本安全头
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    location / {
        try_files $uri $uri/ /index.html;
        
        # 应用请求限制
        limit_req zone=one burst=5 nodelay;
    }

    # API代理配置
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # API请求限制
        limit_req zone=one burst=5 nodelay;
    }
}
```

## 后端部署

1. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建.env文件，添加以下配置：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=aiphoto
DB_USER=root
DB_PASSWORD=your-password

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600  # 访问令牌过期时间（秒）

# OpenAI配置
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，如果使用代理

# 支付宝配置
ALIPAY_APP_ID=your-app-id
ALIPAY_PRIVATE_KEY=your-private-key
ALIPAY_PUBLIC_KEY=your-public-key
ALIPAY_NOTIFY_URL=https://your-domain.com/api/payment/notify
```

4. 初始化数据库
```bash
python manage.py db upgrade
```

5. 启动服务
开发环境：
```bash
python manage.py run
```

生产环境（使用gunicorn）：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app --timeout 120 --access-logfile logs/access.log --error-logfile logs/error.log
```

## 数据库配置

1. 创建数据库
```sql
CREATE DATABASE aiphoto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 创建用户并授权
```sql
CREATE USER 'aiphoto'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON aiphoto.* TO 'aiphoto'@'localhost';
FLUSH PRIVILEGES;
```

## 第三方服务配置

### OpenAI API
1. 访问 [OpenAI官网](https://platform.openai.com/) 注册账号
2. 在API设置页面生成API密钥
3. 将API密钥配置到环境变量
4. （可选）配置API代理
   - 如果直接访问OpenAI API存在网络问题，可以使用代理服务
   - 在.env文件中设置OPENAI_API_BASE为代理地址

### 支付宝支付
1. 注册支付宝开放平台账号
2. 创建应用并获取应用ID
3. 生成RSA密钥对
   ```bash
   # 生成私钥
   openssl genrsa -out private_key.pem 2048
   # 生成公钥
   openssl rsa -in private_key.pem -pubout -out public_key.pem
   ```
4. 配置支付回调地址
   - 设置为https://your-domain.com/api/payment/notify
   - 确保域名已备案（国内服务器必需）
5. 在开发环境中使用沙箱环境进行测试
   - 下载支付宝开发者工具
   - 使用沙箱账号和密码进行测试

## 常见问题

### 1. 前端跨域问题
- 确保Nginx配置了正确的代理规则
- 检查后端CORS配置是否正确
- 验证请求头中是否包含必要的跨域信息

### 2. 数据库连接失败
- 检查数据库服务是否正常运行
- 验证数据库用户名和密码是否正确
- 确认数据库主机和端口配置
- 检查防火墙设置是否允许数据库连接

### 3. OpenAI API调用失败
- 检查API密钥是否正确
- 确认API请求是否被墙，可能需要配置代理
- 检查API调用额度是否充足
- 验证请求参数格式是否符合OpenAI API规范
- 检查网络连接和超时设置

### 4. 图片上传失败
- 检查文件大小是否超过限制
- 确认文件格式是否支持
- 验证存储目录权限是否正确
- 检查磁盘空间是否充足

### 5. 支付回调问题
- 确保回调URL可以被外网访问
- 验证支付宝公钥是否正确配置
- 检查签名验证逻辑
- 确保回调接口幂等性处理正确

## 性能优化

### 前端优化
1. 资源优化
   - 启用gzip压缩
   - 使用CDN加速静态资源
   - 图片懒加载和适当的压缩
   - 代码分割和路由懒加载

2. 缓存策略
   - 合理设置HTTP缓存头
   - 使用Service Worker缓存静态资源
   - 实现数据本地缓存

### 后端优化
1. 数据库优化
   - 添加必要的索引
   - 优化查询语句
   - 使用连接池
   - 定期维护和清理数据

2. 服务器优化
   - 使用Redis缓存热点数据
   - 配置合适的进程数
   - 开启keepalive
   - 合理设置超时时间

3. 图片处理优化
   - 使用异步任务处理大型图片
   - 实现图片压缩和格式转换
   - 配置CDN存储和分发
- 验证请求参数格式是否正确
- 检查网络连接是否稳定

### 4. 支付宝支付问题
- 验证支付宝配置是否正确
- 检查支付回调地址是否可访问
- 确认RSA密钥格式是否正确
- 检查支付宝应用是否已上线
- 确保服务器时间同步准确

### 5. 服务器性能优化
- 调整gunicorn工作进程数
  ```bash
  # 建议设置为CPU核心数的2-4倍
  gunicorn -w $(nproc --all) -b 0.0.0.0:5000 wsgi:app
  ```
- 优化数据库查询
  - 添加适当的索引
  - 优化SQL语句
  - 使用连接池
- 使用缓存服务（如Redis）
  - 缓存频繁访问的数据
  - 实现接口限流
- 开启Nginx缓存
  - 静态资源缓存
  - 响应压缩

## 联系支持
如遇到其他问题，请联系技术支持团队：
- Email: support@example.com
- 工作时间: 周一至周五 9:00-18:00