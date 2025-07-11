#!/usr/bin/env python3
"""
Claude Code 剪切板监听器
跨平台监听剪切板，自动将图片保存到 .tmp/ 目录并替换为文件引用
"""

import os
import sys
import time
import hashlib
import platform
from datetime import datetime, timedelta
from pathlib import Path
import psutil

try:
    from PIL import Image, ImageGrab
    import pyperclip
except ImportError:
    print("请安装依赖: pip install pillow pyperclip psutil")
    sys.exit(1)

class ClipboardMonitor:
    def __init__(self, tmp_dir=".tmp", cleanup_hours=24):
        self.tmp_dir = Path(tmp_dir)
        self.cleanup_hours = cleanup_hours
        self.last_clipboard_hash = None
        self.running = False
        
        # 创建临时目录
        self.tmp_dir.mkdir(exist_ok=True)
    
    def is_claude_code_running(self):
        """检测 Claude Code 是否在运行"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info.get('name', '')
                cmdline = proc.info.get('cmdline', [])
                # 检查进程名或命令行中是否包含 claude
                if (name and 'claude' in name.lower()) or \
                   (cmdline and any('claude' in str(cmd).lower() for cmd in cmdline)):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def get_clipboard_image(self):
        """获取剪切板中的图片"""
        try:
            # 使用 PIL 的 ImageGrab 跨平台获取剪切板图片
            return ImageGrab.grabclipboard()
        except Exception:
            pass
        return None
    
    def get_clipboard_hash(self, image=None):
        """获取剪切板内容的哈希值"""
        try:
            if image:
                # 对图片数据计算哈希
                from io import BytesIO
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                return hashlib.md5(img_bytes.getvalue()).hexdigest()
            else:
                # 对文本内容计算哈希
                text = pyperclip.paste()
                return hashlib.md5(text.encode()).hexdigest()
        except Exception:
            return None
    
    def save_image(self, image):
        """保存图片到临时目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clipboard_{timestamp}.png"
        filepath = self.tmp_dir / filename
        
        image.save(filepath, "PNG")
        return filepath
    
    def cleanup_old_files(self):
        """清理过期的临时文件"""
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_hours)
        
        for file_path in self.tmp_dir.glob("clipboard_*.png"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    print(f"已清理过期文件: {file_path}")
            except Exception as e:
                print(f"清理文件失败 {file_path}: {e}")
    
    def run(self):
        """运行监听器"""
        print("🚀 Claude Code 剪切板监听器已启动")
        print(f"📁 临时文件目录: {self.tmp_dir.absolute()}")
        print("📋 监听剪切板图片中...")
        print("🛑 按 Ctrl+C 停止")
        
        self.running = True
        cleanup_counter = 0
        
        while self.running:
            try:
                # 每100次循环清理一次文件
                cleanup_counter += 1
                if cleanup_counter >= 100:
                    self.cleanup_old_files()
                    cleanup_counter = 0
                
                # 检查 Claude Code 是否运行
                if not self.is_claude_code_running():
                    time.sleep(2)
                    continue
                
                # 检查剪切板是否有图片
                image = self.get_clipboard_image()
                if image:
                    # 检查是否是新的内容（对图片数据计算哈希）
                    current_hash = self.get_clipboard_hash(image)
                    if current_hash != self.last_clipboard_hash:
                        # 保存图片
                        filepath = self.save_image(image)
                        
                        # 替换剪切板内容为格式化的文件路径
                        formatted_path = f" @{filepath} "
                        pyperclip.copy(formatted_path)
                        self.last_clipboard_hash = current_hash
                        
                        print(f"✅ 图片已保存: {filepath}")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 正在停止监听器...")
                self.running = False
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(1)
        
        print("👋 监听器已停止")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
Claude Code 剪切板监听器

用法:
  python clipboard_monitor.py              # 启动监听器
  python clipboard_monitor.py --help       # 显示帮助

功能:
- 监听剪切板图片
- 自动保存到 .tmp/ 目录
- 替换剪切板内容为文件路径
- 自动清理过期文件 (24小时)
- 仅在 Claude Code 运行时工作

依赖:
  pip install pillow pyperclip psutil
            """)
            return
    
    # 检查依赖
    try:
        import PIL, pyperclip, psutil
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install pillow pyperclip psutil")
        return
    
    monitor = ClipboardMonitor()
    monitor.run()

if __name__ == "__main__":
    main()