from typing import Optional
from Task_Conductor.parser import LLMParser

class RelevanceTask:
    """
    处理摘要和关键字相关性的任务类，保持自然语言提示结构但使用JSON格式的示例输出
    """

    def __init__(self, abstract: str, keyword: str):
        self.abstract = abstract
        self.keyword = keyword
        self.llm_parser = LLMParser()

    def generate_prompt(self) -> str:
        """
        生成混合自然语言和JSON示例的提示词
        """
        prompt_template = """文章摘要：{abstract}
        用户指定的关键字：{keyword}

        任务：请根据以下摘要内容和关键字，给出它们的相关性评分：
        评分范围：0 表示完全不相关，1 表示完全相关。

        请严格按照以下JSON格式输出：
        {{
            "relevance_score": <0到1之间的数字>,
            "reason": "<评分理由>"
        }}

        示例：
        文章摘要：This paper discusses AI research and its applications.
        用户指定的关键字：AI
        输出：
        {{
            "relevance_score": 0.95,
            "reason": "摘要明确提到AI研究及其应用，与关键词直接相关"
        }}"""
        # 规范化处理
        normalized_abstract = self.llm_parser._normalize_text(self.abstract)
        normalized_keyword = self.llm_parser._normalize_text(self.keyword)
        
        return prompt_template.format(
            abstract=normalized_abstract,
            keyword=normalized_keyword
        )

    def parse_model_output(self, model_output: str) -> Optional[float]:
        """
        解析包含JSON结构的模型输出
        """
        try:
            # 使用LLMParser提取字典
            result_dict = self.llm_parser.parse_dict(model_output)
            
            # 验证必要字段
            if "relevance_score" not in result_dict:
                raise KeyError("缺少relevance_score字段")
                
            score = result_dict["relevance_score"]
            
            # 类型转换和范围验证
            try:
                score = float(score)
            except ValueError:
                raise TypeError("评分值无法转换为浮点数")
            
            if not 0 <= score <= 1:
                raise ValueError("评分超出0-1范围")
                
            return round(score, 2)  # 保留两位小数
            
        except Exception as e:
            print(f"解析错误：{str(e)}，原始输出：{model_output}")
            return None

# 测试用例
# if __name__ == "__main__":
#     # 正常案例
#     test_abstract = "深度学习模型在自然语言处理领域的突破性进展"
#     test_keyword = "神经网络"
    
#     task = RelevanceTask(test_abstract, test_keyword)
#     print("生成的提示词：")
#     print(task.generate_prompt())

#     # 测试解析
#     good_output = '''
#     这是模型思考过程：
#     该论文主要讨论深度学习在NLP的应用，而神经网络是其基础技术，
#     因此相关性很高。最终评分：
#     {
#         "relevance_score": 0.87,
#         "reason": "深度学习基于神经网络技术，具有直接相关性"
#     }
#     '''
#     print("\n测试有效输出解析：")
#     print("原始输出：", good_output)
#     print("解析结果：", task.parse_model_output(good_output))

#     # 测试错误案例
#     bad_output = "Invalid{json"
#     print("\n测试无效输出解析：")
#     print("解析结果：", task.parse_model_output(bad_output))
