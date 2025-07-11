"""Claude Code 剪切板监听器

自动监听剪切板图片并保存到指定目录，同时替换剪切板内容为文件路径引用。
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .monitor import ClipboardMonitor
from .drag_monitor import DragClipboardMonitor
from .installer import install_claude_code_config
from .drag_simulator import DragSimulator

__all__ = ["ClipboardMonitor", "DragClipboardMonitor", "install_claude_code_config", "DragSimulator"]