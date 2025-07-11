"""
拖拽模拟器 - 模拟文件拖拽到 Claude Code 窗口
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List
import platform

try:
    import pyautogui
    import psutil
except ImportError:
    print("请安装额外依赖: pip install pyautogui")
    sys.exit(1)

# 平台特定的窗口操作
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
    except ImportError:
        print("Windows平台需要: pip install pywin32")
        sys.exit(1)
elif platform.system() == "Darwin":  # macOS
    try:
        from AppKit import NSWorkspace, NSApplication
        import Quartz
    except ImportError:
        print("macOS平台需要: pip install pyobjc-framework-Quartz pyobjc-framework-Cocoa")
        sys.exit(1)
elif platform.system() == "Linux":
    try:
        import subprocess
    except ImportError:
        pass


class ClaudeCodeWindowFinder:
    """Claude Code 窗口查找器"""
    
    def __init__(self):
        self.system = platform.system()
    
    def find_claude_windows(self) -> List[dict]:
        """查找所有 Claude Code 窗口"""
        if self.system == "Windows":
            return self._find_windows_claude()
        elif self.system == "Darwin":
            return self._find_macos_claude()
        elif self.system == "Linux":
            return self._find_linux_claude()
        else:
            return []
    
    def _find_windows_claude(self) -> List[dict]:
        """Windows 平台查找 Claude Code 窗口"""
        windows = []
        
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "claude" in window_text.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    windows.append({
                        'title': window_text,
                        'hwnd': hwnd,
                        'rect': rect,
                        'x': rect[0],
                        'y': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1]
                    })
        
        win32gui.EnumWindows(enum_window_callback, windows)
        return windows
    
    def _find_macos_claude(self) -> List[dict]:
        """macOS 平台查找 Claude Code 窗口"""
        windows = []
        
        # 获取所有窗口信息
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )
        
        for window in window_list:
            name = window.get('kCGWindowName', '')
            owner = window.get('kCGWindowOwnerName', '')
            
            if 'claude' in name.lower() or 'claude' in owner.lower():
                bounds = window.get('kCGWindowBounds', {})
                windows.append({
                    'title': name,
                    'owner': owner,
                    'x': int(bounds.get('X', 0)),
                    'y': int(bounds.get('Y', 0)),
                    'width': int(bounds.get('Width', 0)),
                    'height': int(bounds.get('Height', 0))
                })
        
        return windows
    
    def _find_linux_claude(self) -> List[dict]:
        """Linux 平台查找 Claude Code 窗口"""
        windows = []
        
        try:
            # 使用 wmctrl 或 xdotool 查找窗口
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if 'claude' in line.lower():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append({
                                'title': parts[3],
                                'id': parts[0]
                            })
        except FileNotFoundError:
            # 尝试使用 xdotool
            try:
                result = subprocess.run(
                    ['xdotool', 'search', '--name', 'claude'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    for window_id in result.stdout.strip().split('\n'):
                        if window_id:
                            windows.append({'id': window_id})
            except FileNotFoundError:
                pass
        
        return windows


class DragSimulator:
    """拖拽模拟器"""
    
    def __init__(self):
        self.window_finder = ClaudeCodeWindowFinder()
        # 禁用 pyautogui 的安全特性（在自动化中很重要）
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
    
    def get_active_claude_window(self) -> Optional[dict]:
        """获取活动的 Claude Code 窗口"""
        windows = self.window_finder.find_claude_windows()
        
        # 优先返回可见且在前台的窗口
        for window in windows:
            if window.get('width', 0) > 100 and window.get('height', 0) > 100:
                return window
        
        return windows[0] if windows else None
    
    def simulate_drag_to_claude(self, file_path: str) -> bool:
        """模拟拖拽文件到 Claude Code 窗口"""
        claude_window = self.get_active_claude_window()
        if not claude_window:
            print("❌ 未找到 Claude Code 窗口")
            return False
        
        try:
            # 计算窗口中心位置（聊天区域）
            center_x = claude_window['x'] + claude_window['width'] // 2
            center_y = claude_window['y'] + claude_window['height'] // 2
            
            print(f"🎯 拖拽到窗口位置: ({center_x}, {center_y})")
            
            # 模拟拖拽操作
            if platform.system() == "Windows":
                return self._drag_windows(file_path, center_x, center_y)
            elif platform.system() == "Darwin":
                return self._drag_macos(file_path, center_x, center_y)
            elif platform.system() == "Linux":
                return self._drag_linux(file_path, center_x, center_y)
            
        except Exception as e:
            print(f"❌ 拖拽失败: {e}")
            return False
        
        return False
    
    def _drag_windows(self, file_path: str, x: int, y: int) -> bool:
        """Windows 拖拽实现"""
        # 在Windows上，我们可以使用更直接的方法
        # 比如模拟从文件管理器拖拽，或者使用剪切板+粘贴
        
        # 方案1: 尝试模拟Ctrl+V粘贴
        try:
            # 先将文件路径复制到剪切板
            import pyperclip
            pyperclip.copy(file_path)
            
            # 点击Claude窗口激活
            pyautogui.click(x, y)
            time.sleep(0.2)
            
            # 模拟Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"Windows拖拽失败: {e}")
            return False
    
    def _drag_macos(self, file_path: str, x: int, y: int) -> bool:
        """macOS 拖拽实现"""
        try:
            # macOS上可以使用AppleScript来模拟拖拽
            script = f'''
            tell application "System Events"
                set theFile to POSIX file "{file_path}"
                -- 这里需要更复杂的拖拽脚本
            end tell
            '''
            
            # 暂时使用简单的点击+粘贴方法
            pyautogui.click(x, y)
            time.sleep(0.2)
            
            # 在macOS上尝试使用 Cmd+V
            pyautogui.hotkey('cmd', 'v')
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"macOS拖拽失败: {e}")
            return False
    
    def _drag_linux(self, file_path: str, x: int, y: int) -> bool:
        """Linux 拖拽实现"""
        try:
            # Linux上可以使用xdotool或类似工具
            pyautogui.click(x, y)
            time.sleep(0.2)
            
            # 尝试Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"Linux拖拽失败: {e}")
            return False


def test_drag_simulator():
    """测试拖拽模拟器"""
    simulator = DragSimulator()
    
    # 查找Claude窗口
    windows = simulator.window_finder.find_claude_windows()
    print(f"找到 {len(windows)} 个Claude窗口:")
    for i, window in enumerate(windows):
        print(f"  {i+1}. {window}")
    
    # 创建测试文件
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"Test file for drag simulation")
        test_file = f.name
    
    try:
        # 测试拖拽
        success = simulator.simulate_drag_to_claude(test_file)
        print(f"拖拽测试: {'✅ 成功' if success else '❌ 失败'}")
    finally:
        # 清理测试文件
        os.unlink(test_file)


if __name__ == "__main__":
    test_drag_simulator()