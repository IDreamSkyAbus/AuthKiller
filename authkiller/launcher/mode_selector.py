"""
模式选择器
提供用户引导选择界面，支持多语言
"""

from enum import Enum
from typing import Dict, List, Optional


class Language(Enum):
    """支持的语言枚举"""
    CHINESE = "zh_CN"
    ENGLISH = "en_US"
    JAPANESE = "ja_JP"


class ModeSelector:
    """
    模式选择器类
    负责显示菜单、处理用户选择
    """

    # 多语言文本字典
    TEXTS: Dict[Language, Dict[str, str]] = {
        Language.CHINESE: {
            # 欢迎信息
            "welcome_title": "╔════════════════════════════════════════════════════════╗",
            "welcome_subtitle": "║          AuthKiller - 密码测试工具 v1.0.0             ║",
            "welcome_footer": "╚════════════════════════════════════════════════════════╝",

            # 工具介绍
            "intro_line1": "AuthKiller 是一个高性能的密码测试工具，专为授权安全审计设计。",
            "intro_line2": "支持多种身份验证协议，提供命令行和图形界面两种使用方式。",

            # 警告信息
            "warning_title": "⚠️  重要声明",
            "warning_line1": "本工具仅用于授权安全审计和强度测试！",
            "warning_line2": "未经授权使用可能违反法律，请确保已获得明确书面授权！",

            # 模式选择
            "mode_selection_title": "请选择使用模式：",
            "mode_cli": "1. CLI 命令行模式        - 适合自动化脚本和批量任务",
            "mode_web": "2. Web GUI 模式         - 基于浏览器的图形界面",
            "mode_gui": "3. THINKER GUI 模式     - 桌面应用程序（开发中）",
            "mode_api": "4. API 服务模式         - 提供 REST API 接口",

            # 语言选择
            "language_title": "5. 切换语言 / Switch Language",
            "exit_option": "0. 退出",

            # 提示信息
            "input_prompt": "请输入选项编号 [0-5]: ",
            "invalid_input": "❌ 无效的输入，请输入 0-5 之间的数字",
            "invalid_input_retry": "请重新输入: ",

            # 语言切换
            "language_selection_title": "请选择语言 / Select Language:",
            "lang_chinese": "1. 简体中文",
            "lang_english": "2. English",
            "lang_japanese": "3. 日本語",
            "lang_back": "0. 返回 / Back",

            # 模式启动信息
            "launching_cli": "🚀 启动 CLI 命令行模式...",
            "launching_web": "🚀 启动 Web GUI 模式...",
            "launching_gui": "⚠️  THINKER GUI 模式正在开发中，敬请期待！",
            "launching_api": "🚀 启动 API 服务模式...",

            # 退出信息
            "exit_message": "感谢使用 AuthKiller，再见！",
        },

        Language.ENGLISH: {
            # Welcome messages
            "welcome_title": "╔════════════════════════════════════════════════════════╗",
            "welcome_subtitle": "║          AuthKiller - Password Testing Tool v1.0.0    ║",
            "welcome_footer": "╚════════════════════════════════════════════════════════╝",

            # Introduction
            "intro_line1": "AuthKiller is a high-performance password testing tool designed for",
            "intro_line2": "authorized security audits. Supports multiple authentication protocols.",

            # Warning
            "warning_title": "⚠️  Important Notice",
            "warning_line1": "This tool is ONLY for authorized security audits and testing!",
            "warning_line2": "Unauthorized use may violate laws. Ensure you have explicit written authorization!",

            # Mode selection
            "mode_selection_title": "Select mode:",
            "mode_cli": "1. CLI Mode              - For automation scripts and batch tasks",
            "mode_web": "2. Web GUI Mode          - Browser-based graphical interface",
            "mode_gui": "3. THINKER GUI Mode     - Desktop application (Coming Soon)",
            "mode_api": "4. API Service Mode      - REST API interface",

            # Language selection
            "language_title": "5. Switch Language / 切换语言",
            "exit_option": "0. Exit",

            # Prompts
            "input_prompt": "Enter option number [0-5]: ",
            "invalid_input": "❌ Invalid input, please enter a number between 0-5",
            "invalid_input_retry": "Please try again: ",

            # Language selection menu
            "language_selection_title": "Select Language / 选择语言:",
            "lang_chinese": "1. 简体中文",
            "lang_english": "2. English",
            "lang_japanese": "3. 日本語",
            "lang_back": "0. Back / 返回",

            # Mode launch messages
            "launching_cli": "🚀 Launching CLI mode...",
            "launching_web": "🚀 Launching Web GUI mode...",
            "launching_gui": "⚠️  THINKER GUI mode is under development, coming soon!",
            "launching_api": "🚀 Launching API service mode...",

            # Exit message
            "exit_message": "Thank you for using AuthKiller. Goodbye!",
        },

        Language.JAPANESE: {
            # ウェルカムメッセージ
            "welcome_title": "╔════════════════════════════════════════════════════════╗",
            "welcome_subtitle": "║          AuthKiller - パスワードテストツール v1.0.0    ║",
            "welcome_footer": "╚════════════════════════════════════════════════════════╝",

            # 紹介
            "intro_line1": "AuthKillerは、承認されたセキュリティ監査用に設計された高性能パスワード",
            "intro_line2": "テストツールです。複数の認証プロトコルをサポートしています。",

            # 警告
            "warning_title": "⚠️  重要なお知らせ",
            "warning_line1": "このツールは、承認されたセキュリティ監査とテストのみに使用してください！",
            "warning_line2": "無断使用は法律に違反する可能性があります。明確な書面による承認が必要です！",

            # モード選択
            "mode_selection_title": "モードを選択してください：",
            "mode_cli": "1. CLIモード             - 自動化スクリプトとバッチタスク用",
            "mode_web": "2. Web GUIモード         - ブラウザベースのグラフィカルインターフェース",
            "mode_gui": "3. THINKER GUIモード     - デスクトップアプリケーション（開発中）",
            "mode_api": "4. APIサービスモード     - REST APIインターフェース",

            # 言語選択
            "language_title": "5. 言語を切り替える / Switch Language",
            "exit_option": "0. 終了",

            # プロンプト
            "input_prompt": "オプション番号を入力してください [0-5]: ",
            "invalid_input": "❌ 無効な入力です。0-5の数字を入力してください",
            "invalid_input_retry": "もう一度入力してください: ",

            # 言語選択メニュー
            "language_selection_title": "言語を選択 / Select Language:",
            "lang_chinese": "1. 简体中文",
            "lang_english": "2. English",
            "lang_japanese": "3. 日本語",
            "lang_back": "0. 戻る / Back",

            # モード起動メッセージ
            "launching_cli": "🚀 CLIモードを起動中...",
            "launching_web": "🚀 Web GUIモードを起動中...",
            "launching_gui": "⚠️  THINKER GUIモードは開発中です。お楽しみに！",
            "launching_api": "🚀 APIサービスモードを起動中...",

            # 終了メッセージ
            "exit_message": "AuthKillerをご利用いただきありがとうございました。さようなら！",
        }
    }

    def __init__(self, language: Language = Language.CHINESE):
        """
        初始化模式选择器

        Args:
            language: 默认语言（默认为中文）
        """
        self.language = language

    def get_text(self, key: str) -> str:
        """
        获取当前语言的文本

        Args:
            key: 文本键名

        Returns:
            对应语言的文本
        """
        return self.TEXTS.get(self.language, self.TEXTS[Language.CHINESE]).get(key, key)

    def set_language(self, language: Language):
        """
        设置语言

        Args:
            language: 语言枚举值
        """
        self.language = language

    def display_welcome(self):
        """显示欢迎信息和工具介绍"""
        print("\n" + self.get_text("welcome_title"))
        print(self.get_text("welcome_subtitle"))
        print(self.get_text("welcome_footer"))
        print()

        # 显示工具介绍
        print(self.get_text("intro_line1"))
        print(self.get_text("intro_line2"))
        print()

        # 显示警告信息
        print(self.get_text("warning_title"))
        print(f"  {self.get_text('warning_line1')}")
        print(f"  {self.get_text('warning_line2')}")
        print()

    def display_main_menu(self) -> str:
        """
        显示主菜单

        Returns:
            用户选择的模式
        """
        print("\n" + self.get_text("mode_selection_title"))
        print(f"  {self.get_text('mode_cli')}")
        print(f"  {self.get_text('mode_web')}")
        print(f"  {self.get_text('mode_gui')}")
        print(f"  {self.get_text('mode_api')}")
        print(f"  {self.get_text('language_title')}")
        print(f"  {self.get_text('exit_option')}")
        print()

        # 获取用户输入
        while True:
            try:
                choice = input(self.get_text("input_prompt")).strip()

                if choice == "0":
                    return "exit"
                elif choice == "1":
                    return "cli"
                elif choice == "2":
                    return "web"
                elif choice == "3":
                    return "gui"
                elif choice == "4":
                    return "api"
                elif choice == "5":
                    return "language"
                else:
                    print(self.get_text("invalid_input"))
            except KeyboardInterrupt:
                print("\n")
                return "exit"
            except EOFError:
                print("\n")
                return "exit"

    def display_language_menu(self) -> Optional[Language]:
        """
        显示语言选择菜单

        Returns:
            选择的语言，如果选择返回则为 None
        """
        print("\n" + self.get_text("language_selection_title"))
        print(f"  {self.get_text('lang_chinese')}")
        print(f"  {self.get_text('lang_english')}")
        print(f"  {self.get_text('lang_japanese')}")
        print(f"  {self.get_text('lang_back')}")
        print()

        while True:
            try:
                choice = input(self.get_text("input_prompt")).strip()

                if choice == "0":
                    return None
                elif choice == "1":
                    return Language.CHINESE
                elif choice == "2":
                    return Language.ENGLISH
                elif choice == "3":
                    return Language.JAPANESE
                else:
                    print(self.get_text("invalid_input"))
            except KeyboardInterrupt:
                print("\n")
                return None
            except EOFError:
                print("\n")
                return None

    def run(self) -> str:
        """
        运行模式选择器

        Returns:
            用户选择的模式：cli, web, gui, api, 或 exit
        """
        # 显示欢迎信息
        self.display_welcome()

        # 主循环
        while True:
            # 显示主菜单并获取选择
            choice = self.display_main_menu()

            # 处理语言切换
            if choice == "language":
                new_language = self.display_language_menu()
                if new_language is not None:
                    self.set_language(new_language)
                    print(f"\n✅ 语言已切换 / Language switched / 言語が切り替わりました")
                continue

            # 返回选择的模式
            return choice