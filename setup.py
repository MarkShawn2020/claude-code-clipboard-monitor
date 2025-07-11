#!/usr/bin/env python3
"""
Claude Code Clipboard Monitor
跨平台剪切板监听器，提升 Claude Code 使用体验
"""

from setuptools import setup, find_packages

setup(
    name="claude-code-clipboard-monitor",
    version="1.0.0",
    description="跨平台剪切板监听器，自动处理 Claude Code 中的图片粘贴",
    author="Claude Code User",
    python_requires=">=3.6",
    py_modules=["clipboard_monitor"],
    install_requires=[
        "pillow>=8.0.0",
        "pyperclip>=1.8.0", 
        "psutil>=5.8.0"
    ],
    entry_points={
        "console_scripts": [
            "claude-clipboard-monitor=clipboard_monitor:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    keywords="claude-code clipboard monitor automation productivity",
)