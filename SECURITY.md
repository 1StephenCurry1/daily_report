# 安全性配置指南

## 凭证管理

本项目采用**环境变量 + .gitignore** 的方式管理敏感凭证，确保不会意外泄漏到 Git 仓库。

### 工作流程

```
.env.local (本地私密凭证)
    ↓
daily_report_config.yml (占位符 ${VAR_NAME})
    ↓
bk_daily_report_mcp.py (加载并使用凭证)
```

### 快速开始

#### 1️⃣ 创建本地凭证文件

```bash
cp .env.example .env.local
```

#### 2️⃣ 编辑 `.env.local`，填入真实凭证

```bash
nano .env.local
```

```env
BK_TICKET=your_actual_ticket_here
BK_CSRF_TOKEN=your_actual_csrf_token_here
BK_SESSIONID=your_actual_sessionid_here
```

#### 3️⃣ 验证配置

```bash
python -c "from bk_daily_report_mcp import BKAuthManager; auth = BKAuthManager(); print('✓ 已认证' if auth.is_authenticated() else '✗ 未认证')"
```

### 凭证读取优先级

1. **环境变量**（`BK_TICKET`、`BK_CSRF_TOKEN`、`BK_SESSIONID`）- 优先级最高
2. **YAML 配置文件**（`daily_report_config.yml`）- 包含占位符 `${VAR_NAME}`
3. **默认值** - 空字符串

### 获取凭证

#### 蓝鲸平台 Token 获取步骤：

1. 打开蓝鲸平台：`https://bk-training.bkapps-sz.woa.com`
2. 登录你的账户
3. 按 `F12` 打开开发者工具
4. 进入 **Application** → **Cookies**
5. 查找并复制：
   - `bk_ticket`
   - `bk-training_csrftoken` （对应 `BK_CSRF_TOKEN`）
   - `bk-training_sessionid` （对应 `BK_SESSIONID`）

### 安全检查

✅ **确认凭证已被保护：**

```bash
# 检查 .env.local 是否被忽略
git check-ignore .env.local

# 验证 Git 不会提交凭证
git status
```

### 常见问题

**Q: 误提交了 .env.local 怎么办？**

A: 从 Git 历史中移除：
```bash
git filter-branch --tree-filter 'rm -f .env.local' -- --all
```

**Q: 凭证失效怎么办？**

A: 重新登录蓝鲸平台，获取新的 token，更新 `.env.local` 文件。

**Q: 如何共享配置给团队？**

A: 
- 提交 `.env.example` 文件（含注释）
- 每个开发者自己创建 `.env.local` 并填入凭证
- 绝对不要共享 `.env.local` 文件

### 推荐做法

- 定期更新凭证（按蓝鲸平台的安全策略）
- 不同环境使用不同的 `.env.local` 文件
- 在 CI/CD 流程中，使用机密管理工具（如 GitHub Secrets）
