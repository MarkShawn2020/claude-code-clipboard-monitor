#!/usr/bin/env python3
"""
Claude Code 简单剪切板监听器
简化版本：只保存图片，不替换剪切板内容
"""

import os
import sys
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import psutil

try:
    from PIL import Image, ImageGrab
    import pyperclip
except ImportError:
    print("请安装依赖: pip install pillow pyperclip psutil")
    sys.exit(1)


class SimpleClipboardMonitor:
    """简单剪切板监听器 - 只保存图片，不干扰剪切板"""
    
    def __init__(self, tmp_dir=None, cleanup_hours=24):
        # 默认使用 ~/.neurora/claude-code/screenshots 目录
        if tmp_dir is None:
            tmp_dir = Path.home() / ".neurora" / "claude-code" / "screenshots"
        
        self.tmp_dir = Path(tmp_dir)
        self.cleanup_hours = cleanup_hours
        self.last_clipboard_hash = None
        self.running = False
        
        # 创建目录
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
    
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
            return ImageGrab.grabclipboard()
        except Exception:
            pass
        return None
    
    def get_clipboard_hash(self, image):
        """获取图片内容的哈希值"""
        try:
            from io import BytesIO
            img_bytes = BytesIO()
            image.save(img_bytes, format='PNG')
            return hashlib.md5(img_bytes.getvalue()).hexdigest()
        except Exception:
            return None
    
    def save_image(self, image):
        """保存图片到目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clipboard_{timestamp}.png"
        filepath = self.tmp_dir / filename
        
        image.save(filepath, "PNG")
        return filepath
    
    def cleanup_old_files(self):
        """清理过期的文件"""
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_hours)
        
        for file_path in self.tmp_dir.glob("clipboard_*.png"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    print(f"🧹 已清理过期文件: {file_path}")
            except Exception as e:
                print(f"清理文件失败 {file_path}: {e}")
    
    def run(self):
        """运行监听器"""
        print("🚀 Claude Code 简单剪切板监听器已启动")
        print(f"📁 文件保存目录: {self.tmp_dir.absolute()}")
        print("💡 工作模式: 仅保存图片，不修改剪切板")
        print("📋 剪切板图片将保持不变，可正常在任何应用中粘贴")
        print("🎯 保存的图片可在 Claude Code 中手动引用")
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
                    # 检查是否是新的内容
                    current_hash = self.get_clipboard_hash(image)
                    if current_hash != self.last_clipboard_hash:
                        # 保存图片但不修改剪切板
                        filepath = self.save_image(image)
                        self.last_clipboard_hash = current_hash
                        
                        print(f"💾 图片已保存: {filepath}")
                        print(f"📋 剪切板图片保持不变")
                        print(f"🎯 在 Claude Code 中可使用: @{filepath}")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 正在停止监听器...")
                self.running = False
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(1)
        
        print("👋 监听器已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code 简单剪切板监听器")
    parser.add_argument(
        "--cleanup-hours",
        type=int,
        default=24,
        help="文件清理时间（小时，默认24）"
    )
    parser.add_argument(
        "--tmp-dir",
        type=str,
        help="自定义存储目录路径"
    )
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import PIL, pyperclip, psutil
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install pillow pyperclip psutil")
        return
    
    monitor = SimpleClipboardMonitor(
        tmp_dir=args.tmp_dir,
        cleanup_hours=args.cleanup_hours
    )
    monitor.run()


if __name__ == "__main__":
    main()