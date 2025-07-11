# Claude Code 剪切板监听器

自动监听剪切板图片并保存到指定目录，同时替换剪切板内容为文件路径引用，专为 Claude Code 优化。

## 功能特性

- 📋 **智能监听**: 仅在 Claude Code 运行时监听剪切板
- 💾 **自动保存**: 将剪切板图片保存到 `~/.neurora/claude-code/screenshots/` 目录
- 🔄 **智能替换**: 自动将剪切板内容替换为格式化的文件路径引用
- 🧹 **自动清理**: 自动清理 24 小时前的过期文件
- ⚡ **跨平台**: 支持 Windows、macOS、Linux
- 🎯 **零配置**: 自动配置 Claude Code 的 `additionalDirectories` 设置

## 安装

```bash
pip install claude-clipboard-monitor
```

## 使用方法

### 启动监听器

```bash
claude-clipboard-monitor
```

### 仅配置 Claude Code（不启动监听器）

```bash
claude-clipboard-config
```

或者：

```bash
claude-clipboard-monitor --configure
```

### 自定义选项

```bash
# 自定义清理时间（小时）
claude-clipboard-monitor --cleanup-hours 48

# 自定义存储目录
claude-clipboard-monitor --tmp-dir /path/to/custom/dir
```

## 工作原理

1. **监听**: 持续监听剪切板变化
2. **检测**: 检测到图片内容时自动保存
3. **替换**: 将剪切板内容替换为 ` @/path/to/image.png ` 格式
4. **清理**: 定期清理过期文件

## 配置

首次运行时会自动配置 Claude Code 的设置文件 `~/.claude/settings.json`，添加必要的目录权限：

```json
{
  "permissions": {
    "additionalDirectories": [
      "~/.claude",
      "~/.neurora/claude-code"
    ]
  }
}
```

## 系统要求

- Python 3.8+
- Claude Code（监听器仅在 Claude Code 运行时工作）

## 依赖

- `pillow`: 图片处理
- `pyperclip`: 剪切板操作
- `psutil`: 进程检测

## 开发

```bash
# 克隆项目
git clone https://github.com/yourusername/claude-clipboard-monitor.git
cd claude-clipboard-monitor

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy .
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！