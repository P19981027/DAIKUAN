# DAIKUAN - 邮件发送服务使用说明

## 快速开始

### 1. 启动服务器

```bash
cd d:\AI\loan-service
python server.py
```

服务器将在 `http://localhost:5000` 启动

### 2. 注册用户

1. 打开 `index.html`
2. 注册用户

### 3. 管理和发送

1. 打开 `admin.html`
2. 点击"📋 用户列表"查看所有用户
3. 点击"📧 自动发送到QQ邮箱"

## 配置说明

### QQ 邮箱 SMTP

1. 登录 QQ 邮箱
2. 设置 → 账户 → 开启 SMTP 服务
3. 生成授权码
4. 编辑 `config.json` 配置授权码

## 文件说明

- `server.py` - Flask 后端服务
- `index.html` - 前端注册页面
- `admin.html` - 管理后台
- `users_data.json` - 用户数据存储
- `config.json` - 邮箱配置

## 技术说明

- 后端：Python Flask
- 邮件服务：QQ 邮箱 SMTP
- 跨域：CORS
