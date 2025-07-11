# Claude Code 剪切板监听器

智能监听剪切板图片，自动拖拽到 Claude Code 窗口或保存到本地，专为 Claude Code 优化的剪切板增强工具。

## 功能特性

### 🎯 拖拽模式（推荐）
- 📋 **智能监听**: 仅在 Claude Code 运行时监听剪切板
- 🎯 **自动拖拽**: 检测到图片时自动拖拽到 Claude Code 窗口
- 🔄 **官方上传**: 使用 Claude Code 官方文件上传机制
- 🧹 **即时清理**: 上传完成后立即清理临时文件
- ⚡ **跨平台**: 支持 Windows、macOS、Linux
- 🎯 **零配置**: 无需配置权限，直接使用

### 📁 文件保存模式
- 💾 **自动保存**: 将剪切板图片保存到 `~/.neurora/claude-code/screenshots/` 目录
- 🔄 **智能替换**: 自动将剪切板内容替换为格式化的文件路径引用
- 🧹 **定期清理**: 自动清理过期文件
- ⚙️ **自动配置**: 自动配置 Claude Code 的 `additionalDirectories` 设置

## 安装

```bash
pip install claude-clipboard-monitor
```

## 使用方法

### 🎯 拖拽模式（推荐）

```bash
claude-clipboard-drag
```

自动检测剪切板图片并拖拽到 Claude Code 窗口，使用官方上传机制。

### 📁 文件保存模式

```bash
claude-clipboard-monitor
```

保存图片到本地目录并替换剪切板内容为文件引用。

### 🔧 仅配置 Claude Code

```bash
claude-clipboard-config
```

### 🧪 测试拖拽功能

```bash
claude-clipboard-drag --test-drag
```

### 自定义选项

```bash
# 拖拽模式选项
claude-clipboard-drag --cleanup-hours 2

# 文件保存模式选项  
claude-clipboard-monitor --cleanup-hours 48 --tmp-dir /path/to/custom/dir
```

## 工作原理

### 🎯 拖拽模式（推荐）
1. **监听**: 持续监听剪切板变化
2. **检测**: 检测到图片内容时保存到临时文件
3. **拖拽**: 自动拖拽文件到 Claude Code 窗口
4. **上传**: 使用 Claude Code 官方上传机制
5. **清理**: 上传完成后删除临时文件

### 📁 文件保存模式
1. **监听**: 持续监听剪切板变化
2. **保存**: 检测到图片内容时保存到指定目录
3. **替换**: 将剪切板内容替换为 ` @/path/to/image.png ` 格式
4. **清理**: 定期清理过期文件

## 配置

### 🎯 拖拽模式
无需任何配置，直接使用！

### 📁 文件保存模式
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

### 核心依赖
- `pillow`: 图片处理
- `pyperclip`: 剪切板操作  
- `psutil`: 进程检测
- `pyautogui`: GUI 自动化（拖拽功能）

### 平台特定依赖
- **Windows**: `pywin32` (窗口操作)
- **macOS**: `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa` (窗口操作)

### 安装完整功能
```bash
# 安装所有平台依赖
pip install "claude-clipboard-monitor[all]"

# 或仅安装当前平台依赖
pip install "claude-clipboard-monitor[windows]"  # Windows
pip install "claude-clipboard-monitor[macos]"    # macOS
```

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