from __future__ import annotations

import pytest
from src.utils.image_converter import extract_nano_banana_images, extract_gt4o_images


class TestExtractNanoBananaImages:
    """测试 Nano-banana 图片 URL 提取"""

    def test_extract_single_image(self) -> None:
        """测试提取单张图片"""
        sse_data = '{"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/xxx.jpg)\\n","code":0}'
        images = extract_nano_banana_images(sse_data)
        assert len(images) == 1
        assert images[0] == "https://cn-nb1.rains3.com/jay/xxx.jpg"

    def test_extract_multiple_images(self) -> None:
        """测试提取多张图片"""
        sse_data = '''data: {"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/1.jpg)\\n","code":0}
data: {"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/2.jpg)\\n","code":0}
data: {"id":"...","type":"string","data":"\\n\\n![image](https://cn-nb1.rains3.com/jay/3.jpg)\\n","code":0}'''
        images = extract_nano_banana_images(sse_data)
        assert len(images) == 3
        assert images == [
            "https://cn-nb1.rains3.com/jay/1.jpg",
            "https://cn-nb1.rains3.com/jay/2.jpg",
            "https://cn-nb1.rains3.com/jay/3.jpg"
        ]

    def test_no_image(self) -> None:
        """测试无图片情况"""
        sse_data = '{"id":"...","type":"string","data":"没有图片","code":0}'
        images = extract_nano_banana_images(sse_data)
        assert images == []

    def test_https_url(self) -> None:
        """测试 HTTPS URL"""
        sse_data = 'data: {"id":"...","type":"string","data":"\\n\\n![image](https://example.com/image.png)\\n","code":0}'
        images = extract_nano_banana_images(sse_data)
        assert len(images) == 1
        assert images[0] == "https://example.com/image.png"


class TestExtractGT4OImages:
    """测试 GT-4o-image-vip 图片 URL 提取"""

    def test_extract_single_image(self) -> None:
        """测试提取单张图片"""
        sse_data = '{"id":"...","type":"string","data":"\\n\\n![gen_01kmjacvgnfwx8zbnfm28amn46](https://pro.filesystem.site/cdn/xxx.png)\\n","code":0}'
        images = extract_gt4o_images(sse_data)
        assert len(images) == 1
        assert images[0] == "https://pro.filesystem.site/cdn/xxx.png"

    def test_extract_multiple_images(self) -> None:
        """测试提取多张图片"""
        sse_data = '''data: {"id":"...","data":"\\n\\n![gen_01kmjacvgnfwx8zbnfm28amn46](https://pro.filesystem.site/cdn/1.png)\\n"}
data: {"id":"...","data":"\\n\\n![gen_02abcdefghijklmnopqrstuv](https://pro.filesystem.site/cdn/2.png)\\n"}'''
        images = extract_gt4o_images(sse_data)
        assert len(images) == 2
        assert images == [
            "https://pro.filesystem.site/cdn/1.png",
            "https://pro.filesystem.site/cdn/2.png"
        ]

    def test_no_image(self) -> None:
        """测试无图片情况"""
        sse_data = '{"id":"...","type":"string","data":"没有图片","code":0}'
        images = extract_gt4o_images(sse_data)
        assert images == []

    def test_different_gen_id(self) -> None:
        """测试不同格式的 gen_id"""
        sse_data = '![gen_abc123](https://example.com/img.png)'
        images = extract_gt4o_images(sse_data)
        assert len(images) == 1
        assert images[0] == "https://example.com/img.png"
