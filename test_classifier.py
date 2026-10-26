# -*- coding: utf-8 -*-
"""分类器单元测试"""
import unittest
import json
import tempfile
import os

from lkong_sentinel.classifier import gate, THEMES, QUESTION_KW


class TestGate(unittest.TestCase):
    """测试三层相关性闸门"""

    def test_qidian_title(self):
        self.assertTrue(gate("起点这是要干嘛"))
        self.assertTrue(gate("阅文这是要干嘛"))
        self.assertFalse(gate("番茄这是要干嘛"))

    def test_editor_live(self):
        self.assertTrue(gate("星河直播说了什么"))
        self.assertTrue(gate("编辑部和官号开播了"))
        self.assertFalse(gate("星河动画开播了"))  # LIVE_EXCL

    def test_exclusive_keywords(self):
        self.assertTrue(gate("全勤改了"))
        self.assertTrue(gate("三江推荐"))
        self.assertFalse(gate("全勤改了番茄"))  # OTHER_PLAT


class TestQuestionDetection(unittest.TestCase):
    def test_question(self):
        from lkong_sentinel.classifier import is_question
        self.assertTrue(is_question("为什么起点这样"))
        self.assertTrue(is_question("新人求教？"))
        self.assertFalse(is_question("起点改规则了"))


if __name__ == "__main__":
    unittest.main()
