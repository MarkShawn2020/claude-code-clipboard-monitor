"""Claude Code 剪切板监听器

自动监听剪切板图片并保存到指定目录，同时替换剪切板内容为文件路径引用。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .monitor import ClipboardMonitor
from .installer import install_claude_code_config

__all__ = ["ClipboardMonitor", "install_claude_code_config"]