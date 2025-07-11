"""
Claude Code 配置安装器
自动配置 Claude Code 的 additionalDirectories 设置
"""

import json
import os
from pathlib import Path


def install_claude_code_config():
    """安装和配置 Claude Code 设置"""
    print("🔧 配置 Claude Code...")
    
    # 创建必要的目录
    claude_dir = Path.home() / ".claude"
    screenshot_dir = Path.home() / ".neurora" / "claude-code" / "screenshots"
    
    # 创建目录
    claude_dir.mkdir(exist_ok=True)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 目录已创建: {screenshot_dir}")
    
    # 配置文件路径
    settings_file = claude_dir / "settings.json"
    
    # 读取或创建配置文件
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print("⚠️  配置文件格式错误，重新创建")
            settings = {}
    else:
        settings = {}
        print("✅ 创建 Claude Code 配置文件")
    
    # 确保必要的键存在
    if "permissions" not in settings:
        settings["permissions"] = {}
        print("✅ 创建 permissions 配置")
    
    if "additionalDirectories" not in settings["permissions"]:
        settings["permissions"]["additionalDirectories"] = []
        print("✅ 创建 additionalDirectories 配置")
    
    # 必要的目录列表
    required_dirs = ["~/.claude", "~/.neurora/claude-code"]
    
    # 添加缺失的目录
    additional_dirs = settings["permissions"]["additionalDirectories"]
    updated = False
    
    for dir_path in required_dirs:
        if dir_path not in additional_dirs:
            additional_dirs.append(dir_path)
            print(f"✅ 添加目录: {dir_path}")
            updated = True
    
    # 如果有更新，保存配置文件
    if updated or not settings_file.exists():
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print("✅ Claude Code 配置已保存")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    else:
        print("✅ Claude Code 配置已是最新")
    
    return True


def main():
    """命令行入口点"""
    try:
        success = install_claude_code_config()
        if success:
            print("\n🎉 配置完成！")
            print("现在可以启动剪切板监听器了:")
            print("  claude-clipboard-monitor")
        else:
            print("\n❌ 配置失败")
            return 1
    except KeyboardInterrupt:
        print("\n🛑 配置已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 配置错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())