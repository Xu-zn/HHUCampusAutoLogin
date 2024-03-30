from pathlib import Path
import requests
import sys
import toml
import time
import os
from playwright.sync_api import sync_playwright
from loguru import logger

USERNAME: str  # 学号
PASSWORD: str  # 密码
SERVICE: str  # 使用的服务
PORTAL: str  # 登录界面

DETECT_URL: str  # 用于探测的链接
DETECT_VALUE: str
DETECT_INTERVAL: float  # 探测的时间间隔 s


def load_config():
    global USERNAME, PASSWORD, SERVICE, PORTAL, DETECT_URL, DETECT_VALUE, DETECT_INTERVAL
    # 从程序运行目录加载配置文件
    config_file = Path(sys.argv[0]).parent / 'config.toml'
    config = toml.load(config_file)

    login_info = config['login']
    # 初始化登录信息
    USERNAME = login_info.get('username')
    PASSWORD = login_info.get('password')
    SERVICE = login_info.get('service')
    PORTAL = login_info.get('portal')

    detect_info = config['detect']
    # 初始化探测信息
    DETECT_URL = detect_info.get('detect_url')
    DETECT_VALUE = detect_info.get('detect_value')
    DETECT_INTERVAL = detect_info.get('detect_interval')


def detect_net_connection():
    # 探测连接状态，这里模仿的是windows10判断网络连接的方法

    # 另外，其实也可以不用生成器来做，这里去掉while循环，yield改成return
    while True:
        g = requests.get(DETECT_URL, timeout=5)  # noqa
        if g.status_code == 200 and g.text == DETECT_VALUE:
            yield True
        else:
            yield False


def login():  # noqa
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
        )
        page = browser.new_page()

        page.goto(PORTAL)

        # 防止探测失效，做另外的判断
        # 如果是已登录的状态，url是 PORTAL/eportal/success.jsp?userIndex=...
        if page.url.find('success.jsp') != -1:
            logger.warning("探测失效")
            return

        # 输入学号
        page.type("//*[@id='username']", USERNAME)

        # 输入密码，密码框是两层span嵌套，外层 #pwd_tip 激活后才能向内层 #pwd 输入密码
        page.locator("//*[@id='pwd_tip']").click()
        page.fill("//*[@id='pwd']", PASSWORD)

        # 联网服务选择，这里网页上并不是用的select，所以还得模拟点击
        page.locator("//*[@id='selectDisname']").click()
        # 点击服务
        page.locator(f"//*[@id='{SERVICE}']").click()

        # 登录框
        page.locator("//*[@id='loginLink_div']").click()

        # 登录操作完后就关闭浏览器
        page.close()
        browser.close()


if __name__ == "__main__":
    # 获取进程号，如果使用pyinstaller -Fw命令打包，可以通过进程号来杀死进程
    # 打开 PowerShell
    # Stop-Process -Id 进程号
    pid = os.getpid()
    with open("pid", 'w') as f:
        f.write(str(pid))

    load_config()  # 一定要先加载配置
    # 添加日志，
    logger.remove(handler_id=None)
    logger.add(
        Path(sys.argv[0]).parent / 'auto-login.log',
        encoding='utf8',
        format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>',
        rotation="10 MB",
        retention=5
    )
    # 如果没有使用生成器，那下面这一行放while True循环里，且不需要next和detection.close()
    detection = detect_net_connection()
    try:
        while True:
            if not next(detection):
                logger.warning("未连接，尝试连接...")
                login()  # noqa
                # 无需主动验证，让下一循环验证即可，不能删掉continue，因为后面有个sleep(INTERVAL)
                continue
            else:
                logger.info("已连接")
            time.sleep(DETECT_INTERVAL)  # noqa
    except Exception as e:
        logger.error(e)

    finally:
        detection.close()
