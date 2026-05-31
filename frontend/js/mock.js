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

export const mockErrorResponses = {
  invalid_url: {
    success: false,
    data: null,
    error: {
      code: "INVALID_URL",
      message: "无效的GitHub PR URL格式",
      details: "请确保URL格式为: https://github.com/owner/repo/pull/number"
    }
  },
  pr_not_found: {
    success: false,
    data: null,
    error: {
      code: "PR_NOT_FOUND",
      message: "PR不存在",
      details: "无法找到指定的PR，请检查URL是否正确"
    }
  },
  rate_limit: {
    success: false,
    data: null,
    error: {
      code: "RATE_LIMIT",
      message: "API请求已达上限",
      details: "请稍后再试，或检查API配置"
    }
  },
  network_error: {
    success: false,
    data: null,
    error: {
      code: "NETWORK_ERROR",
      message: "网络连接失败",
      details: "请检查网络连接后重试"
    }
  },
  timeout: {
    success: false,
    data: null,
    error: {
      code: "TIMEOUT",
      message: "请求超时",
      details: "分析时间过长，请稍后重试"
    }
  },
  empty_result: {
    success: true,
    data: {
      pr_info: {
        title: "No changes found",
        author: "unknown",
        files_count: 0,
        additions: 0,
        deletions: 0
      },
      summary: "未发现任何代码变更",
      risks: [],
      total_files: 0,
      processing_time: 2.1
    },
    error: null
  }
};
