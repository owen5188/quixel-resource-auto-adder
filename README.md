# Quixel Bridge 资源自动添加工具

这是一个自动添加 Quixel Bridge 免费资源到个人库的 Python 脚本。

## 功能特点

- 自动检测并添加 Quixel Bridge 的免费资源
- 自动记录已处理的资源，避免重复添加
- 支持断点续传
- 自动检测登录状态
- 跨平台支持（Windows/MacOS/Linux）

## 使用要求

- Python 3.7+
- Chrome 浏览器
- DrissionPage 4.0.0+

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/owen5188/quixel-resource-auto-adder.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行脚本：
```bash
python auto_add_to_library.py
```

2. 首次运行时，需要设置 Chrome 用户数据目录
3. 如果未登录，请按提示在浏览器中完成登录
4. 登录后，脚本会自动开始添加免费资源

## 注意事项

- 请确保您的网络连接稳定
- 首次运行时需要登录 Quixel Bridge 账号
- 脚本会自动记录已添加的资源，避免重复添加

## 版本历史

### 2.0.0
- 使用 DrissionPage 重构代码，提升稳定性
- 添加跨平台支持
- 优化资源检测和添加逻辑
- 添加日志记录功能
- 改进错误处理机制

### 1.0.0
- 初始版本发布