#!/usr/bin/env python3
"""
Claude Code 拖拽式剪切板监听器
监听剪切板图片，自动拖拽到 Claude Code 窗口进行上传
"""

import os
import sys
import time
import hashlib
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import psutil

try:
    from PIL import Image, ImageGrab
    import pyperclip
except ImportError:
    print("请安装依赖: pip install pillow pyperclip psutil")
    sys.exit(1)

from .drag_simulator import DragSimulator


class DragClipboardMonitor:
    """拖拽式剪切板监听器"""
    
    def __init__(self, cleanup_hours=1):
        self.cleanup_hours = cleanup_hours
        self.last_clipboard_hash = None
        self.running = False
        self.drag_simulator = DragSimulator()
        
        # 创建临时目录
        self.temp_dir = Path(tempfile.gettempdir()) / "claude_clipboard_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
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
    
    def save_temp_image(self, image):
        """保存图片到临时文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claude_clipboard_{timestamp}.png"
        filepath = self.temp_dir / filename
        
        image.save(filepath, "PNG")
        return filepath
    
    def cleanup_temp_files(self):
        """清理过期的临时文件"""
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_hours)
        
        for file_path in self.temp_dir.glob("claude_clipboard_*.png"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    print(f"🧹 清理临时文件: {file_path.name}")
            except Exception as e:
                print(f"⚠️ 清理文件失败 {file_path}: {e}")
    
    def process_clipboard_image(self, image):
        """处理剪切板图片：保存并拖拽到Claude"""
        try:
            # 1. 保存到临时文件
            temp_file = self.save_temp_image(image)
            print(f"💾 图片已保存到临时文件: {temp_file.name}")
            
            # 2. 短暂延迟确保文件完全写入
            time.sleep(0.2)
            
            # 3. 模拟拖拽到Claude Code窗口
            print("🎯 正在拖拽到 Claude Code...")
            success = self.drag_simulator.simulate_drag_to_claude(str(temp_file))
            
            if success:
                print("✅ 图片已成功拖拽到 Claude Code")
                # 延迟删除，确保Claude有时间处理文件
                time.sleep(2)
                try:
                    temp_file.unlink()
                    print(f"🗑️ 临时文件已删除: {temp_file.name}")
                except Exception as e:
                    print(f"⚠️ 删除临时文件失败: {e}")
            else:
                print("❌ 拖拽失败，临时文件保留")
                
            return success
            
        except Exception as e:
            print(f"❌ 处理图片失败: {e}")
            return False
    
    def run(self):
        """运行监听器"""
        print("🚀 Claude Code 拖拽式剪切板监听器已启动")
        print("📋 监听剪切板图片中...")
        print("🎯 检测到图片时将自动拖拽到 Claude Code 窗口")
        print("🛑 按 Ctrl+C 停止")
        
        # 检查依赖
        try:
            self.drag_simulator.get_active_claude_window()
        except Exception as e:
            print(f"⚠️ 拖拽功能初始化失败: {e}")
            print("将使用备用方案（保存文件但不拖拽）")
        
        self.running = True
        cleanup_counter = 0
        
        while self.running:
            try:
                # 每50次循环清理一次临时文件
                cleanup_counter += 1
                if cleanup_counter >= 50:
                    self.cleanup_temp_files()
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
                        print(f"\n📋 检测到新图片 (hash: {current_hash[:8]}...)")
                        
                        # 处理图片：保存并拖拽
                        success = self.process_clipboard_image(image)
                        self.last_clipboard_hash = current_hash
                        
                        if not success:
                            print("💡 提示: 也可以手动拖拽图片文件到 Claude Code 窗口")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 正在停止监听器...")
                self.running = False
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(1)
        
        # 清理退出
        self.cleanup_temp_files()
        print("👋 监听器已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code 拖拽式剪切板监听器")
    parser.add_argument(
        "--cleanup-hours",
        type=int,
        default=1,
        help="临时文件清理时间（小时，默认1）"
    )
    parser.add_argument(
        "--test-drag",
        action="store_true",
        help="测试拖拽功能"
    )
    
    args = parser.parse_args()
    
    if args.test_drag:
        from .drag_simulator import test_drag_simulator
        test_drag_simulator()
        return
    
    # 检查依赖
    try:
        import PIL, pyperclip, psutil, pyautogui
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install pillow pyperclip psutil pyautogui")
        return
    
    monitor = DragClipboardMonitor(cleanup_hours=args.cleanup_hours)
    monitor.run()


if __name__ == "__main__":
    main()