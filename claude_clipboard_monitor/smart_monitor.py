#!/usr/bin/env python3
"""
Claude Code 智能剪切板监听器
智能处理剪切板图片：保存文件但不影响其他应用的正常粘贴
"""

import os
import sys
import time
import hashlib
import platform
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import threading
import queue

try:
    from PIL import Image, ImageGrab
    import pyperclip
except ImportError:
    print("请安装依赖: pip install pillow pyperclip psutil")
    sys.exit(1)


class SmartClipboardMonitor:
    """智能剪切板监听器"""
    
    def __init__(self, tmp_dir=None, cleanup_hours=24):
        # 默认使用 ~/.neurora/claude-code/screenshots 目录
        if tmp_dir is None:
            tmp_dir = Path.home() / ".neurora" / "claude-code" / "screenshots"
        
        self.tmp_dir = Path(tmp_dir)
        self.cleanup_hours = cleanup_hours
        self.last_clipboard_hash = None
        self.running = False
        
        # 存储图片文件映射 {hash: file_path}
        self.image_files = {}
        
        # 创建临时目录
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化键盘监听（用于检测粘贴操作）
        self.setup_keyboard_listener()
    
    def setup_keyboard_listener(self):
        """设置键盘监听器（检测粘贴操作）"""
        self.paste_queue = queue.Queue()
        self.keyboard_thread = None
        
        try:
            # 尝试导入键盘监听库
            import keyboard
            self.keyboard_available = True
        except ImportError:
            print("⚠️  键盘监听功能不可用，建议安装: pip install keyboard")
            self.keyboard_available = False
    
    def start_keyboard_listener(self):
        """启动键盘监听线程"""
        if not self.keyboard_available:
            return
        
        def keyboard_listener():
            import keyboard
            
            while self.running:
                try:
                    # 检测 Ctrl+V 或 Cmd+V
                    if platform.system() == "Darwin":
                        # macOS 使用 Cmd+V
                        if keyboard.is_pressed('cmd') and keyboard.is_pressed('v'):
                            self.paste_queue.put('paste_detected')
                            time.sleep(0.1)  # 防止重复触发
                    else:
                        # Windows/Linux 使用 Ctrl+V
                        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('v'):
                            self.paste_queue.put('paste_detected')
                            time.sleep(0.1)  # 防止重复触发
                    
                    time.sleep(0.05)  # 降低CPU占用
                except Exception:
                    pass
        
        self.keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
        self.keyboard_thread.start()
    
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
    
    def get_active_window_title(self):
        """获取当前活动窗口标题"""
        try:
            if platform.system() == "Windows":
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            elif platform.system() == "Darwin":
                # macOS
                from AppKit import NSWorkspace
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                return active_app.get('NSApplicationName', '')
            elif platform.system() == "Linux":
                # Linux
                import subprocess
                result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], 
                                      capture_output=True, text=True)
                return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            pass
        return ""
    
    def is_claude_code_active(self):
        """检查 Claude Code 是否是当前活动窗口"""
        window_title = self.get_active_window_title()
        return 'claude' in window_title.lower()
    
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
                    
                    # 从映射中移除
                    for hash_key, path in list(self.image_files.items()):
                        if path == file_path:
                            del self.image_files[hash_key]
                            break
                            
            except Exception as e:
                print(f"清理文件失败 {file_path}: {e}")
    
    def handle_paste_in_claude(self, image_hash):
        """处理在 Claude Code 中的粘贴操作"""
        if image_hash in self.image_files:
            file_path = self.image_files[image_hash]
            if file_path.exists():
                # 临时替换剪切板内容为文件路径
                formatted_path = f" @{file_path} "
                pyperclip.copy(formatted_path)
                print(f"🎯 在 Claude Code 中粘贴文件引用: {file_path}")
                
                # 1秒后恢复图片到剪切板
                def restore_image():
                    time.sleep(1)
                    try:
                        # 重新加载图片到剪切板
                        from PIL import Image
                        img = Image.open(file_path)
                        # 这里需要平台特定的代码来将图片放回剪切板
                        # 暂时跳过，因为PIL的ImageGrab.grabclipboard()只读不写
                        pass
                    except Exception:
                        pass
                
                threading.Thread(target=restore_image, daemon=True).start()
    
    def run(self):
        """运行监听器"""
        print("🚀 Claude Code 智能剪切板监听器已启动")
        print(f"📁 文件保存目录: {self.tmp_dir.absolute()}")
        print("💡 工作模式: 保存图片但不影响正常粘贴")
        print("🛑 按 Ctrl+C 停止")
        
        self.running = True
        cleanup_counter = 0
        
        # 启动键盘监听
        self.start_keyboard_listener()
        
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
                        self.image_files[current_hash] = filepath
                        self.last_clipboard_hash = current_hash
                        
                        print(f"💾 图片已保存: {filepath}")
                        print("✅ 剪切板图片保持不变，可正常在其他应用中粘贴")
                
                # 检查是否有粘贴操作
                if self.keyboard_available:
                    try:
                        self.paste_queue.get_nowait()
                        # 检测到粘贴操作，判断是否在 Claude Code 中
                        if self.is_claude_code_active() and self.last_clipboard_hash:
                            self.handle_paste_in_claude(self.last_clipboard_hash)
                    except queue.Empty:
                        pass
                
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
    
    parser = argparse.ArgumentParser(description="Claude Code 智能剪切板监听器")
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
    
    monitor = SmartClipboardMonitor(
        tmp_dir=args.tmp_dir,
        cleanup_hours=args.cleanup_hours
    )
    monitor.run()


if __name__ == "__main__":
    main()