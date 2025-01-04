import os
import folder_paths
import json

class MarkmapNode:
    """
    将Markdown文本转换为思维导图的节点
    """
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), 'markmap')
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "markdown_text": ("STRING", {"multiline": True}),
                "filename": ("STRING", {"default": "mindmap.html"})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "create_markmap"
    CATEGORY = "markmap"

    def create_markmap(self, markdown_text, filename):
        # 确保文件名以.html结尾
        if not filename.endswith('.html'):
            filename += '.html'
            
        # 使用规范化的路径
        output_path = os.path.normpath(os.path.join(self.output_dir, filename))
        
        # 读取模板文件
        template_path = os.path.join(self.static_dir, 'markmap.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # 确保markdown文本格式正确
        markdown_lines = markdown_text.split('\n')
        markdown_lines = [line.strip() for line in markdown_lines if line.strip()]
        # 确保第一行是标题
        if not markdown_lines[0].startswith('#'):
            markdown_lines.insert(0, '# Mindmap')
        
        # 解析markdown为树形结构
        def parse_markdown(lines):
            root = {"content": lines[0].lstrip('#').strip(), "children": [], "payload": {"tag": "h1", "lines": "0,1"}}
            current_level = 1
            current_node = root
            parent_stack = []
            line_number = 1
            
            for line in lines[1:]:
                if line.startswith('#'):
                    level = len(line.split()[0])
                    content = line.lstrip('#').strip()
                    node = {"content": content, "children": [], "payload": {"tag": f"h{level}", "lines": f"{line_number},{line_number+1}"}}
                    
                    while len(parent_stack) >= level - 1:
                        parent_stack.pop()
                    
                    parent = parent_stack[-1] if parent_stack else root
                    parent["children"].append(node)
                    parent_stack.append(node)
                    current_node = node
                elif line.startswith('-'):
                    content = line.lstrip('- ').strip()
                    node = {"content": content, "children": [], "payload": {"tag": "li", "lines": f"{line_number},{line_number+1}"}}
                    current_node["children"].append(node)
                
                line_number += 1
            
            return root
        
        # 生成数据结构
        data = parse_markdown(markdown_lines)
        
        # 替换模板中的数据
        html_content = html_template.replace('{{data}}', json.dumps(data))
        
        # 使用UTF-8编码保存文件，不带BOM
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html_content)
            
        return (output_path,)

class ReadHtmlNode:
    """
    读取HTML文件内容并输出文本的节点
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "read_html"
    CATEGORY = "markmap"

    def read_html(self, file_path):
        # 确保文件存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 读取HTML文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return (html_content,)

# 更新节点列表
NODE_CLASS_MAPPINGS = {
    "MarkmapNode": MarkmapNode,
    "ReadHtmlNode": ReadHtmlNode
}

# 更新节点显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "MarkmapNode": "Markdown to Mindmap",
    "ReadHtmlNode": "Read HTML Content"
} 