import re
import bs4
import requests

# =================== 论文解析相关函数 =================== #
def parse_metadata(metas):
    """
    将论文引用的元数据字符串解析成作者、标题和期刊等信息
    """
    metas = [item.replace('\n', ' ') for item in metas]
    meta_string = ' '.join(metas)
    authors, title, journal = "", "", ""
    if len(metas) == 3:  # 分别为 author, title, journal
        authors, title, journal = metas
    else:
        meta_string = re.sub(r'\.\s\d{4}[a-z]?\.', '.', meta_string)
        regex = r"^(.*?\.\s)(.*?)(\.\s.*|$)"
        match = re.match(regex, meta_string, re.DOTALL)
        if match:
            authors = match.group(1).strip() if match.group(1) else ""
            title = match.group(2).strip() if match.group(2) else ""
            journal = match.group(3).strip() if match.group(3) else ""
            if journal.startswith('. '):
                journal = journal[2:]
    return {
        "meta_list": metas,
        "meta_string": meta_string,
        "authors": authors,
        "title": title,
        "journal": journal
    }

def create_dict_for_citation(cite_element):
    """
    根据引用元素（包含 li 元素）创建引用字典
    """
    citation_dict, id_attrs, meta_list = {}, [], []
    for li in cite_element.find_all("li", recursive=False):
        id_attr = li.get('id', '')
        metas = [x.text.strip() for x in li.find_all('span', class_='ltx_bibblock')]
        id_attrs.append(id_attr)
        meta_list.append(parse_metadata(metas))
    citation_dict = dict(zip(id_attrs, meta_list))
    return citation_dict

def generate_full_toc(soup):
    """
    根据 HTML 中的标题（h1 ~ h5）生成论文目录（toc）
    """
    toc = []
    stack = [(0, toc)]
    heading_tags = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5}
    for tag in soup.find_all(list(heading_tags.keys())):
        level = heading_tags[tag.name]
        title = tag.get_text()
        while stack and stack[-1][0] >= level:
            stack.pop()
        current_level = stack[-1][1]
        section = tag.find_parent('section', id=True)
        section_id = section.get('id') if section else None
        new_entry = {'title': title, 'id': section_id, 'subsections': []}
        current_level.append(new_entry)
        stack.append((level, new_entry['subsections']))
    return toc

def parse_text(local_text, tag):
    """
    递归提取标签内的文本，同时跳过不需要的标签
    """
    ignore_tags = ['a', 'figure', 'center', 'caption', 'td', 'h1', 'h2', 'h3', 'h4']
    ignore_tags += ['sup']
    max_math_length = 300000

    for child in tag.children:
        if isinstance(child, bs4.element.NavigableString):
            local_text.append(str(child))
        elif isinstance(child, bs4.element.Comment):
            continue
        elif isinstance(child, bs4.element.Tag):
            if child.name in ignore_tags or (child.has_attr('class') and child['class'][0] == 'navigation'):
                continue
            elif child.name == 'cite':
                hrefs = [a.get('href').strip('#') for a in child.find_all('a', class_='ltx_ref')]
                local_text.append('~\\cite{' + ', '.join(hrefs) + '}')
            elif child.name == 'img' and child.has_attr('alt'):
                math_txt = child.get('alt')
                if len(math_txt) < max_math_length:
                    local_text.append(math_txt)
            elif child.has_attr('class') and (child['class'][0] in ['ltx_Math', 'ltx_equation']):
                math_txt = child.get_text()
                if len(math_txt) < max_math_length:
                    local_text.append(math_txt)
            elif child.name == 'section':
                return  # 不递归 section 标签内部
            else:
                parse_text(local_text, child)
        else:
            raise RuntimeError('Unhandled type')

def clean_text(text):
    """
    对提取到的文本进行清洗
    """
    delete_items = ['=-1', '\t', u'\xa0', '[]', '()', 'mathbb', 'mathcal', 'bm', 
                    'mathrm', 'mathit', 'mathbf', 'mathbfcal', 'textbf', 'textsc', 
                    'langle', 'rangle', 'mathbin']
    for item in delete_items:
        text = text.replace(item, '')
    text = re.sub(' +', ' ', text)
    text = re.sub(r'[[,]+]', '', text)
    text = re.sub(r'\.(?!\d)', '. ', text)
    text = re.sub('bib. bib', 'bib.bib', text)
    return text

def remove_stop_word_sections_and_extract_text(toc, soup, stop_words=['references', 'acknowledgments', 'about this document', 'apopendix']):
    """
    去除目录中包含停止词的 section，并为剩下的 section 提取文本
    """
    def has_stop_word(title, stop_words):
        return any(stop_word.lower() in title.lower() for stop_word in stop_words)
    
    def extract_text(entry, soup):
        section_id = entry['id']
        if section_id:
            section = soup.find(id=section_id)
            if section is not None:
                local_text = []
                parse_text(local_text, section)
                if local_text:
                    processed_text = clean_text(''.join(local_text))
                    entry['text'] = processed_text
        return
    
    def filter_and_update_toc(entries):
        filtered_entries = []
        for entry in entries:
            if not has_stop_word(entry['title'], stop_words):
                extract_text(entry, soup)
                entry['subsections'] = filter_and_update_toc(entry['subsections'])
                filtered_entries.append(entry)
        return filtered_entries
    
    return filter_and_update_toc(toc)

def parse_html(html_file):
    """
    解析 arXiv 论文 HTML，提取标题、摘要、目录和参考文献等信息
    """
    soup = bs4.BeautifulSoup(html_file, "lxml")
    title = soup.head.title.get_text().replace("\n", " ") if soup.head and soup.head.title else ""
    abstract_div = soup.find(class_='ltx_abstract')
    abstract = abstract_div.get_text() if abstract_div else ""
    citation = soup.find(class_='ltx_biblist')
    citation_dict = create_dict_for_citation(citation) if citation else {}
    sections = generate_full_toc(soup)
    sections = remove_stop_word_sections_and_extract_text(sections, soup)
    document = {
        "title": title,
        "abstract": abstract,
        "sections": sections,
        "references": citation_dict,
    }
    return document
