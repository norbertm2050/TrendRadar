import unittest

from trendradar.report.dedupe import TitleDeduper, dedupe_items, normalize_title, title_similarity
from trendradar.report.html import render_html_content


class ReportDedupeTests(unittest.TestCase):
    def test_normalize_title_strips_noise(self):
        self.assertEqual(normalize_title("快讯：NVIDIA shares jump!"), "nvidiajump")

    def test_similar_titles_are_merged(self):
        items = [
            {"title": "就在下周四！科技四巨头同日财报，AI 面临验证时刻", "source_name": "华尔街见闻"},
            {"title": "科技四巨头同日财报 AI行情面临验证时刻", "source_name": "财联社"},
        ]
        unique = dedupe_items(items)
        self.assertEqual(len(unique), 1)
        self.assertIn("财联社", unique[0]["source_name"])
        self.assertEqual(unique[0]["duplicate_count"], 2)

    def test_feed_names_are_preserved_when_merged(self):
        items = [
            {"title": "SEC opens probe into chip company disclosure", "feed_name": "SEC"},
            {"title": "SEC probe into chip company disclosure", "feed_name": "CNBC Markets"},
        ]
        unique = dedupe_items(items)
        self.assertEqual(len(unique), 1)
        self.assertIn("SEC", unique[0]["source_name"])
        self.assertIn("CNBC Markets", unique[0]["source_name"])

    def test_html_render_dedupes_across_sections(self):
        title = "SEC opens probe into chip company disclosure"
        report_data = {
            "stats": [
                {
                    "word": "监管事故与安全事件",
                    "count": 1,
                    "titles": [
                        {"title": title, "source_name": "SEC", "count": 1, "ranks": [1]},
                    ],
                }
            ],
            "new_titles": [],
            "failed_ids": [],
            "total_new_count": 0,
        }
        rss_items = [
            {
                "word": "监管事故与安全事件",
                "count": 1,
                "titles": [
                    {"title": "SEC probe into chip company disclosure", "source_name": "CNBC Markets", "count": 1, "ranks": [1]},
                ],
            }
        ]
        html = render_html_content(report_data, total_titles=2, rss_items=rss_items)
        self.assertEqual(html.count(title), 1)

    def test_unrelated_titles_remain_separate(self):
        deduper = TitleDeduper()
        first = deduper.add({"title": "美联储释放降息信号", "source_name": "Fed"})
        second = deduper.add({"title": "台积电上调资本开支", "source_name": "WSJ"})
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertLess(title_similarity(first["title"], second["title"]), 0.72)


if __name__ == "__main__":
    unittest.main()
