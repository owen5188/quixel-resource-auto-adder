import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import configparser
import os
import sys
import platform

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auto_add.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class QuixelResourceAdder:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.config = self.load_config()
        self.system = platform.system()  # 获取操作系统类型
        self.setup_driver()

    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()

        # 检查配置文件是否存在
        if not os.path.exists('config.ini'):
            self.create_default_config()

        config.read('config.ini', encoding='utf-8')
        return config

    def create_default_config(self):
        """创建默认配置文件"""
        config = configparser.ConfigParser()
        config['Chrome'] = {
            'user_data_dir': ''
        }
        config['Settings'] = {
            'page_load_wait': '3',
            'click_wait': '2',
            'max_retries': '3'
        }

        with open('config.ini', 'w', encoding='utf-8') as f:
            config.write(f)

    def get_default_chrome_path(self):
        """根据操作系统获取默认的Chrome用户数据目录路径"""
        if self.system == "Windows":
            return os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
        elif self.system == "Darwin":  # macOS
            return os.path.expanduser('~/Library/Application Support/Google/Chrome')
        else:  # Linux
            return os.path.expanduser('~/.config/google-chrome')

    def get_chrome_user_data_dir(self):
        """获取Chrome用户数据目录"""
        user_data_dir = self.config.get('Chrome', 'user_data_dir', fallback='')

        if not user_data_dir:
            print("\n" + "=" * 50)
            print("请输入Chrome用户数据目录路径。")
            if self.system == "Windows":
                print("通常位于：C:\\Users\\用户名\\AppData\\Local\\Google\\Chrome\\User Data")
            elif self.system == "Darwin":  # macOS
                print("通常位于：~/Library/Application Support/Google/Chrome")
            else:  # Linux
                print("通常位于：~/.config/google-chrome")
            print("您可以在Chrome浏览器地址栏输入 chrome://version 查看")
            print("=" * 50 + "\n")

            default_path = self.get_default_chrome_path()
            user_input = input(f"请输入路径 (直接回车使用默认路径: {default_path}): ").strip()
            user_data_dir = user_input if user_input else default_path

            # 保存到配置文件
            self.config['Chrome']['user_data_dir'] = user_data_dir
            with open('config.ini', 'w', encoding='utf-8') as f:
                self.config.write(f)

        return os.path.expanduser(user_data_dir)  # 展开用户目录的波浪号

    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            # 添加版本信息日志
            logger.info(f"操作系统: {self.system}")
            logger.info(f"Python版本: {sys.version}")

            options = uc.ChromeOptions()
            options.add_argument('--window-size=1280,720')
            options.add_argument('--window-position=600,300')

            user_data_dir = self.get_chrome_user_data_dir()

            if not os.path.exists(user_data_dir):
                raise Exception(f"Chrome用户数据目录不存在: {user_data_dir}")

            logger.info(f"使用Chrome用户数据目录: {user_data_dir}")
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--profile-directory=Default')

            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 20)

            # 添加Chrome版本信息日志
            chrome_version = self.driver.capabilities['browserVersion']
            logger.info(f"Chrome版本: {chrome_version}")
            logger.info("浏览器驱动初始化成功")

            print("\n" + "=" * 50)
            print("提示：您可以移动或最小化浏览器窗口")
            print("脚本会在后台继续运行")
            print("=" * 50 + "\n")

        except Exception as e:
            logger.error(f"驱动初始化失败: {str(e)}")
            if self.driver:
                self.driver.quit()
            raise

    def wait_for_manual_login(self):
        """等待人工登录"""
        try:
            logger.info("请在浏览器中手动登录...")

            # 打开登录页面
            self.driver.get("https://www.fab.com/zh-cn/sellers/Quixel")

            # 提示用户操作
            print("\n" + "=" * 50)
            print("请在打开的浏览器中完成以下操作：")
            print("1. 手动登录您的账号")
            print("2. 确保成功登录到 Quixel 页面")
            print("3. 登录成功后，请返回命令行按回车键继续")
            print("=" * 50 + "\n")

            input("请在完成登录后按回车键继续...")

            # 等待登录成功
            time.sleep(3)

            logger.info("继续执行自动化操作...")
            return True

        except Exception as e:
            logger.error(f"等待登录过程中发生错误: {str(e)}")
            raise

    def scroll_page(self, amount):
        """模拟人工拖动滚动条"""
        try:
            # 获取当前滚动位置
            current_position = int(self.driver.execute_script("return window.pageYOffset;"))
            target_position = current_position + amount

            # 获取页面总高度
            total_height = int(self.driver.execute_script(
                "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
                "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
                "document.documentElement.offsetHeight);"
            ))

            # 确保不会滚动超过页面总高度
            target_position = min(target_position, total_height - 800)

            # 模拟平滑滚动，每次滚动一小段距离
            step = 100 if amount > 0 else -100
            for pos in range(current_position, target_position, step):
                self.driver.execute_script(f"window.scrollTo(0, {int(pos)});")
                time.sleep(0.05)

            # 最后滚动到目标位置
            self.driver.execute_script(f"window.scrollTo(0, {int(target_position)});")
            time.sleep(1)

            # 返回实际滚动位置
            return int(self.driver.execute_script("return window.pageYOffset;"))

        except Exception as e:
            logger.error(f"滚动页面时出错: {str(e)}")
            return current_position  # 返回当前位置而不是 None

    def add_resources_to_library(self):
        """添加所有资源到库中"""
        processed_links = set()  # 用于存储已处理的链接
        scroll_position = 0  # 记录当前滚动位置
        no_new_resources_count = 0  # 连续没有新资源的次数

        while True:
            try:
                # 确保在正确的面上
                if "fab.com/zh-cn/sellers/Quixel" not in self.driver.current_url:
                    self.driver.get("https://www.fab.com/zh-cn/sellers/Quixel")
                    scroll_position = 0  # 重置滚动位置

                # 等待资源列表加载完成
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul li"))
                )
                time.sleep(2)

                # 恢复到之前的滚动位置
                if scroll_position > 0:
                    self.scroll_page(scroll_position)
                    time.sleep(2)

                # 查找当前可见区域内带有"免费"标记的资源卡片
                free_resources = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'fabkit-Typography-root') and contains(text(), '免费')]"
                    "/ancestor::li//a[contains(@href, '/listings/')]"
                )

                # 获取未处理的资源链接
                new_links = []
                for element in free_resources:
                    try:
                        link = element.get_attribute("href")
                        # 确保链接有效��未处理过
                        if link and link not in processed_links:
                            new_links.append(link)
                            processed_links.add(link)  # 立即标记为已处理，避免重复添加
                    except:
                        continue

                logger.info(f"找到 {len(new_links)} 个未处理的免费资源")

                # 如果找到未处理的资源，先处理它们
                if len(new_links) > 0:
                    # 处理每个免费资源
                    for link in new_links:
                        try:
                            logger.info(f"正在处理资源: {link}")

                            # 访问资源详情页
                            self.driver.get(link)
                            time.sleep(2)

                            # 查找并点击"添加到我的库"按钮
                            add_button = self.wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH,
                                    "//button[contains(@class, 'fabkit-Button-root')]//span[contains(@class, 'fabkit-Button-label') and text()='添加到我的库']/.."
                                ))
                            )

                            # 滚动到按钮可见
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                            time.sleep(1)

                            # 点击按钮
                            add_button.click()
                            logger.info("点击了添加到库按钮")
                            time.sleep(2)

                            # 返回列表页并恢复滚动位置
                            self.driver.get("https://www.fab.com/zh-cn/sellers/Quixel")
                            time.sleep(3)
                            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                            time.sleep(2)

                            logger.info(f"成功添加资源: {link}")

                        except Exception as e:
                            logger.error(f"处理资源时出错: {str(e)}")
                            continue

                    no_new_resources_count = 0  # 重置计数器

                else:
                    # 如果当前视图没有未处理的资源，则滚动页面
                    no_new_resources_count += 1
                    if no_new_resources_count >= 5:  # 连续5次没有新资源
                        # 尝试大范围滚动
                        new_position = self.scroll_page(3000)
                        if new_position is not None and new_position > scroll_position:
                            scroll_position = new_position
                            no_new_resources_count = 0
                        else:
                            logger.info("连续多次未发现新资源，任务完成")
                            break
                    else:
                        # 正常滚动
                        new_position = self.scroll_page(1500)
                        if new_position is not None:
                            scroll_position = new_position
                        time.sleep(2)  # 等待新内容加载

            except Exception as e:
                logger.error(f"处理页面时发生错误: {str(e)}")
                time.sleep(3)
                continue

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def main():
    print("\n欢迎使用 Quixel 资源自动添加工具！\n")

    try:
        adder = QuixelResourceAdder()

        # 等待人工登录
        adder.wait_for_manual_login()

        # 开始添加资源
        adder.add_resources_to_library()

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        input("\n按回车键退出...")
    finally:
        if adder:
            adder.close()


if __name__ == "__main__":
    main()