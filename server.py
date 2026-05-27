# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory, session
from flask_mail import Mail, Message
from flask_cors import CORS
import sys
import io
import os
import json
import uuid
import hashlib

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__, static_folder='.')
CORS(app)

app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Mail config — all from env vars, no defaults for credentials
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '465'))
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')

mail = Mail(app)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin888')

DATA_DIR = os.environ.get('DATA_DIR', '.')
os.makedirs(DATA_DIR, exist_ok=True)


def _path(filename):
    return os.path.join(DATA_DIR, filename)


def _hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# ---------- static files ----------

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    if os.path.isfile(filename):
        return send_from_directory('.', filename)
    return jsonify({'error': 'not found'}), 404


# ---------- admin auth ----------

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    if data.get('password') == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '密码错误'}), 401


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return jsonify({'success': True})


def require_admin():
    if not session.get('admin'):
        return jsonify({'error': '未授权，请先登录管理后台'}), 401
    return None


# ---------- user APIs ----------

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少数据'}), 400

        storage_file = _path('users_data.json')
        existing_data = {}
        if os.path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        if 'users' in data:
            if not data.get('users') or len(data.get('users', {})) == 0:
                existing_data['users'] = {}
            else:
                existing_users = existing_data.get('users', {})
                new_users = data.get('users', {})
                for phone, user in new_users.items():
                    # hash password before storing
                    if 'password' in user and not user['password'].startswith('sha256:'):
                        user['password'] = 'sha256:' + _hash_password(user['password'])
                    existing_users[phone] = user
                existing_data['users'] = existing_users

        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '用户数据已保存'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/login-user', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        password = data.get('password', '')

        storage_file = _path('users_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'success': False, 'error': '该账号未注册'}), 400

        with open(storage_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        users = existing_data.get('users', {})
        if phone not in users:
            return jsonify({'success': False, 'error': '该账号未注册'}), 400

        user = users[phone]
        stored_pw = user.get('password', '')

        # support both hashed and plain-text passwords during migration
        if stored_pw.startswith('sha256:'):
            if stored_pw != 'sha256:' + _hash_password(password):
                return jsonify({'success': False, 'error': '密码错误'}), 400
        else:
            if stored_pw != password:
                return jsonify({'success': False, 'error': '密码错误'}), 400

        return jsonify({'success': True, 'user': {'phone': phone, 'createdAt': user.get('createdAt', '')}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete-user', methods=['POST'])
def delete_user():
    auth = require_admin()
    if auth:
        return auth
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        if not phone:
            return jsonify({'error': '缺少手机号'}), 400

        storage_file = _path('users_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'error': '用户不存在'}), 404

        with open(storage_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        users = existing_data.get('users', {})
        if phone not in users:
            return jsonify({'error': '用户不存在'}), 404

        del users[phone]
        existing_data['users'] = users

        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '用户已删除'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete-order', methods=['POST'])
def delete_order():
    auth = require_admin()
    if auth:
        return auth
    try:
        data = request.get_json()
        order_id = data.get('id', '')
        if not order_id:
            return jsonify({'error': '缺少订单ID'}), 400

        storage_file = _path('orders_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'error': '订单不存在'}), 404

        with open(storage_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        if not isinstance(existing_data, list):
            return jsonify({'error': '订单数据格式错误'}), 500

        new_data = [o for o in existing_data if o.get('id') != order_id]
        if len(new_data) == len(existing_data):
            return jsonify({'error': '订单不存在'}), 404

        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '订单已删除'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import-data', methods=['POST'])
def import_data():
    auth = require_admin()
    if auth:
        return auth
    try:
        data = request.get_json()

        if 'users' in data:
            storage_file = _path('users_data.json')
            existing = {}
            if os.path.exists(storage_file):
                with open(storage_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            existing_users = existing.get('users', {})
            for phone, user in data['users'].items():
                existing_users[phone] = user
            existing['users'] = existing_users
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)

        if 'orders' in data:
            storage_file = _path('orders_data.json')
            existing = []
            if os.path.exists(storage_file):
                with open(storage_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
            existing_ids = {o.get('id') for o in existing}
            for order in data['orders']:
                if order.get('id') not in existing_ids:
                    existing.insert(0, order)
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '数据导入成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-users', methods=['GET'])
def get_users():
    auth = require_admin()
    if auth:
        return auth
    try:
        storage_file = _path('users_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'users': {}})
        with open(storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'users': data.get('users', {})})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-orders', methods=['GET'])
def get_orders():
    auth = require_admin()
    if auth:
        return auth
    try:
        storage_file = _path('orders_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'orders': []})
        with open(storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'orders': data if isinstance(data, list) else []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------- user-facing order API (no admin required, but filtered by phone) ----------

@app.route('/api/my-orders', methods=['POST'])
def my_orders():
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        if not phone:
            return jsonify({'error': '缺少手机号'}), 400

        storage_file = _path('orders_data.json')
        if not os.path.exists(storage_file):
            return jsonify({'orders': []})
        with open(storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_orders = data if isinstance(data, list) else []
        my = [o for o in all_orders if o.get('clientPhone') == phone]
        return jsonify({'orders': my})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/save-order', methods=['POST'])
def save_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少数据'}), 400

        storage_file = _path('orders_data.json')
        existing_data = []
        if os.path.exists(storage_file):
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        if 'order' in data:
            if not isinstance(existing_data, list):
                existing_data = []
            new_order = data['order']
            order_id = new_order.get('id')
            exists = False
            for i, order in enumerate(existing_data):
                if order.get('id') == order_id:
                    existing_data[i] = {**order, **new_order, 'updatedAt': new_order.get('updatedAt') or new_order.get('paidAt')}
                    exists = True
                    break
            if not exists:
                existing_data.insert(0, new_order)
        elif 'orders' in data and isinstance(data['orders'], list):
            for new_order in data['orders']:
                order_id = new_order.get('id')
                exists = False
                for i, order in enumerate(existing_data):
                    if order.get('id') == order_id:
                        existing_data[i] = {**order, **new_order, 'updatedAt': new_order.get('updatedAt') or new_order.get('paidAt')}
                        exists = True
                        break
                if not exists:
                    existing_data.insert(0, new_order)

        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '订单保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------- email (admin only) ----------

@app.route('/api/send-users-email', methods=['POST'])
def send_users_email():
    auth = require_admin()
    if auth:
        return auth
    try:
        data = request.get_json()
        if not data or 'users' not in data:
            return jsonify({'error': '缺少用户数据'}), 400

        users = data['users']
        email = data.get('email', app.config['MAIL_USERNAME'])

        if not users:
            return jsonify({'error': '没有用户数据'}), 400

        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            return jsonify({'error': '邮箱未配置，请设置 MAIL_USERNAME 和 MAIL_PASSWORD 环境变量'}), 500

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
        msg = Message(subject=subject, recipients=[email], body=body)
        mail.send(msg)

        return jsonify({'success': True, 'message': f'成功发送邮件到 {email}，包含 {len(users)} 位用户'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'服务已启动！')
    print(f'访问 http://localhost:{port} 查看状态')
    print(f'管理后台 http://localhost:{port}/admin.html')
    app.run(host='0.0.0.0', port=port)
