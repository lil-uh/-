"""
塔斯汀签到
export TASTI_TOKEN="token1\ntoken2"
cron: 0 0 0 * * *
"""
import os
import requests
import json
from datetime import datetime
import time

def get_tokens():
    """读取环境变量中的 token 列表"""
    raw = os.getenv("TASTI_TOKEN", "")
    tokens = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return tokens

def build_headers(token):
    """构造请求头"""
    return {
        'Host': 'sss-web.tastientech.com',
        'Connection': 'keep-alive',
        'user-token': token,
        'channel': '1',
        'content-type': 'application/json',
        'version': '3.13.0',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.55(0x1800372f) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx557473f23153a429/414/page-frame.html',
        'Accept-Language': 'zh-cn',
        'Accept': '*/*'
    }

def get_member_info(headers):
    """获取会员信息"""
    url = 'https://sss-web.tastientech.com/api/intelligence/member/getMemberDetail'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            nick_name = result.get("nickName")  
            phone = result.get("phone")
            if phone and len(phone) >= 7:
                masked_phone = phone[:3] + "****" + phone[-4:]
            else:
                masked_phone = "未知"
            print(f"👤 昵称: {nick_name or '未知'}, 📱 手机号: {masked_phone}")
            return nick_name or "Unknown", phone or "0000000000"
        else:
            print(f"❌ 获取会员信息失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"🚨 获取会员信息异常：{str(e)}")

    return "Unknown", "0000000000"

def calculate_activity_id():
    """动态计算 activityId（一直递增）"""
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    base_year = 2025
    base_month = 5
    base_activity_id = 59

    # 计算距离基准时间的月份差
    months_passed = (current_year - base_year) * 12 + (current_month - base_month)
    activity_id = base_activity_id + months_passed
    return activity_id

def sign_in(headers, name, phone):
    """执行签到"""
    activity_id = calculate_activity_id()
    print(f"📅 当前 activityId: {activity_id}")

    url = 'https://sss-web.tastientech.com/api/sign/member/signV2'
    payload = {
        "activityId": activity_id,
        "memberName": name,
        "memberPhone": phone
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            res = response.json()
            res_code = res.get("code")
            msg = res.get("msg", "")
            result = res.get("result", {})

            if res_code == 200:
                rewards = result.get("rewardInfoList", [])
                reward_names = [item.get("rewardName", "未知奖励") for item in rewards]
                continuous_days = result.get("continuousNum", 0)

                print(f"✅ 签到成功！连续签到：{continuous_days} 天")
                print(f"🎁 获得奖励：{', '.join(reward_names) if reward_names else '无'}")
            elif res_code == 500:
                print(f"🔁 {msg}")
            else:
                print(f"⚠️ 未知签到状态（code={res_code}）：{msg}")
        else:
            print(f"❌ 签到失败，HTTP 状态码：{response.status_code}")
            print(response.text)
    except Exception as e:
        print("🚨 签到请求异常：", str(e))

def process_account(index, token):
    """处理单个账号"""
    print(f"========== 🧾 账号 {index} ==========")
    headers = build_headers(token)
    name, phone = get_member_info(headers)
    sign_in(headers, name, phone)
    print("\n")

def main():
    tokens = get_tokens()
    if not tokens:
        print("⚠️ 未设置 TASTI_TOKEN 环境变量或内容为空")
        print("👉 请设置方式如下（Linux/macOS）：")
        print("export TASTI_TOKEN='token1\ntoken2\ntoken3'")
        return

    print(f"🔍 检测到 {len(tokens)} 个账号，开始执行...\n")

    for index, token in enumerate(tokens, 1):
        process_account(index, token)
        time.sleep(1)  # 避免过快请求

if __name__ == "__main__":
    main()
