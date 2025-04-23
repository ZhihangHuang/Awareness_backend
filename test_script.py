import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("测试脚本开始运行")
print("测试脚本标准输出", file=sys.stdout)
print("测试脚本错误输出", file=sys.stderr)

for i in range(5):
    logger.info(f"测试循环 {i}")
    print(f"测试循环标准输出 {i}", file=sys.stdout)
    print(f"测试循环错误输出 {i}", file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(5)
