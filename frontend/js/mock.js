export const mockReviewResponse = {
  success: true,
  data: {
    pr_info: {
      title: "feat: 添加用户认证功能",
      author: "test-user",
      files_count: 5,
      additions: 100,
      deletions: 50
    },
    summary: "本次变更主要是添加用户认证功能，包括登录页面、JWT token验证和密码加密模块...",
    risks: [
      {
        level: "high",
        file: "src/utils/auth.py",
        line: "25-30",
        type: "security",
        description: "发现硬编码的密钥",
        suggestion: "使用环境变量替代硬编码密钥"
      },
      {
        level: "medium",
        file: "src/routes/login.py",
        line: "15-20",
        type: "logic",
        description: "缺少登录失败重试次数限制",
        suggestion: "添加失败次数限制，防止暴力破解"
      },
      {
        level: "low",
        file: "src/utils/helpers.py",
        line: "10-15",
        type: "style",
        description: "函数命名不够清晰",
        suggestion: "使用更描述性的函数命名以提高代码可读性"
      }
    ],
    total_files: 5,
    processing_time: 12.5
  },
  error: null
};

export const mockHealthCheck = { status: "ok" };
