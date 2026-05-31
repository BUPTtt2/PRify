import json
import requests
from typing import Dict, List, Any, Optional
from config import settings
from utils.exceptions import LLMError, TimeoutError


class LLMService:
    SYSTEM_PROMPT = """你是一个专业的代码审查助手。请分析以下代码变更，识别潜在风险并提供改进建议。
    
分析维度：
1. 逻辑风险：空指针、边界缺失、错误处理不当等
2. 安全风险：硬编码密钥、SQL注入、XSS漏洞等
3. 性能风险：低效循环、内存泄漏、N+1查询等

请以JSON格式返回分析结果。"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "ms-6930d9e1-7f37-47da-8dae-c0fecb94b849"
        self.api_url = "https://api-inference.modelscope.cn/v1"
        self.model = "deepseek-ai/DeepSeek-V3.2"
        self.timeout = settings.llm_timeout

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _build_payload(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }

    def call_llm(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用LLM获取响应"""
        messages = []
        
        if system_prompt or self.SYSTEM_PROMPT:
            messages.append({
                "role": "system",
                "content": system_prompt or self.SYSTEM_PROMPT
            })
        
        messages.append({
            "role": "user", 
            "content": user_prompt
        })
        
        payload = self._build_payload(messages)
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
                timeout=self.timeout,
                verify=False
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.Timeout:
            raise TimeoutError(f"LLM请求超时（{self.timeout}秒）")
        except requests.exceptions.RequestException as e:
            raise LLMError(f"LLM API调用失败: {str(e)}")
        except (KeyError, IndexError) as e:
            raise LLMError(f"LLM响应格式错误: {str(e)}")

    def analyze_changes(self, pr_info: Dict[str, Any], files: List[Dict[str, Any]], diffs: str) -> Dict[str, Any]:
        """分析代码变更"""
        files_summary = self._summarize_files(files)
        
        prompt = f"""请分析以下Pull Request的代码变更：

## PR信息
标题: {pr_info.get('title', 'N/A')}
作者: {pr_info.get('user', {}).get('login', 'N/A')}
变更文件数: {len(files)}
总行数变化: +{pr_info.get('additions', 0)} -{pr_info.get('deletions', 0)}

## 变更文件摘要
{files_summary}

## 代码Diff
{diffs[:8000] if len(diffs) > 8000 else diffs}

请生成JSON格式的分析结果，包含：
1. summary: 变更总结（100字以内）
2. risks: 风险列表，每项包含level(高/中/低)、file、line(行号或范围)、type(security/logic/performance)、description、suggestion
3. positive_points: 正面评价列表

返回格式示例：
{{
    "summary": "本次变更主要是...",
    "risks": [
        {{
            "level": "high",
            "file": "src/auth.py",
            "line": "25-30",
            "type": "security",
            "description": "发现硬编码密钥",
            "suggestion": "使用环境变量替代"
        }}
    ],
    "positive_points": ["代码结构清晰"]
}}"""

        try:
            response = self.call_llm(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            raise LLMError(f"代码变更分析失败: {str(e)}")

    def _summarize_files(self, files: List[Dict[str, Any]]) -> str:
        """生成文件变更摘要"""
        summaries = []
        for f in files[:20]:
            summaries.append(
                f"- {f.get('filename', 'unknown')}: "
                f"({f.get('status', 'modified')}) "
                f"+{f.get('additions', 0)} -{f.get('deletions', 0)}"
            )
        return "\n".join(summaries)

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end == -1:
                    end = len(response)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end == -1:
                    end = len(response)
                response = response[start:end].strip()
            
            result = json.loads(response)
            
            if "summary" not in result:
                result["summary"] = "变更分析完成"
            if "risks" not in result:
                result["risks"] = []
            if "positive_points" not in result:
                result["positive_points"] = []
            
            return result
        
        except json.JSONDecodeError:
            return {
                "summary": response[:200] if len(response) > 200 else response,
                "risks": [],
                "positive_points": [],
                "parse_error": True
            }

    def generate_summary(self, pr_info: Dict[str, Any], files: List[Dict[str, Any]]) -> str:
        """仅生成变更总结"""
        files_summary = self._summarize_files(files)
        
        prompt = f"""请简要总结以下Pull Request的变更（50字以内）：

标题: {pr_info.get('title', 'N/A')}
作者: {pr_info.get('user', {}).get('login', 'N/A')}
变更文件: {files_summary}

直接返回总结内容，不需要额外解释。"""

        return self.call_llm(prompt)

    def identify_risks(self, diffs: str) -> List[Dict[str, Any]]:
        """仅识别风险"""
        prompt = f"""请分析以下代码变更中的风险：

{diffs[:6000] if len(diffs) > 6000 else diffs}

返回JSON格式的风险列表，格式：
[
    {{
        "level": "high/medium/low",
        "description": "风险描述",
        "type": "security/logic/performance"
    }}
]

如果没有发现风险，返回空列表 []"""

        try:
            response = self.call_llm(prompt)
            risks = json.loads(response)
            return risks if isinstance(risks, list) else []
        except:
            return []

    def generate_suggestions(self, risks: List[Dict[str, Any]]) -> List[str]:
        """为每个风险生成改进建议"""
        if not risks:
            return []
        
        risks_text = "\n".join([
            f"- {r.get('description', '未知风险')} (等级: {r.get('level', 'unknown')})"
            for r in risks
        ])
        
        prompt = f"""请为以下代码风险提供改进建议：

{risks_text}

返回JSON格式的建议列表：
[
    "建议1: ...",
    "建议2: ..."
]"""

        try:
            response = self.call_llm(prompt)
            suggestions = json.loads(response)
            return suggestions if isinstance(suggestions, list) else []
        except:
            return [f"建议: 审查风险等级为 {r.get('level', '未知')} 的问题"
                    for r in risks]
