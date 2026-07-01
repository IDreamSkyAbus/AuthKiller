"""
AuthKiller - 密码测试工具安装配置
仅用于授权安全审计和强度测试
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="authkiller",
    version="1.0.0",
    author="IDrameSkyAbuas",
    author_email="admin@pubnexus.cn",
    description="Password testing tool for authorized security audits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/authkiller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.9.0",
        "aiofiles>=23.2.0",
        "tqdm>=4.66.0",
        "colorama>=0.4.6",
        "pyyaml>=6.0",
        "flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "authkiller=authkiller.cli.main:main",
            "authkiller-launch=authkiller.launcher.launcher:main",
        ],
    },
)
