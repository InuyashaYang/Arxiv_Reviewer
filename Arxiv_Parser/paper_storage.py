import os
import json

# =================== 论文数据存储相关函数 =================== #
def save_paper_data(data, file_path):
    """
    将论文数据以 JSON 格式保存到指定文件中。

    参数：
      - data (dict): 论文数据字典，通常包含 "title"、"abstract"、"sections"、"references" 等字段。
      - file_path (str): 保存 JSON 文件的完整路径（例如 "output/my_paper.json"）。

    功能：
      - 如果保存路径中的目录不存在，则自动创建目录。
      - 使用 UTF-8 编码，确保中文等非 ASCII 字符能正确保存。
      - 将数据以缩进格式写入文件，便于人工检查。
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"目录 {directory} 创建成功。")
        except Exception as e:
            print(f"创建目录 {directory} 失败：{e}")
            return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"论文数据成功保存到 {file_path}")
    except Exception as e:
        print(f"保存论文数据时出错：{e}")

def load_paper_data(file_path):
    """
    从指定的 JSON 文件中加载论文数据。

    参数：
      - file_path (str): 包含论文数据的 JSON 文件路径。

    返回：
      - dict: 解析后的论文数据字典；如果文件不存在或解析出错，则返回 None。
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"论文数据成功从 {file_path} 加载。")
        return data
    except Exception as e:
        print(f"加载论文数据时出错：{e}")
        return None
