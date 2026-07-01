"""
AuthKiller Web GUI
基于 Flask + LayUI 的 Web 界面
"""

from authkiller.web.app import create_app, run_web

__all__ = ["create_app", "run_web"]