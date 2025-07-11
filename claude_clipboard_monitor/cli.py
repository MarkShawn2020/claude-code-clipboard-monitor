"""
命令行接口
"""

import sys
import argparse
from .monitor import ClipboardMonitor
from .installer import install_claude_code_config


def main():
    """主命令行入口点"""
    parser = argparse.ArgumentParser(
        description="Claude Code 剪切板监听器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
功能:
  📋 监听剪切板图片
  💾 自动保存到 ~/.neurora/claude-code/screenshots/ 目录  
  🔄 替换剪切板内容为文件路径引用
  🧹 自动清理过期文件 (24小时)
  🔍 仅在 Claude Code 运行时工作

示例:
  claude-clipboard-monitor                    # 启动监听器
  claude-clipboard-monitor --configure        # 仅配置 Claude Code
  claude-clipboard-monitor --help             # 显示此帮助
        """
    )
    
    parser.add_argument(
        "--configure",
        action="store_true",
        help="仅配置 Claude Code 设置而不启动监听器"
    )
    
    parser.add_argument(
        "--cleanup-hours",
        type=int,
        default=24,
        help="文件清理时间（小时，默认24）"
    )
    
    parser.add_argument(
        "--tmp-dir",
        type=str,
        help="自定义临时目录路径（默认: ~/.neurora/claude-code/screenshots）"
    )
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import PIL
        import pyperclip
        import psutil
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install claude-clipboard-monitor")
        return 1
    
    # 自动配置 Claude Code
    print("🔧 正在配置 Claude Code...")
    if not install_claude_code_config():
        print("❌ Claude Code 配置失败")
        return 1
    
    # 如果只是配置，就退出
    if args.configure:
        print("✅ 配置完成")
        return 0
    
    # 启动监听器
    try:
        monitor = ClipboardMonitor(
            tmp_dir=args.tmp_dir,
            cleanup_hours=args.cleanup_hours
        )
        monitor.run()
    except KeyboardInterrupt:
        print("\n🛑 监听器已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())