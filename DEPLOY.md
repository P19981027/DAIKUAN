# DAIKUAN 部署到 Render

由于当前网络环境无法直接访问 GitHub，请按以下步骤手动部署：

## 方法一：本地部署脚本

双击运行 `deploy-local.bat`，它会自动：
1. 提交代码到 GitHub
2. 打开 Render 网站

然后手动在 Render 上创建 Web Service。

## 方法二：GitHub Actions 自动部署

### 1. 获取 Render API Token

1. 登录 https://dashboard.render.com
2. 点击右上角头像 → **Account Settings**
3. 在 **API Tokens** 部分 → **Create Token**
4. 复制生成的 token

### 2. 添加 GitHub Secret

1. 进入 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加：
   - Name: `RENDER_API_TOKEN`
   - Value: 你的 Render API Token

### 3. 触发部署

1. 进入 **Actions** 标签
2. 选择 **Deploy to Render** workflow
3. 点击 **Run workflow** → **Run workflow**

## 方法三：完全手动部署

### 步骤 1：登录 Render
访问 https://render.com 用 GitHub 登录

### 步骤 2：创建 Web Service

1. 点击 "New +" → "Web Service"
2. 连接 GitHub 仓库 `P19981027/DAIKUAN`
3. 配置：
   ```
   Name: daikuan-app
   Region: Singapore (ap-southeast)
   Environment: Python 3
   Root Directory: ./
   Build Command: pip install -r requirements.txt
   Start Command: python server.py
   ```
4. 添加环境变量：
   - `MAIL_USERNAME` = `943411733@qq.com`
   - `MAIL_PASSWORD` = `hipziemwzrifbdjh`

### 步骤 3：部署
点击 "Create Web Service"，等待 2-3 分钟

### 步骤 4：访问
复制 Render URL，访问 `/admin` 查看管理后台

## 部署后配置

### 配置域名（可选）
在 Render 服务设置中添加自定义域名

### 配置持久化存储
Free 计划会丢失数据，需要：
1. 升级到 Paid 计划
2. 或使用 GitHub Actions + 外部数据库
3. 或使用 Render Persistent Disk（付费）

## 故障排除

### 构建失败
- 检查 `requirements.txt` 是否正确
- 查看 Render 的 Build Logs

### 启动失败
- 确认 `startCommand` 是 `python server.py`
- 检查端口是否正确

### 环境变量未生效
- 确认变量名称完全匹配（区分大小写）
- 重新部署生效
