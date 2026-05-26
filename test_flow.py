# -*- coding: utf-8 -*-
"""
测试整个注册和登录流程
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_register():
    print("=" * 50)
    print("测试1: 注册新用户")
    print("=" * 50)

    # 测试注册一个新用户
    phone = "13800138000"
    password = "test123"

    # 先清空该用户
    requests.post(f'{BASE_URL}/api/save-user', json={"users": {phone: {}}})

    # 检查是否已存在
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    if result['users'].get(phone):
        print(f"[X] Error: Phone number {phone} already exists")
        return False
    print(f"[OK] Phone number {phone} available, starting registration...")

    # 注册用户
    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone: {
                "phone": phone,
                "password": password,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })

    if response.json().get('success'):
        print(f"[OK] Registration successful: {phone}")
    else:
        print(f"[X] Registration failed: {response.json()}")
        return False

    # 验证注册结果
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    if result['users'].get(phone) and result['users'][phone]['password'] == password:
        print(f"[OK] Verification successful: password correct")
        return True
    else:
        print(f"[X] Verification failed: {result}")
        return False

def test_duplicate_register():
    print("\n" + "=" * 50)
    print("测试2: 重复注册应该失败")
    print("=" * 50)

    phone = "13800138000"
    password = "test123"

    # 尝试用相同的手机号注册
    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone: {
                "phone": phone,
                "password": "different",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })

    if not response.json().get('success'):
        print(f"[OK] Correctly blocked duplicate registration")
        return True
    else:
        print(f"[X] Error: allowed duplicate registration")
        return False

def test_clear_users():
    print("\n" + "=" * 50)
    print("测试3: 清空所有用户")
    print("=" * 50)

    # 清空所有用户
    response = requests.post(f'{BASE_URL}/api/save-user', json={"users": {}})

    if response.json().get('success'):
        print(f"[OK] Cleared successfully")

        # 验证
        response = requests.get(f'{BASE_URL}/api/get-users')
        result = response.json()
        if len(result['users']) == 0:
            print(f"[OK] Verification successful: user list is empty")
            return True
        else:
            print(f"[X] Verification failed: user list not empty - {result['users']}")
            return False
    else:
        print(f"[X] Clear failed: {response.json()}")
        return False

def test_orders():
    print("\n" + "=" * 50)
    print("测试4: 测试订单功能")
    print("=" * 50)

    # 创建用户
    phone = "13800138001"
    requests.post(f'{BASE_URL}/api/save-user', json={"users": {phone: {"phone": phone, "password": "123456", "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")}}})

    # 创建订单
    order = {
        "id": "1234567890",
        "clientName": "测试客户",
        "clientPhone": phone,
        "idCard": "110101199001011234",
        "bank": "6222021234567890123",
        "type": "消费贷",
        "desc": "测试订单",
        "status": "pending",
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    response = requests.post(f'{BASE_URL}/api/save-order', json={"order": order})

    if response.json().get('success'):
        print(f"[OK] Order saved successfully")

        # 验证订单
        response = requests.get(f'{BASE_URL}/api/get-users')
        result = response.json()
        orders = result.get('orders', [])
        if orders and len(orders) > 0 and orders[0]['id'] == order['id']:
            print(f"[OK] Order verification successful")
            return True
        else:
            print(f"[X] Order verification failed: {orders}")
            return False
    else:
        print(f"[X] Order save failed: {response.json()}")
        return False

def main():
    print("\n开始测试...\n")

    results = []

    results.append(("注册新用户", test_register()))
    results.append(("重复注册保护", test_duplicate_register()))
    results.append(("清空所有用户", test_clear_users()))
    results.append(("订单功能", test_orders()))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print("\n[X] Some tests failed!")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
