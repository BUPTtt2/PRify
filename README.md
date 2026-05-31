# PRify 🤖

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Frontend-TailwindCSS-38B2AC?style=flat&logo=tailwind-css" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

<h2 align="center">AI驱动的代码安全审查系统</h2>

<p align="center">
  🔍 自动检测PR中的安全风险<br>
  🛡️ 智能识别硬编码密钥、逻辑漏洞、性能问题<br>
  📝 一键生成修复建议
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/🧪-安全漏洞检测-FF6B6B?style=for-the-badge" alt="Security">
  <img src="https://img.shields.io/badge/⚡-性能分析-4ECDC4?style=for-the-badge" alt="Performance">
  <img src="https://img.shields.io/badge/🔧-逻辑缺陷识别-F7DC6F?style=for-the-badge" alt="Logic">
</p>

---

## ✨ 特性

### 🎯 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| **PR信息获取** | 自动解析GitHub PR URL，提取标题、作者、文件列表 | ✅ |
| **变更总结** | 自然语言生成代码变更摘要 | ✅ |
| **风险识别** | 三类风险检测：安全/逻辑/性能 | ✅ |
| **修复建议** | 针对每个风险生成可执行的改进建议 | ✅ |
| **结果展示** | 分组展示、折叠/展开、一键复制 | ✅ |
| **错误处理** | 友好提示各类异常情况 | ✅ |

### 🔒 安全检测能力

- **🔴 高风险**：硬编码密钥、敏感信息泄露、密码明文比较
- **🟡 中风险**：边界检查缺失、空指针风险、缺少输入验证
- **🟢 低风险**：性能优化建议、代码可读性改进

### 💡 技术亮点

```
🤖 LLM + 安全专家模式
   ↓
📥 GitHub API 获取 PR Diff
   ↓
🔍 DeepSeek V3 智能分析
   ↓
📊 结构化风险报告
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/BUPTtt2/PRify.git
cd PRify
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# GitHub Personal Access Token（必需）
# 访问 https://github.com/settings/tokens 创建
GITHUB_TOKEN=your_github_token_here

# 魔搭 API Key（必需）
# 访问 https://modelscope.cn 获取
DEEPSEEK_API_KEY=your_api_key_here

# 其他配置（可选）
DEEPSEEK_API_URL=https://api-inference.modelscope.cn/v1
GITHUB_TIMEOUT=30
LLM_TIMEOUT=60
```

### 4. 启动服务

**后端服务：**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**前端服务：**
```bash
cd frontend
python -m http.server 8080
```

### 5. 开始使用

打开浏览器访问：
- **前端界面**：http://localhost:8080
- **API文档**：http://localhost:8001/docs

---

## 📖 使用方法

### 输入PR URL

```
https://github.com/owner/repo/pull/123
```

### 查看分析结果

```
# feat: 新增API路由模块
By developer
3 files • +150 • -20

## Summary
本次变更添加了PR分析核心路由和数据模型...

## Risk Assessment (3)
🔴 MEDIUM: [logic] models/schemas.py:25-30
   缺少部分字段的验证
   Suggestion: 添加更多字段验证规则

🟡 LOW: [performance] services/analyzer_service.py:15-20
   可以添加缓存机制
   Suggestion: 考虑添加API调用缓存

🟢 LOW: [security] utils/url_parser.py:10-15
   建议添加URL白名单验证
   Suggestion: 考虑限制可分析的域名范围
```

---

## 🏗️ 项目架构

```
PRify/
├── backend/                    # Python FastAPI 后端
│   ├── main.py                # 应用入口
│   ├── config.py              # 配置管理
│   ├── routers/              # API路由层
│   │