#!/bin/bash

echo "🚀 安装 Claude Code 剪切板监听器..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3"
    exit 1
fi

# 创建存储目录
echo "📁 创建存储目录..."
SCREENSHOT_DIR="$HOME/.neurora/claude-code/screenshots"
mkdir -p "$SCREENSHOT_DIR"
echo "✅ 目录已创建: $SCREENSHOT_DIR"

# 配置 Claude Code
echo "🔧 配置 Claude Code..."
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
CLAUDE_DIR="$HOME/.claude"

# 创建 .claude 目录
mkdir -p "$CLAUDE_DIR"

# 创建或读取配置文件
if [ ! -f "$CLAUDE_SETTINGS" ]; then
    echo '{}' > "$CLAUDE_SETTINGS"
    echo "✅ 创建 Claude Code 配置文件"
fi

# 确保 permissions 键存在
if ! jq -e '.permissions' "$CLAUDE_SETTINGS" > /dev/null 2>&1; then
    jq '.permissions = {}' "$CLAUDE_SETTINGS" > "$CLAUDE_SETTINGS.tmp" && mv "$CLAUDE_SETTINGS.tmp" "$CLAUDE_SETTINGS"
    echo "✅ 创建 permissions 配置"
fi

# 确保 additionalDirectories 键存在
if ! jq -e '.permissions.additionalDirectories' "$CLAUDE_SETTINGS" > /dev/null 2>&1; then
    jq '.permissions.additionalDirectories = []' "$CLAUDE_SETTINGS" > "$CLAUDE_SETTINGS.tmp" && mv "$CLAUDE_SETTINGS.tmp" "$CLAUDE_SETTINGS"
    echo "✅ 创建 additionalDirectories 配置"
fi

# 添加必要的目录
REQUIRED_DIRS=("~/.claude" "~/.neurora/claude-code")
for dir in "${REQUIRED_DIRS[@]}"; do
    if ! jq -e --arg dir "$dir" '.permissions.additionalDirectories[] | select(. == $dir)' "$CLAUDE_SETTINGS" > /dev/null 2>&1; then
        jq --arg dir "$dir" '.permissions.additionalDirectories += [$dir]' "$CLAUDE_SETTINGS" > "$CLAUDE_SETTINGS.tmp" && mv "$CLAUDE_SETTINGS.tmp" "$CLAUDE_SETTINGS"
        echo "✅ 添加目录: $dir"
    fi
done

echo "✅ Claude Code 配置完成"

# 安装依赖
echo "📦 安装依赖..."
pip3 install pillow pyperclip psutil

# 创建启动脚本
cat > start_clipboard_monitor.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 clipboard_monitor.py
EOF

chmod +x start_clipboard_monitor.sh

echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  ./start_clipboard_monitor.sh    # 启动监听器"
echo "  python3 clipboard_monitor.py    # 直接运行"
echo ""
echo "功能:"
echo "  📋 监听剪切板图片"
echo "  💾 自动保存到 .tmp/ 目录"  
echo "  🔄 替换为文件路径引用"
echo "  🧹 自动清理过期文件"