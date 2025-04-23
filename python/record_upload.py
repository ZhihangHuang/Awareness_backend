import time
import json
import requests
import sys
import random
from datetime import datetime

# ========================= 配置区域 =========================
API_BASE = "https://awareness-backend-x28a.onrender.com/api"
CONFIG_URL = f"{API_BASE}/get-config/"
UPLOAD_URL = f"{API_BASE}/sensor_data/"
# ============================================================

# 获取配置（user_id, activity_id, data_type, email, password）
try:
    res = requests.get(CONFIG_URL)
    res.raise_for_status()
    config = res.json()

    if "user_id" not in config:
        print(f"❌ 配置内容不完整：{config}")
        exit()

    USER_ID = config["user_id"]
    ACTIVITY_ID = config["activity_id"]
    DATA_TYPE = config.get("data_type", "eeg")
    EMAIL = config.get("email", "N/A")

    print(f"Get configuration successfully: user_id={USER_ID}, activity_id={ACTIVITY_ID}, data_type={DATA_TYPE}")
except Exception as e:
    print(f"❌ 配置获取失败: {e}")
    exit()

headers = {
    "Content-Type": "application/json"
}

def process_eeg_data(eeg_data):
    """直接处理EEG数据的全局函数"""
    try:
        eeg_values = eeg_data['eeg']
        counter_value = eeg_values[0]  # 数据计数器值
        t7_value = eeg_values[2]  # T7电极的值
        
        # 只处理能被10整除的计数值，减少频率
        if counter_value % 10 == 0:
            print(f"\nEEG counter: {counter_value}, T7 value: {t7_value}")
            
            payload = {
                "user": USER_ID,
                "activity": ACTIVITY_ID,
                "data_type": DATA_TYPE,
                "value": t7_value,
                "unit": "uV",
                "recorded_at": datetime.now().isoformat(),
                "session_id": f"session_{datetime.now().strftime('%Y%m%d%H%M')}"
            }
            
            print(f"Prepare to send data: {payload}")
            
            try:
                res = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=5)
                print(f"Request status code: {res.status_code}")
                
                if res.status_code == 201:
                    print(f" Uploaded EEG successfully: {t7_value}")
                    return True
                else:
                    print(f"❌ 上传失败 [{res.status_code}]: {res.text}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求异常: {e}")
                return False
    except Exception as e:
        print(f"❌ 处理数据异常: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def upload_sample_data():
    """上传一个样本数据点"""
    # 生成一个模拟的EEG数据值（4100-4300范围内）
    value = 4100 + random.random() * 200
    
    payload = {
        "user": USER_ID,
        "activity": ACTIVITY_ID,
        "data_type": DATA_TYPE,
        "value": value,
        "unit": "uV",
        "recorded_at": datetime.now().isoformat(),
        "session_id": f"session_{datetime.now().strftime('%Y%m%d%H%M')}"
    }
    
    print(f"Upload mock data: {payload}")
    
    try:
        res = requests.post(UPLOAD_URL, json=payload, headers=headers, timeout=5)
        print(f"Request status code: {res.status_code}")
        
        if res.status_code == 201:
            print(f"Uploaded successfully: {value}")
            return True
        else:
            print(f"❌ 上传失败 [{res.status_code}]: {res.text}")
            return False
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Start uploading data")
    count = 0
    try:
        while True:
            success = upload_sample_data()
            count += 1
            if success:
                print(f"Successfully uploaded {count} data points")
            else:
                print(f"Upload failed, total: {count} attempts")
            
            # 每2秒上传一次
            time.sleep(2)
    except KeyboardInterrupt:
        print(f" Manual interruption, a total of {count} data points uploaded")