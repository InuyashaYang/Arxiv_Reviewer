# Arxiv_Analyser/parser.py

import json
import ast
import re

class LLMParser:
    def __init__(self):
        pass

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        将中文标点替换为英文标点，并对引号内的换行符进行转义，保证字符串解析时格式正确。
        """
        punctuation_mapping = {
            "，": ",",
            "‘": "'",
            "’": "'",
            "“": "'",
            "”": "'",
            "。": ".",
            "：": ":",
            "；": ";",
            "？": "?",
            "【": "[",
            "】": "]",
            "（": "(",
            "）": ")",
            "！": "!",
            "—": "-",
            "…": "..."
        }
        for cn, en in punctuation_mapping.items():
            text = text.replace(cn, en)
        # 替换引号内的换行符，防止解析时出错
        text = re.sub(r'(".*?")', lambda m: m.group(1).replace('\n', '\\n'), text, flags=re.DOTALL)
        return text

    def parse_list(self, str_with_list: str):
        """
        将包含列表的字符串解析为Python列表对象。

        参数:
          - str_with_list: 包含列表格式文本的字符串

        返回:
          - list: 解析后的列表

        异常:
          - RuntimeError: 如果解析失败则抛出异常
        """
        try:
            normalized = self._normalize_text(str_with_list)
            # 查找第一个 '[' 和最后一个 ']' 的位置
            start_index = normalized.find('[')
            end_index = normalized.rfind(']') + 1  # 切片时包含结束位置
            if start_index == -1 or end_index == 0:
                raise ValueError(f"列表的开始或结束标志未找到。原文字串为: {str_with_list}")
            list_str = normalized[start_index:end_index]
            knowledge_points = ast.literal_eval(list_str)
            if isinstance(knowledge_points, list):
                return knowledge_points
            else:
                raise ValueError("解析出的对象不是列表。")
        except Exception as e:
            raise RuntimeError(f"解析失败，错误信息：{e}。原文字串为: {str_with_list}")

    def parse_dict(self, str_with_dict: str):
        """
        将包含字典的字符串解析为Python字典对象。

        参数:
          - str_with_dict: 包含字典格式文本的字符串

        返回:
          - dict: 解析后的字典

        异常:
          - RuntimeError: 如果解析失败则抛出异常
        """
        try:
            normalized = self._normalize_text(str_with_dict)
            # 查找第一个 '{' 和最后一个 '}' 的位置
            start_index = normalized.find('{')
            end_index = normalized.rfind('}') + 1  # 切片时包含结束位置
            if start_index == -1 or end_index == 0:
                raise ValueError(f"字典的开始或结束标志未找到。原文字串为: {str_with_dict}")
            dict_str = normalized[start_index:end_index]
            parsed_dict = ast.literal_eval(dict_str)
            if isinstance(parsed_dict, dict):
                return parsed_dict
            else:
                raise ValueError("解析出的对象不是字典。")
        except Exception as e:
            raise RuntimeError(f"解析失败，错误信息：{e}。原文字串为: {str_with_dict}")

    def parse_pads(self, str_with_pads: str):
        """
        从包含特殊pad标记的文本中提取内容，该内容位于 '=start_pad=' 和 '=end_pad=' 标记之间。

        参数:
          - str_with_pads: 包含pad标记的字符串

        返回:
          - str: 提取的pad内容

        异常:
          - RuntimeError: 如果解析失败则抛出异常
        """
        try:
            normalized = self._normalize_text(str_with_pads)
            # 将文本转为小写，确保标记匹配不受大小写影响
            normalized_lower = normalized.lower()
            start_pad = '=start_pad='
            end_pad = '=end_pad='
            start_index = normalized_lower.find(start_pad)
            end_index = normalized_lower.rfind(end_pad)
            if start_index == -1 or end_index == -1:
                raise ValueError(f"开始或结束标志未找到。原文字串为: {str_with_pads}")
            start_index += len(start_pad)
            content_str = normalized[start_index:end_index].strip()
            return content_str
        except Exception as e:
            raise RuntimeError(f"解析失败，错误信息：{e}。原文字串为: {str_with_pads}")

    def parse_code(self, markdown_text: str):
        """
        提取Markdown文本中被 ``` 包裹的代码块及其语言信息。
        本方法返回第一个匹配的代码块内容。

        参数:
          - markdown_text: 包含代码块的Markdown格式文本

        返回:
          - str: 代码块内容，如果未找到则返回 None
        """
        pattern = r'```([\w\s]+?)\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        if matches:
            # 如果需要返回语言信息，也可以通过 matches[0][0] 获取
            code = matches[0][1].strip()
            return code
        return None

    def parse_str(self, text: str):
        """
        原子方法，直接返回传入的文本内容。

        参数:
          - text: 字符串文本

        返回:
          - str: 原文本
        """
        return text
