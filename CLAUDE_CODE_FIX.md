# Claude Code 运行问题修复指南

## 问题描述

Claude Code 运行 Python 文件时报错：找不到 Python 解释器

## 解决方案

### 方法1：使用 VS Code 配置（推荐）

项目已创建配置文件：

1. **`.vscode/settings.json`** - Python 解释器配置
2. **`.vscode/launch.json`** - 运行和调试配置

**在 VS Code 中使用**：
1. 打开 `/root/clawd/wildtrip-existing/` 文件夹
2. 按 F5 或点击"运行和调试"
3. 选择配置：
   - "Python: 当前文件" - 运行当前打开的 Python 文件
   - "Python: 测试多智能体" - 运行完整测试
   - "Python: Flask API" - 启动 API 服务

---

### 方法2：命令行运行（最稳定）

```bash
# 进入项目目录
cd /root/clawd/wildtrip-existing/backend

# 运行测试
python3 test_multi_agent.py --mode full

# 或指定完整路径
/usr/bin/python3 test_multi_agent.py --mode full
```

---

### 方法3：设置环境变量

```bash
# 临时设置（当前终端）
export PYTHONPATH=/root/clawd/wildtrip-existing/backend

# 永久设置
echo 'export PYTHONPATH=/root/clawd/wildtrip-existing/backend' >> ~/.bashrc
source ~/.bashrc
```

---

## 验证环境

```bash
# 检查 Python 版本
python3 --version
# 应该输出: Python 3.10.12

# 检查 Python 路径
which python3
# 应该输出: /usr/bin/python3

# 测试导入
cd /root/clawd/wildtrip-existing/backend
python3 -c "from core.trip_state import TripState; print('导入成功')"
```

---

## 常见问题

### Q1: 提示"No module named 'xxx'"

**原因**: PYTHONPATH 未设置

**解决**:
```bash
cd /root/clawd/wildtrip-existing/backend
export PYTHONPATH=$(pwd)
python3 your_script.py
```

### Q2: VS Code 提示"Python interpreter not found"

**解决**:
1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择 `/usr/bin/python3`

### Q3: Claude Code 还是报错

**解决**: 使用命令行运行
```bash
cd /root/clawd/wildtrip-existing/backend
python3 test_multi_agent.py --mode full
```

---

## 推荐的工作流程

### 开发/调试
```bash
# 1. 进入项目目录
cd /root/clawd/wildtrip-existing/backend

# 2. 设置环境变量
export PYTHONPATH=$(pwd)
export $(cat .env | grep -v '^#' | xargs)

# 3. 运行脚本
python3 test_multi_agent.py --mode single
```

### 测试
```bash
cd /root/clawd/wildtrip-existing/backend
export $(cat .env | grep -v '^#' | xargs)
python3 test_multi_agent.py --mode full
```

### 启动 API
```bash
cd /root/clawd/wildtrip-existing/backend
export $(cat .env | grep -v '^#' | xargs)
python3 api/app.py
```

---

## 已创建的配置文件

✅ `.vscode/settings.json` - Python 环境配置  
✅ `.vscode/launch.json` - 运行配置  
✅ `fix_pydantic_v2.py` - Pydantic 兼容性修复  

---

## 验证修复

运行以下命令验证一切正常：

```bash
cd /root/clawd/wildtrip-existing/backend
python3 -c "
from core.trip_state import TripState
from core.agent_orchestrator import create_trip_orchestrator
from services.user_profile import extract_preferences
print('✅ 所有模块导入成功')
"
```

如果看到 "✅ 所有模块导入成功"，说明环境正常。

---

## 总结

**最简单的方法**: 使用命令行运行
```bash
cd /root/clawd/wildtrip-existing/backend
python3 test_multi_agent.py --mode full
```

**推荐方法**: 配置 VS Code，使用 F5 运行
