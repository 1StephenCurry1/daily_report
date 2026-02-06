# 快速开始指南

## 项目概述

本项目是一个蓝鲸日报自动上报系统，支持从 Git 仓库分析代码变动、智能总结工作内容，并自动上传到蓝鲸平台。

## 安装和配置

### 1️⃣ 克隆或初始化项目

```bash
# 如果是第一次使用
git clone <repository-url> bk-daily-report
cd bk-daily-report
```

### 2️⃣ 创建虚拟环境和安装依赖

```bash
# 使用 venv
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements_mcp.txt
```

### 3️⃣ 配置个人环境变量

复制 `.env.example` 为 `.env.local` 并填写你的蓝鲸凭证：

```bash
cp .env.example .env.local
nano .env.local  # 编辑文件，填入真实凭证
```

**如何获取凭证**：
1. 打开蓝鲸平台：https://bk-training.bkapps-sz.woa.com
2. 登录你的账户
3. 按 `F12` 打开开发者工具
4. 进入 **Application** → **Cookies**
5. 复制以下值到 `.env.local`：
   - `bk_ticket`
   - `bk-training_csrftoken` → `BK_CSRF_TOKEN`
   - `bk-training_sessionid` → `BK_SESSIONID`

### 4️⃣ 配置个人项目路径

复制 `daily_report_config.example.yml` 为 `daily_report_config.local.yml` 并填写你的项目路径：

```bash
cp daily_report_config.example.yml daily_report_config.local.yml
nano daily_report_config.local.yml  # 编辑文件，填入你的项目路径
```

**编辑内容**：
```yaml
projects:
  bk_monitor:
    repo_path: "/your/actual/path/to/bk-monitor"  # 改为你的项目路径

output:
  summary_dir: "/your/actual/path/to/daily/reports"  # 改为你的输出目录
```

### 5️⃣ 验证配置

```bash
python -c "from bk_daily_report_mcp import BKAuthManager; print('✓ 配置正确' if BKAuthManager().is_authenticated() else '✗ 配置有问题')"
```

## 使用方式

### 启动 MCP 服务

```bash
python bk_daily_report_mcp.py
```

### 调用日报上报功能

```bash
python example_mcp_client.py
```

或通过 MCP 工具调用：

```python
from bk_daily_report_mcp import upload_daily_report

result = upload_daily_report(
    today_summary="- 完成功能1\n- 修复bug1\n- 优化性能1",
    tomorrow_plan="- 开发功能2\n- 编写单元测试\n- 代码审查",
    feeling="进度顺利",
    report_date="2026-02-06"
)
print(result)
```

## 文件说明

| 文件 | 说明 | 需要编辑? |
|------|------|---------|
| `.env.local` | 凭证存储（被忽略） | ✅ 需要填写 |
| `.env.example` | 凭证模板 | ❌ 参考用 |
| `daily_report_config.local.yml` | 个人配置（被忽略） | ✅ 需要填写 |
| `daily_report_config.example.yml` | 配置示例 | ❌ 参考用 |
| `daily_report_config.yml` | 默认通用配置 | ❌ 不要编辑 |
| `pyproject.toml` | 项目元数据 + UV 配置 | ⚠️ 按需 |

## 配置加载优先级

```
环境变量 (优先级最高)
  ↑
daily_report_config.local.yml (个人配置)
  ↑
daily_report_config.yml (默认配置)
```

## 安全性

- ✅ 凭证存储在 `.env.local`（被 .gitignore 忽略）
- ✅ 项目路径存储在 `daily_report_config.local.yml`（被 .gitignore 忽略）
- ✅ 所有敏感信息不会被提交到 Git 仓库

## 常见问题

**Q: 凭证失效怎么办？**  
A: 重新登录蓝鲸平台，获取新的 token，更新 `.env.local` 文件。

**Q: 我可以在 `daily_report_config.yml` 中填写项目路径吗？**  
A: 不建议。应该使用 `daily_report_config.local.yml` 填写个人配置，这样不会被 Git 提交。

**Q: 如何支持多个项目的日报？**  
A: 在 `daily_report_config.local.yml` 中配置多个项目：
```yaml
projects:
  project1:
    name: "项目1"
    repo_path: "/path/to/project1"
  project2:
    name: "项目2"
    repo_path: "/path/to/project2"
```

**Q: 其他团队成员如何使用？**  
A: 按照本指南的步骤配置 `.env.local` 和 `daily_report_config.local.yml` 即可。

## 进阶配置

### 修改蓝鲸平台地址

如果你使用的不是标准蓝鲸平台，可在 `daily_report_config.local.yml` 中覆盖：

```yaml
blueking:
  platform_url: "https://your-custom-blueking.com"
  report_api_endpoint: "https://your-custom-blueking.com/save_daily/"
```

### Python 版本要求

项目要求 Python 3.11+。查看 `pyproject.toml` 了解更多版本要求。

## 支持和反馈

遇到问题？
1. 检查 `.env.local` 和 `daily_report_config.local.yml` 是否正确配置
2. 查看日志信息判断失败原因
3. 查看 `SECURITY.md` 了解凭证管理方式

## 许可证

MIT License
