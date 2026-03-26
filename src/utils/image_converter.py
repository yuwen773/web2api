import re
from typing import List

def extract_nano_banana_images(sse_data: str) -> List[str]:
    """从 Nano-banana SSE 响应中提取图片 URL

    Nano-banana 响应格式:
    data: {"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/xxx.jpg)\\n","code":0}

    返回: ["https://cn-nb1.rains3.com/jay/xxx.jpg"]
    """
    # 匹配 ![image](url) 格式
    pattern = r'!\[image\]\((https?://[^\s)]+)\)'
    return re.findall(pattern, sse_data)

def extract_gt4o_images(sse_data: str) -> List[str]:
    """从 GT-4o-image-vip SSE 响应中提取图片 URL

    GT-4o-image-vip 响应格式:
    data: {"id":"...","type":"string","data":"\\n\\n![gen_01kmjacvgnfwx8zbnfm28amn46](https://pro.filesystem.site/cdn/xxx.png)\\n","code":0}

    返回: ["https://pro.filesystem.site/cdn/xxx.png"]
    """
    # 匹配 ![gen_xxx](url) 格式
    pattern = r'!\[gen_[^\]]*\]\((https?://[^\s)]+)\)'
    return re.findall(pattern, sse_data)
