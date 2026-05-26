# -*- coding: utf-8 -*-
"""
后端邮件发送服务
使用 Flask 和 QQ 邮箱 SMTP 发送邮件
"""
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
import sys
import io
import os

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__)
CORS(app)

# 从环境变量读取配置，如果不存在则使用默认值
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '465'))
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '943411733@qq.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'hipziemwzrifbdjh')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '943411733@qq.com')

mail = Mail(app)

@app.route('/')
def index():
    return jsonify({'message': '邮件服务已启动'})

@app.route('/api/send-users-email', methods=['POST'])
def send_users_email():
    try:
        data = request.get_json()

        if not data or 'users' not in data:
            return jsonify({'error': '缺少用户数据'}), 400

        users = data['users']
        email = data.get('email', '943411733@qq.com')

        if not users:
            return jsonify({'error': '没有用户数据'}), 400

        # 生成邮件内容
        subject = '用户注册信息汇总'
        body_lines = [
            '========================================',
            '        用户注册信息汇总',
            '========================================',
            '发送时间：' + request.headers.get('date', '未知'),
            '用户数量：' + str(len(users)) + ' 位',
            '========================================',
            ''
        ]

        for index, (phone, user) in enumerate(users.items(), 1):
            created_at = user.get('createdAt', '未知时间')
            body_lines.extend([
                f'【用户 {index}】',
                f'手机号：{phone}',
                f'注册时间：{created_at}',
                '========================================',
                ''
            ])

        body = '\n'.join(body_lines)

        # 创建邮件
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body
        )

        # 发送邮件
        mail.send(msg)

        return jsonify({
            'success': True,
            'message': f'成功发送邮件到 {email}，包含 {len(users)} 位用户'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    """保存用户数据"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '缺少数据'}), 400

        # 读取现有数据
        storage_file = 'users_data.json'

        existing_data = {}
        if __import__('os').path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_data = __import__('json').load(f)

        # 合并数据 - 如果新数据有users且为空对象，则清空所有用户
        if 'users' in data:
            if not data.get('users') or len(data.get('users', {})) == 0:
                # 清空所有用户
                existing_data['users'] = {}
            else:
                # 更新用户数据 - 检查重复
                existing_users = existing_data.get('users', {})
                new_users = data.get('users', {})

                for phone, user in new_users.items():
                    if phone in existing_users:
                        # 手机号已存在，覆盖更新
                        existing_users[phone] = user
                    else:
                        # 新手机号，添加
                        existing_users[phone] = user

                existing_data['users'] = existing_users

        # 保存数据
        with open(storage_file, 'w', encoding='utf-8') as f:
            __import__('json').dump(existing_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '用户数据已保存'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-users', methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        storage_file = 'users_data.json'

        if not __import__('os').path.exists(storage_file):
            return jsonify({'users': {}})

        with open(storage_file, 'r', encoding='utf-8') as f:
            data = __import__('json').load(f)

        return jsonify({'users': data.get('users', {})})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-orders', methods=['GET'])
def get_orders():
    """获取所有订单"""
    try:
        storage_file = 'orders_data.json'

        if not __import__('os').path.exists(storage_file):
            return jsonify({'orders': []})

        with open(storage_file, 'r', encoding='utf-8') as f:
            data = __import__('json').load(f)

        return jsonify({'orders': data if isinstance(data, list) else []})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-order', methods=['POST'])
def save_order():
    """保存订单"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '缺少数据'}), 400

        storage_file = 'orders_data.json'

        existing_data = []
        if __import__('os').path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_data = __import__('json').load(f)

        # 添加新订单
        if 'order' in data:
            if not isinstance(existing_data, list):
                existing_data = []

            new_order = data['order']

            # 检查订单是否已存在
            order_id = new_order.get('id')
            exists = False

            for i, order in enumerate(existing_data):
                if order.get('id') == order_id:
                    # 订单已存在，更新状态和时间
                    existing_data[i] = {**order, **new_order, 'updatedAt': new_order.get('updatedAt') or new_order.get('paidAt')}
                    exists = True
                    break

            if not exists:
                # 订单不存在，添加到数组开头
                existing_data.insert(0, new_order)
        elif 'orders' in data and isinstance(data['orders'], list):
            # 批量添加订单
            for new_order in data['orders']:
                order_id = new_order.get('id')
                exists = False

                for i, order in enumerate(existing_data):
                    if order.get('id') == order_id:
                        # 订单已存在，更新状态和时间
                        existing_data[i] = {**order, **new_order, 'updatedAt': new_order.get('updatedAt') or new_order.get('paidAt')}
                        exists = True
                        break

                if not exists:
                    # 订单不存在，添加到数组开头
                    existing_data.insert(0, new_order)

        # 保存数据
        with open(storage_file, 'w', encoding='utf-8') as f:
            __import__('json').dump(existing_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '订单保存成功'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'邮件服务已启动！')
    print(f'访问 http://localhost:{port} 查看状态')
    app.run(host='0.0.0.0', port=port)
