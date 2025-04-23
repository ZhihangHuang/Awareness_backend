import json
import time
from cortex import Cortex

CLIENT_ID = "ptXSvmu17TMeS0ATgLkid3ZY0pmTUwPSUNYjso81"
CLIENT_SECRET = "dgEoN6S0sO5SvoeIkc55df7QqEkN2lRLN8c03KSasusZbtNwgdEDIG5LsvzF7gX6t3Lmw26HUJanhxMhiARPZElZYNBmOwK82tqTmGsDEGHq9yzjZfZCueWyRkQrBt6z"
class AutoReconnectRecorder:
    def __init__(self):
        self.cortex = Cortex(CLIENT_ID, CLIENT_SECRET)
    
    def run(self):
        try:
            self.cortex.open()
            self.cortex.authorize()

            # 自动尝试多次查询设备
            for _ in range(5):
                print("🔄 尝试查询设备...")
                self.cortex.query_headset()
                time.sleep(3)
                if self.cortex.isHeadsetConnected:
                    print("✅ 设备已连接")
                    break
            else:
                print("❌ 未找到可用设备，退出程序")
                return

            # 创建会话并订阅数据
            self.cortex.create_session()
            self.cortex.sub_request(["eeg", "pow"])
            print("🎯 已创建会话并订阅 EEG / 频段数据")

            # 简单接收数据输出
            while True:
                msg = self.cortex.ws.recv()
                print(f"[📩 Data] {msg}")

        except Exception as e:
            print(f"❌ 异常发生: {e}")
        finally:
            self.cortex.close()

if __name__ == "__main__":
    AutoReconnectRecorder().run()
