"""
启动器主文件
根据用户选择启动对应的运行模式
"""

import sys
import os
import subprocess
from pathlib import Path

from authkiller.launcher.mode_selector import ModeSelector, Language


class Launcher:
    """
    启动器类
    负责启动不同的运行模式
    """

    def __init__(self, language: Language = Language.CHINESE):
        """
        初始化启动器

        Args:
            language: 默认语言
        """
        self.mode_selector = ModeSelector(language)

    def launch_cli(self):
        """启动 CLI 命令行模式"""
        print("\n" + self.mode_selector.get_text("launching_cli"))
        print("=" * 60)
        print()

        # 调用 CLI 主入口
        try:
            from authkiller.cli.main import main as cli_main
            # 显示帮助信息
            print("提示：以下参数可用：")
            print("  attack    - 启动新的密码测试任务")
            print("  resume    - 从断点恢复任务")
            print("  report    - 生成报告")
            print("  web       - 启动Web界面")
            print()
            print("使用 'authkiller --help' 查看详细帮助信息")
            print()

            # 启动交互式CLI
            cli_main()

        except ImportError as e:
            print(f"❌ 无法导入 CLI 模块: {e}")
            print("请确保已正确安装所有依赖")
            sys.exit(1)
        except SystemExit:
            # CLI 正常退出
            pass
        except Exception as e:
            print(f"❌ 启动 CLI 模式失败: {e}")
            sys.exit(1)

    def launch_web(self):
        """启动 Web GUI 模式"""
        print("\n" + self.mode_selector.get_text("launching_web"))
        print("=" * 60)
        print()

        try:
            from authkiller.web.app import run_web

            # 启动 Web 服务
            run_web(
                host='127.0.0.1',
                port=37496,
                debug=False,
                auto_port=True
            )

        except ImportError as e:
            print(f"❌ 无法导入 Web 模块: {e}")
            print("请确保已安装 Flask: pip install flask")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n✅ Web 服务已停止")
        except Exception as e:
            print(f"❌ 启动 Web GUI 模式失败: {e}")
            sys.exit(1)

    def launch_gui(self):
        """启动 THINKER GUI 模式（桌面应用）"""
        print("\n" + self.mode_selector.get_text("launching_gui"))
        print()
        print("THINKER GUI 是一个跨平台桌面应用程序，目前正在开发中。")
        print("完成后将提供：")
        print("  - 直观的图形界面")
        print("  - 实时进度监控")
        print("  - 可视化结果展示")
        print("  - 配置文件管理")
        print()
        print("敬请期待！")
        print()

        # 返回主菜单
        input("按回车键返回主菜单...")
        self.run()

    def launch_api(self):
        """启动 API 服务模式"""
        print("\n" + self.mode_selector.get_text("launching_api"))
        print("=" * 60)
        print()

        # 检查 API 模块是否存在
        api_module_path = Path(__file__).parent.parent / "api"

        if not api_module_path.exists():
            print("⚠️  API 服务模块尚未实现")
            print()
            print("计划功能：")
            print("  - RESTful API 接口")
            print("  - 任务创建和管理")
            print("  - 实时状态查询")
            print("  - 结果导出")
            print()
            print("敬请期待！")
            print()
            input("按回车键返回主菜单...")
            self.run()
            return

        try:
            # 如果 API 模块存在，启动它
            from authkiller.api.server import run_api_server

            run_api_server(
                host='127.0.0.1',
                port=8080
            )

        except ImportError as e:
            print(f"❌ 无法导入 API 模块: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n✅ API 服务已停止")
        except Exception as e:
            print(f"❌ 启动 API 服务失败: {e}")
            sys.exit(1)

    def run(self):
        """运行启动器主循环"""
        try:
            # 获取用户选择的模式
            mode = self.mode_selector.run()

            # 根据选择启动对应模式
            if mode == "exit":
                print("\n" + self.mode_selector.get_text("exit_message"))
                sys.exit(0)
            elif mode == "cli":
                self.launch_cli()
            elif mode == "web":
                self.launch_web()
            elif mode == "gui":
                self.launch_gui()
            elif mode == "api":
                self.launch_api()
            else:
                print(f"❌ 未知模式: {mode}")
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n" + self.mode_selector.get_text("exit_message"))
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 启动器发生错误: {e}")
            sys.exit(1)


def main():
    """
    启动器主入口函数
    可通过 authkiller-launch 命令调用
    """
    launcher = Launcher()
    launcher.run()


if __name__ == '__main__':
    main()