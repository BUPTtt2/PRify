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
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**前端服务：**
```bash
cd frontend
python -m http.server 8080
```

### 5. 开始使用

打开浏览器访问：
- **前端界面**：http://localhost:8080
- **API文档**：http://localhost:8000/docs

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
│   │   └── review.py         # PR审查接口
│   ├── services/              # 业务逻辑层
│   │   ├── github_service.py # GitHub API封装
│   │   ├── llm_service.py    # LLM模型调用
│   │   └── analyzer_service.py # 风险分析核心
│   ├── models/                # 数据模型
│   │   └── schemas.py        # Pydantic模型
│   └── utils/                 # 工具模块
│       ├── url_parser.py     # URL解析
│       └── exceptions.py      # 自定义异常
│
├── frontend/                   # HTML/CSS/JS 前端
│   ├── index.html             # 主页面
│   ├── css/style.css          # 自定义样式
│   └── js/
│       ├── main.js            # 主逻辑
│       ├── api.js             # API调用
│       └── mock.js            # Mock数据
│
└── tests/                      # 测试用例
    ├── test_url_parser.py
    ├── test_github_service.py
    ├── test_llm_service.py
    └── test_analyzer_service.py
```

---

## 🛠️ API 接口

### 健康检查

```bash
GET /health
```

响应：
```json
{
  "status": "ok"
}
```

### PR审查

```bash
POST /api/review
Content-Type: application/json

{
  "pr_url": "https://github.com/owner/repo/pull/123"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "pr_info": {
      "title": "feat: 添加新功能",
      "author": "username",
      "state": "open",
      "files_count": 5,
      "additions": 100,
      "deletions": 50
    },
    "summary": "本次变更主要包括...",
    "risks": [
      {
        "level": "high",
        "file": "src/auth.py",
        "line": "25-30",
        "type": "security",
        "description": "发现硬编码密钥",
        "suggestion": "使用环境变量替代"
      }
    ],
    "positive_points": [
      "代码结构清晰",
      "模块化良好"
    ],
    "total_files": 5,
    "processing_time": 12.5
  },
  "error": null
}
```

---

## 🎯 适用场景

| 场景 | 价值 |
|------|------|
| **代码审查** | 自动发现潜在风险，减少人工审查负担 |
| **安全扫描** | 提前发现安全漏洞，降低生产环境风险 |
| **新人培训** | 帮助新成员快速理解代码变更 |
| **合规检查** | 确保代码符合团队安全规范 |

---

## 📦 技术栈

### 后端

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat&logo=fastapi)
![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC?style=flat&logo=pytest)

### 前端

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=flat&logo=tailwind-css)

### AI & API

![DeepSeek](https://img.shields.io/badge/AI-DeepSeek_V3-FF6B6B?style=flat&logo=robot)
![GitHub API](https://img.shields.io/badge/API-GitHub-333333?style=flat&logo=github)
![ModelScope](https://img.shields.io/badge/ModelScope-0000FF?style=flat)

---

## 📈 开发进度

### ✅ 已完成

- [x] PR-01: 项目初始化
- [x] PR-02: URL解析模块
- [x] PR-03: GitHub API集成
- [x] PR-04: LLM服务集成
- [x] PR-05: 风险分析核心
- [x] PR-06: 前端基础页面
- [x] PR-07: 前后端联调
- [x] PR-08: 测试用例完善

### 🔄 进行中

- [ ] README文档完善
- [ ] Demo视频录制

---

## 🤝 贡献者

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/BUPTtt2">
        <img src="https://avatars.githubusercontent.com/u/your-id" width="60px;" alt="开发者"/>
        <br/>
        <sub><b>后端开发</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Star-yua">
        <img src="https://avatars.githubusercontent.com/u/your-id" width="60px;" alt="开发者"/>
        <br/>
        <sub><b>前端开发</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- **七牛云** - 感谢提供本次实训机会
- **ModelScope** - 提供 DeepSeek V3 API 支持
- **GitHub** - 提供强大的 API 接口

---

<p align="center">
  <strong>Made with ❤️ by Team PRify</strong>
  <br>
  <sub>© 2024 PRify. All rights reserved.</sub>
</p>
