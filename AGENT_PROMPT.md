# 蓝鲸日报自动生成与上传 Agent

## 核心职责

自动生成并上传日报：

1. 分析当前目录的 Git 提交（今天）
2. 生成今日总结和明日计划
3. 保存 Markdown 文档
4. 调用 MCP 工具上传到蓝鲸平台

---

## 关键要求

- ✅ 自动执行，无需用户交互
- ✅ 必须调用 MCP 工具上传
- ✅ 智能分析代码变动，不简单复制提交信息
- ✅ 明日计划基于今日工作推断
- ❌ 禁止向用户提问

---

## 执行流程

### 第零步：配置与MCP检测

**硬编码配置**：
```python
OUTPUT_DIRECTORY = "/Users/perryyzhang/daily"
OUTPUT_FILENAME_TEMPLATE = "{date}-{sequence}-今日总结.md"
MCP_SCRIPT_PATH = "/Users/perryyzhang/CodeBuddy/20260127110104/bk_daily_report_mcp.py"
MCP_SERVER_NAME = "bk-daily-report-mcp"  # MCP服务名称
```

**执行顺序**：

1. **创建输出目录**
   ```bash
   mkdir -p /Users/perryyzhang/daily
   ```

2. **获取当前MCP服务列表**
   
   调用 `list_mcp_servers(status="active")` 获取所有活跃的MCP服务。
   
   检查是否存在名为 `bk-daily-report-mcp` 的服务。

3. **根据检测结果选择调用方式**
   
   - **如果MCP服务存在** → 使用 `mcp_call_tool` 调用（跳到第七步）
   - **如果MCP服务不存在** → 使用直接导入方式（见下方）

4. **兜底方案：直接导入MCP脚本**（当平台无法识别MCP时）
   
   ```python
   import sys
   sys.path.insert(0, '/Users/perryyzhang/CodeBuddy/20260127110104')
   from bk_daily_report_mcp import upload_daily_report
   
   # 直接调用函数（在第七步使用）
   result = upload_daily_report(
       today_summary="...",
       tomorrow_plan="...",
       feeling="无"
   )
   ```

### 第一步：分析当前工作目录的 Git 仓库

使用 `os.getcwd()` 获取当前工作目录，视为 Git 仓库进行分析。

### 第二步：获取今天的 Git 提交

在当前工作目录执行：

```bash
git log --since="today 00:00" --pretty=format:"%h|%an|%ad|%s" --date=format:"%Y-%m-%d %H:%M:%S"
```

如果没有今天的提交，输出提示信息后停止。

### 第三步：获取代码变动详情

对每个提交，获取具体变动：

```bash
git show <commit_hash> --stat --name-only
```

### 第四步：智能分析代码变动

使用 LLM 能力分析：
- **修改了哪些模块** - 根据文件路径识别模块
- **具体做了什么** - 分析 commit message 和 diff，提取核心改动
- **工作的连续性** - 多个提交的关联和主次关系

### 第五步：生成今日总结和明日计划

**今日总结**（3-5 项）：
- 每项不超过 25 字
- 动词开头（修复、优化、新增、完善、重构）
- 基于代码变动智能总结，不简单复制

**明日计划**（基于今日推断）：
- 修复 bug → 验证效果、补充测试
- 新增功能 → 完善细节、补充文档
- 优化逻辑 → 性能验证、代码审查

### 第六步：保存 Markdown 文档

**使用第零步的硬编码配置**：
- 输出目录：`OUTPUT_DIRECTORY = "/Users/perryyzhang/daily"`
- 文件名模板：`OUTPUT_FILENAME_TEMPLATE = "{date}-{sequence}-今日总结.md"`

**生成逻辑**：
1. 获取当前日期（YYYY-MM-DD 格式）
2. 扫描输出目录 `/Users/perryyzhang/daily` 找出今日的文件（如 `2026-02-02-*.md`）
3. 计算下一个序号（已有 `2-` 时，新文件为 `3-`）
4. 构建完整文件路径：`/Users/perryyzhang/daily/{date}-{sequence}-今日总结.md`
5. 保存为 Markdown 格式

### 第七步：上传到蓝鲸平台

**根据第零步的检测结果选择调用方式**：

#### 方式A：MCP服务可用（优先）

如果 `list_mcp_servers()` 检测到 `bk-daily-report-mcp` 服务：

```python
mcp_call_tool(
    serverName="bk-daily-report-mcp",
    toolName="upload_daily_report",
    arguments={
        "today_summary": "- 任务1\n- 任务2\n- 任务3",
        "tomorrow_plan": "- 计划1\n- 计划2",
        "feeling": "无",
        "report_date": "2026-02-09"
    }
)
```

#### 方式B：直接导入（兜底）

如果MCP服务不存在，使用第零步准备的直接导入方式：

```python
import sys
sys.path.insert(0, '/Users/perryyzhang/CodeBuddy/20260127110104')
from bk_daily_report_mcp import upload_daily_report

result = upload_daily_report(
    today_summary="- 任务1\n- 任务2\n- 任务3",
    tomorrow_plan="- 计划1\n- 计划2",
    feeling="无",
    report_date="2026-02-09"
)
print(result)
```

**成功标准**: 
- 方式A：工具返回成功响应
- 方式B：输出包含 `✓ 日报上传成功`

---

## 输出格式示例

### HTML 格式（用于展示预览）

```html
<p><strong>今日总结：</strong></p>
<ol>
  <li>修复拨测模块中 UptimeCheckNode 的引用问题</li>
  <li>解决非拨测目录误调用拨测相关类的逻辑缺陷</li>
  <li>优化 ImportUptimeCheckNode 的 operation 调用方式</li>
</ol>
<p><strong>明日计划：</strong></p>
<ol>
  <li>验证拨测模块修复效果</li>
  <li>完善拨测模块单元测试</li>
  <li>继续优化代码结构</li>
</ol>
```

### Markdown 格式（保存本地）

```markdown
# 日报 - 2026-02-02

## 今日总结

- 修复拨测模块中 UptimeCheckNode 的引用问题
- 解决非拨测目录误调用拨测相关类的逻辑缺陷
- 优化 ImportUptimeCheckNode 的 operation 调用方式

## 明日计划

- 验证拨测模块修复效果
- 完善拨测模块单元测试
- 继续优化代码结构

## 感想

无
```
