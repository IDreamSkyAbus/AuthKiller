"""
AuthKiller 友好安装引导脚本
引导用户安装、配置和启动
"""
import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """显示欢迎横幅"""
    print("""
============================================================
                                                           
        AuthKiller 友好安装引导                           
     AuthKiller Friendly Installation Wizard              
                                                           
  [!] 仅用于授权安全审计和强度测试！                       
                                                           
============================================================
    """)


def select_language():
    """选择语言"""
    print("\n" + "=" * 60)
    print("  Select Language / 选择语言 / 言語選択")
    print("=" * 60)
    print("  1. 中文 (zh-CN) - 默认")
    print("  2. English (en-US)")
    print("  3. 日本語 (ja-JP)")
    print("=" * 60)

    choice = input("请选择 [1]: ").strip() or "1"

    lang_map = {"1": "zh-CN", "2": "en-US", "3": "ja-JP"}
    return lang_map.get(choice, "zh-CN")


def check_dependencies():
    """检查依赖"""
    print("\n[1/4] 检查依赖...")

    required = {
        "aiohttp": "aiohttp",
        "aiofiles": "aiofiles",
        "tqdm": "tqdm",
        "colorama": "colorama",
        "yaml": "pyyaml",
        "flask": "flask",
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (缺失)")
            missing.append(package)

    return missing


def install_dependencies(missing):
    """安装缺失的依赖"""
    if not missing:
        print("\n[2/4] 所有依赖已安装 ✓")
        return True

    print(f"\n[2/4] 需要安装 {len(missing)} 个依赖:")
    for pkg in missing:
        print(f"  - {pkg}")

    choice = input("\n是否自动安装？(y/n) [y]: ").strip().lower() or "y"

    if choice != "y":
        print("\n请手动运行: pip install " + " ".join(missing))
        return False

    try:
        for pkg in missing:
            print(f"\n正在安装 {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("\n[2/4] 所有依赖安装完成 ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] 安装失败: {e}")
        return False


def install_package():
    """安装authkiller包"""
    print("\n[3/4] 安装 AuthKiller...")

    setup_py = Path("setup.py")
    if not setup_py.exists():
        print("  ✗ setup.py 不存在")
        return False

    try:
        subprocess.check_call([sys.executable, "setup.py", "develop"])
        print("  ✓ AuthKiller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ 安装失败: {e}")
        return False


def launch_web():
    """启动Web界面"""
    print("\n[4/4] 启动 Web GUI...")

    # 尝试自动打开浏览器
    import threading
    import time
    import webbrowser

    def open_browser():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:37496")

    threading.Thread(target=open_browser, daemon=True).start()

    # 启动Web服务
    try:
        from authkiller.web.app import run_web
        run_web(host="127.0.0.1", port=37496, debug=False, auto_port=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] 服务已停止")


def launch_mode(mode):
    """启动指定模式"""
    if mode == "1":
        # Web GUI
        launch_web()
    elif mode == "2":
        # THINKER GUI
        try:
            from authkiller.gui.run_gui import launch_gui
            launch_gui()
        except ImportError:
            print("\n[ERROR] GUI模块不可用")
    elif mode == "3":
        # CLI
        print("\n" + "=" * 60)
        print("  CLI 命令行模式")
        print("=" * 60)
        print("\n使用示例:")
        print("  authkiller attack --config config.json")
        print("  authkiller attack --url http://example.com/login \\")
        print("    --users users.txt --passwords passwords.txt")
        print("\n更多: authkiller --help")
    elif mode == "4":
        # API
        from authkiller.web.app import create_app
        app = create_app()
        print("\n" + "=" * 60)
        print("  AuthKiller API 服务")
        print("  http://127.0.0.1:5000")
        print("=" * 60)
        try:
            app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)
        except KeyboardInterrupt:
            print("\n\n[INFO] API服务已停止")


def main():
    """主函数"""
    print_banner()

    # 1. 选择语言
    lang = select_language()

    # 2. 检查依赖
    missing = check_dependencies()
    if not install_dependencies(missing):
        print("\n请先安装依赖后再运行")
        return

    # 3. 安装包
    if not install_package():
        print("\n包安装失败")
        return

    # 4. 选择界面并启动
    print("\n" + "=" * 60)
    print("  选择界面模式 / Select Interface Mode")
    print("=" * 60)
    print("  1. Web GUI  - 浏览器界面（推荐，自动打开）")
    print("  2. THINKER  - 桌面图形界面")
    print("  3. CLI      - 命令行界面")
    print("  4. API      - API服务模式")
    print("=" * 60)

    choice = input("请选择 [1]: ").strip() or "1"

    print(f"\n[INFO] 启动模式 {choice}...")
    print("=" * 60)

    try:
        launch_mode(choice)
    except KeyboardInterrupt:
        print("\n\n[INFO] 已退出")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 已取消")
