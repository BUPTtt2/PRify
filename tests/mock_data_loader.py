import json
import os

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "mock_data")


def load_mock_data(filename: str) -> dict:
    """加载mock数据文件"""
    filepath = os.path.join(MOCK_DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mock_pr_info() -> dict:
    """获取mock PR信息"""
    return load_mock_data("sample_pr.json")["mock_pr_info"]


def get_mock_pr_files() -> list:
    """获取mock PR文件列表"""
    return load_mock_data("sample_pr.json")["mock_pr_files"]


def get_mock_diff() -> str:
    """获取mock diff内容"""
    return load_mock_data("sample_pr.json")["mock_diff"]


def get_mock_llm_analysis() -> dict:
    """获取mock LLM分析结果"""
    return load_mock_data("sample_pr.json")["mock_llm_analysis"]


def get_mock_review_response() -> dict:
    """获取mock审查响应"""
    return load_mock_data("sample_pr.json")["mock_review_response"]
