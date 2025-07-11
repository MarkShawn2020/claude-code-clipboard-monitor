# Claude Code 剪切板监听器

智能监听剪切板图片，自动拖拽到 Claude Code 窗口或保存到本地，专为 Claude Code 优化的剪切板增强工具。

## 项目背景

在使用 Claude Code 进行开发时，经常需要将截图发送给 Claude 进行分析。传统的操作流程是：
1. 截图到剪切板
2. 在 Claude Code 中手动粘贴
3. 等待上传完成

这个过程存在几个问题：
- 需要手动切换窗口操作
- 粘贴过程可能失败或不稳定
- 无法批量处理多个图片

## 解决方案设计

为了解决上述问题，我们设计了一个独立的监听程序：

### 核心设计思路
1. **独立进程监听**: 创建一个独立的 Python 程序监听剪切板变化
2. **智能检测**: 仅在 Claude Code 运行时进行监听，避免资源浪费
3. **自动化处理**: 检测到图片时自动处理并发送到 Claude Code
4. **存储管理**: 将图片统一保存到 `~/.neurora/claude-code/` 目录
5. **工作区集成**: 将存储目录添加到 Claude Code 的 `additionalDirectories` 配置中

### 技术实现
- **剪切板监听**: 使用 `pyperclip` 监听剪切板变化
- **图片处理**: 使用 `Pillow` 处理图片格式和保存
- **进程检测**: 使用 `psutil` 检测 Claude Code 是否运行
- **自动化操作**: 使用 `pyautogui` 实现拖拽功能
- **配置管理**: 自动修改 Claude Code 的设置文件

### 工作流程
1. **监听启动**: 程序启动后持续监听剪切板
2. **图片检测**: 检测到图片内容时触发处理流程
3. **文件保存**: 将图片保存到指定目录并生成唯一文件名
4. **路径替换**: 将剪切板内容替换为格式化的文件路径引用
5. **自动清理**: 定期清理过期的临时文件

## ⚠️ 方案评估与结论

经过实际使用和测试，**这个方案存在根本性问题，不推荐继续使用**：

### 主要问题
1. **破坏系统行为**: 截图后立即转换剪切板内容，导致其他软件无法正常使用截图功能
2. **用户体验差**: 用户期望截图后能在任何地方正常粘贴图片，而不是文本路径
3. **兼容性问题**: 与其他需要图片数据的应用程序冲突
4. **违反预期**: 改变了用户对剪切板的基本预期行为

### 更好的解决方案
**应该在 Claude Code 窗口粘贴时进行图片转文本处理，而不是在截图生成时转换**：

- 保持剪切板的原始图片数据不变
- 仅在 Claude Code 中粘贴时智能检测并处理图片
- 其他应用程序可以正常使用剪切板中的图片数据
- 用户体验更符合预期

### 建议方向
1. 开发 Claude Code 插件或扩展
2. 在 Claude Code 内部实现粘贴拦截和处理
3. 保持系统剪切板行为的完整性
4. 提供更自然的用户交互体验

**总结**: 当前方案虽然技术上可行，但违反了用户对系统行为的基本预期，应该废弃并采用更合理的在应用内处理的方案。

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