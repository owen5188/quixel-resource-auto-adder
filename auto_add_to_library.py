from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
import logging
import configparser
import os
import sys
import platform
import time

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
        self.page = None
        self.config = self.load_config()
        self.system = platform.system()
        self.processed_links_file = 'processed_links.txt'
        self.last_resource_file = 'last_resource.txt'
        self.processed_links = set()
        self.resource_list_url = "https://www.fab.com/zh-cn/search?free=true"
        self.setup_page()

    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()

        # 检查配置文件是否存在
        if not os.path.exists('config.ini'):
            self.create_default_config()

        config.read('config.ini', encoding='utf-8')
        return config

    @staticmethod
    def create_default_config():
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

        return os.path.expanduser(user_data_dir)

    def setup_page(self):
        """设置页面"""
        try:
            logger.info(f"操作系统: {self.system}")
            logger.info(f"Python版本: {sys.version}")

            user_data_dir = self.get_chrome_user_data_dir()
            if not os.path.exists(user_data_dir):
                raise Exception(f"Chrome用户数据目录不存在: {user_data_dir}")

            logger.info(f"使用Chrome用户数据: {user_data_dir}")
            
            # 创建配置
            co = ChromiumOptions()
            co.set_paths(user_data_path=user_data_dir)
            
            # 使用配置创建页面
            self.page = ChromiumPage(co)
            logger.info("浏览器初始化成功")

            print("\n" + "=" * 50)
            print("提示：正在检测您的登录状态，如您已登录Fab，")
            print("您可以移动或最小化浏览器窗口")
            print("脚本会在后台继续运行")
            print("如未登录，请按下面的提示登录")
            print("=" * 50 + "\n")

        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            if self.page:
                self.page.quit()
            raise

    def save_last_resource(self, resource_info):
        """保存最后处理的资源信息"""
        try:
            with open(self.last_resource_file, 'w', encoding='utf-8') as f:
                f.write(resource_info)
        except Exception as e:
            logger.error(f"保存资源信息时出错: {str(e)}")

    def load_last_resource(self):
        """加载上次处理的资源信息"""
        try:
            if os.path.exists(self.last_resource_file):
                with open(self.last_resource_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            logger.error(f"加载资源信息时出错: {str(e)}")
            return None

    def load_processed_links(self):
        """加载已处理的链接"""
        try:
            if os.path.exists(self.processed_links_file):
                with open(self.processed_links_file, 'r', encoding='utf-8') as f:
                    return set(line.strip() for line in f if line.strip())
            return set()
        except Exception as e:
            logger.error(f"加载已处理链接时出错: {str(e)}")
            return set()

    def save_processed_link(self, link):
        """保存已处理的链接"""
        try:
            with open(self.processed_links_file, 'a', encoding='utf-8') as f:
                f.write(f"{link}\n")
        except Exception as e:
            logger.error(f"保存已处理链接时出错: {str(e)}")

    def check_login_status(self):
        """检查登录状态"""
        try:
            # 访问 Quixel 页面
            self.page.get("https://www.fab.com/zh-cn/sellers/Quixel")
            time.sleep(2)

            # 检查是否存在登录按钮
            login_button = self.page.ele(
                'xpath://button[contains(@class, "fabkit-Avatar-root") and @aria-label="登录"]'
            )
            
            if login_button:
                logger.info("检测到未登录状态，请先登录")
                print("\n" + "=" * 50)
                print("请在浏览器中完成以下操作：")
                print("1. 点击右上角的登录按钮")
                print("2. 使用您的账号登录")
                print("3. 确保成功登录到 Quixel 页面")
                print("4. 登录成功后，请返回命令行按回车键继续")
                print("=" * 50 + "\n")
                input("请在完成登录后按回车键继续...")
                
                # 刷新页面并再次检查登录状态
                self.page.get("https://www.fab.com/zh-cn/sellers/Quixel")
                time.sleep(2)
                if self.page.ele(
                    'xpath://button[contains(@class, "fabkit-Avatar-root") and @aria-label="登录"]'
                ):
                    raise Exception("登录失败，请确保成功登录后再运行程序")
                
                logger.info("登录状态确认成功")
                return True
            
            logger.info("已检测到登录状态")
            return True

        except Exception as e:
            logger.error(f"检查登录状态时出错: {str(e)}")
            raise

    def add_resources_to_library(self):
        """添加所有资源到库中"""
        try:
            if not self.check_login_status():
                return

            # 加载已处理的链接
            self.processed_links = self.load_processed_links()
            
            # 确保访问正确的资源列表页面
            self.resource_list_url = "https://www.fab.com/zh-cn/sellers/Quixel"
            
            last_height = 0
            pending_resources = set()  # 使用set避免重复
            no_new_height_count = 0
            
            while True:
                try:
                    # 确保在正确的页面上
                    current_url = self.page.url
                    if "fab.com/zh-cn/sellers/Quixel" not in current_url:
                        logger.info("页面已改变，重新导航到资源列表页...")
                        self.page.get(self.resource_list_url)
                        time.sleep(3)
                    
                    # 获取当前页面高度
                    current_height = self.page.run_js('return document.documentElement.scrollHeight')
                    
                    # 获取并处理免费资源
                    free_resources = self.page.eles(
                        'xpath://div[text()="免费"]/ancestor::li//a[contains(@href, "/listings/")]'
                    )
                    
                    current_resources_count = len(free_resources)
                    logger.info(f"当前页面上共有 {current_resources_count} 个免费资源")

                    # 收集未添加的资源URL
                    for element in free_resources:
                        link = element.link
                        if (link and 
                            link not in self.processed_links and
                            link not in pending_resources):
                            
                            pending_resources.add(link)
                            logger.info(f"找到未添加的资源: {link}")

                    # 处理收集到的资源
                    if pending_resources:
                        resources_to_process = list(pending_resources)[:20]
                        logger.info(f"开始处理 {len(resources_to_process)} 个新资源...")
                        
                        for resource_url in resources_to_process:
                            try:
                                self.page.get(resource_url)
                                time.sleep(2)
                                
                                add_button = self.page.ele('css:button.fabkit-Button--secondary.fabkit-Button--fullWidth._A6MYYt2')
                                
                                if add_button:
                                    add_button.click()
                                    time.sleep(1)
                                    self.processed_links.add(resource_url)
                                    self.save_processed_link(resource_url)
                                    pending_resources.remove(resource_url)
                                    logger.info(f"已添加资源: {resource_url}")
                                else:
                                    logger.error(f"未找到添加按钮: {resource_url}")
                                    pending_resources.remove(resource_url)  # 移除无法添加的资源
                                    
                            except Exception as e:
                                logger.error(f"添加资源失败: {resource_url}, 错误: {str(e)}")
                        
                        # 返回资源列表页
                        self.page.get(self.resource_list_url)
                        time.sleep(3)

                    # 滚动页面
                    self.page.run_js('window.scrollTo(0, document.documentElement.scrollHeight)')
                    time.sleep(2)

                    # 检查页面高度是否变化
                    if current_height > last_height:
                        logger.info(f"页面高度增加: {current_height - last_height}px")
                        last_height = current_height
                        no_new_height_count = 0
                    else:
                        no_new_height_count += 1
                        logger.info(f"页面高度未变化 ({no_new_height_count}/5)")
                        
                        if no_new_height_count >= 5:
                            logger.info("尝试更大范围的滚动...")
                            self.page.run_js('window.scrollTo(0, document.documentElement.scrollHeight * 2)')
                            time.sleep(3)
                            
                            new_height = self.page.run_js('return document.documentElement.scrollHeight')
                            if new_height > current_height:
                                logger.info("检测到新内容，继续处理")
                                no_new_height_count = 0
                                continue
                            elif pending_resources:
                                logger.info(f"处理剩余的 {len(pending_resources)} 个资源...")
                                continue

                except Exception as e:
                    logger.error(f"处理页面时发生错误: {str(e)}")
                    time.sleep(1)
                    continue

        except Exception as e:
            logger.error(f"处理页面时发生错误: {str(e)}")

    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()


def main():
    print("\n欢迎使用 Quixel 资源自动添加工具！\n")
    adder = None

    try:
        adder = QuixelResourceAdder()
        adder.add_resources_to_library()

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        input("\n按回车键退出...")
    finally:
        if adder:
            adder.close()


if __name__ == "__main__":
    main()