# -*- coding: utf-8 -*-
"""
测试注册流程 - 模拟前端JavaScript行为
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def simulate_register_flow():
    """模拟前端注册流程"""
    print("=" * 50)
    print("模拟前端注册流程测试")
    print("=" * 50)

    # 清空所有数据
    print("\n1. 清空所有数据...")
    requests.post(f'{BASE_URL}/api/save-user', json={"users": {}})
    response = requests.get(f'{BASE_URL}/api/get-users')
    print(f"   用户数: {len(response.json()['users'])} (应为0)")

    # 测试注册新用户
    print("\n2. 注册新用户...")
    phone = "13800138000"
    password = "test123"

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
        print(f"   [OK] 注册成功")
    else:
        print(f"   [X] 注册失败: {response.json()}")
        return False

    # 验证
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    if result['users'].get(phone) and result['users'][phone]['password'] == password:
        print(f"   [OK] 验证成功")
    else:
        print(f"   [X] 验证失败")
        return False

    # 测试再次注册同一手机号 - 应该允许覆盖
    print("\n3. 再次注册同一手机号 (应该允许覆盖)...")
    new_password = "newpass123"

    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone: {
                "phone": phone,
                "password": new_password,
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })

    if response.json().get('success'):
        print(f"   [OK] 允许覆盖，成功")
    else:
        print(f"   [X] 阻止覆盖: {response.json()}")
        return False

    # 验证密码已更新
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    if result['users'].get(phone) and result['users'][phone]['password'] == new_password:
        print(f"   [OK] 密码已更新为新密码")
    else:
        print(f"   [X] 密码更新失败: {result.get('users', {}).get(phone)}")
        return False

    # 测试注册不同手机号
    print("\n4. 注册不同手机号...")
    phone2 = "13800138001"
    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone2: {
                "phone": phone2,
                "password": "password2",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })

    if response.json().get('success'):
        print(f"   [OK] 注册成功")
    else:
        print(f"   [X] 注册失败: {response.json()}")
        return False

    # 验证两个用户都存在
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    users = result.get('users', {})

    if users.get(phone) and users.get(phone2):
        print(f"   [OK] 两个用户都存在")
        if users[phone]['password'] == new_password and users[phone2]['password'] == "password2":
            print(f"   [OK] 密码都正确")
        else:
            print(f"   [X] 密码不正确")
            return False
    else:
        print(f"   [X] 用户不完整: {users}")
        return False

    return True

def simulate_clear_and_reuse():
    """模拟清空后重新使用手机号"""
    print("\n" + "=" * 50)
    print("模拟清空后重新使用手机号")
    print("=" * 50)

    # 清空所有数据
    print("\n1. 清空所有数据...")
    requests.post(f'{BASE_URL}/api/save-user', json={"users": {}})
    response = requests.get(f'{BASE_URL}/api/get-users')
    print(f"   用户数: {len(response.json()['users'])} (应为0)")

    # 注册手机号
    print("\n2. 注册手机号...")
    phone = "13800138000"
    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone: {
                "phone": phone,
                "password": "password1",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })
    print(f"   [OK] 注册成功")

    # 清空数据
    print("\n3. 清空所有数据...")
    requests.post(f'{BASE_URL}/api/save-user', json={"users": {}})
    response = requests.get(f'{BASE_URL}/api/get-users')
    print(f"   用户数: {len(response.json()['users'])} (应为0)")

    # 再次注册同一手机号
    print("\n4. 再次注册同一手机号 (应该允许)...")
    response = requests.post(f'{BASE_URL}/api/save-user', json={
        "users": {
            phone: {
                "phone": phone,
                "password": "password2",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
    })

    if response.json().get('success'):
        print(f"   [OK] 允许重新注册成功")
    else:
        print(f"   [X] 阻止重新注册: {response.json()}")
        return False

    # 验证
    response = requests.get(f'{BASE_URL}/api/get-users')
    result = response.json()
    if result['users'].get(phone) and result['users'][phone]['password'] == "password2":
        print(f"   [OK] 手机号可以重新使用")
        return True
    else:
        print(f"   [X] 验证失败: {result.get('users')}")
        return False

def main():
    print("\n开始注册流程测试...\n")

    results = []

    results.append(("新用户注册", simulate_register_flow()))
    results.append(("清空后重用", simulate_clear_and_reuse()))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n[OK] 所有测试通过!")
        return 0
    else:
        print("\n[X] 部分测试失败!")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
