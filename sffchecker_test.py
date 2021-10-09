import unittest
import sffchecker
from sffchecker import (
    normalize_authors,
    normalize_author,
    lookslikeinitial,
    group_by_collection,
    group_by_title,
    remove_last_number,
    grab_last_number,
    lookup_match_authors,
    scan_dir,
)


class SFFCheckerTest(unittest.TestCase):
    def setUp(self):
        sffchecker.opts = sffchecker.opts_parser.parse_args()
        sffchecker.opts.debug = False

    def tearDown(self):
        pass


class CalibreInitialMatcher(SFFCheckerTest):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_smoke1(self):
        self.assertTrue(lookslikeinitial("P."))
        self.assertTrue(lookslikeinitial("P. T."))
        self.assertFalse(lookslikeinitial("Jo"))


class RemoveLastNumber(SFFCheckerTest):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_smoke1(self):
        self.assertEqual(remove_last_number("ten10"), "ten10")
        self.assertEqual(remove_last_number("ten 10"), "ten")
        self.assertEqual(remove_last_number("ten 10 "), "ten")
        self.assertEqual(remove_last_number("10 10"), "10")
        self.assertEqual(remove_last_number("1 1"), "1")
        self.assertEqual(remove_last_number("ten10 10"), "ten10")
        self.assertEqual(remove_last_number("ten 1 "), "ten")
        self.assertEqual(remove_last_number(" ten1 "), "ten1")
        self.assertEqual(remove_last_number(" ten 1 "), "ten")
        self.assertEqual(remove_last_number("ten 1 ten1"), "ten")

    def test_inserts(self):
        self.assertEqual(remove_last_number("ten 1.5"), "ten")


class GrabLastNumber(SFFCheckerTest):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_smoke1(self):
        self.assertEqual(grab_last_number("ten10"), None)
        self.assertEqual(grab_last_number("ten 10"), "10")
        self.assertEqual(grab_last_number("ten 10 "), "10")
        self.assertEqual(grab_last_number("10 10"), "10")
        self.assertEqual(grab_last_number("1 1"), "1")
        self.assertEqual(grab_last_number("ten10 10"), "10")
        self.assertEqual(grab_last_number("ten 1 "), "1")
        self.assertEqual(grab_last_number(" ten1 "), None)
        self.assertEqual(grab_last_number(" ten 1 "), "1")
        self.assertEqual(grab_last_number("ten 1 ten1"), None)

    def test_inserts(self):
        self.assertEqual(grab_last_number("ten 1.5"), "1.5")


class CalibreNormalizer(SFFCheckerTest):
    def setUp(self):
        super(CalibreNormalizer, self).setUp()

    def tearDown(self):
        pass

    def test_smoke1(self):
        guesses = normalize_author("Simon GOOGWILL")
        self.assertIn("Simon Googwill", guesses)
        self.assertIn("S. Googwill", guesses)

    def test_smoke2(self):
        guesses = normalize_author("Simon GOOGWILL")
        self.assertIn("Simon Googwill", guesses)
        self.assertIn("S. Googwill", guesses)

    def test_smoke4(self):
        guesses = normalize_author("A.G. Riddle")
        self.assertIn("A. G. Riddle", guesses)
        self.assertIn("A. Riddle", guesses)

    def test_author_3parts(self):
        guesses = normalize_author("Adolfo Bioy Casares")
        self.assertIn("Adolfo Bioy Casares", guesses)
        self.assertIn("Adolfo B. Casares", guesses)
        self.assertIn("A. B. Casares", guesses)
        self.assertIn("Adolfo Casares", guesses)
        self.assertIn("A. Casares", guesses)

    def test_author_2initiales(self):
        guesses = normalize_author("Ruth L. C. Simms")
        self.assertIn("Ruth L. C. Simms", guesses)
        self.assertIn("Ruth Simms", guesses)
        self.assertIn("R. L. C. Simms", guesses)
        self.assertIn("R. Simms", guesses)

    def test_author_2initiales2(self):
        guesses = normalize_author("Ruth L.C. Simms")
        self.assertIn("Ruth L. C. Simms", guesses)
        self.assertIn("Ruth Simms", guesses)
        self.assertIn("R. L. C. Simms", guesses)
        self.assertIn("R. Simms", guesses)

    def test_author_forgetadot(self):
        guesses = normalize_author("Alfred E van Vogt")
        self.assertIn("Alfred E. Van Vogt", guesses)
        self.assertIn("Alfred E. van Vogt", guesses)
        self.assertIn("A. E. Van Vogt", guesses)
        self.assertIn("A. E. V. Vogt", guesses)

    def test_author_van_or_Van(self):
        guesses = normalize_author("Alfred E Van Vogt")
        self.assertIn("Alfred E. Van Vogt", guesses)
        self.assertIn("Alfred E. van Vogt", guesses)
        self.assertIn("A. E. Van Vogt", guesses)
        self.assertIn("A. E. V. Vogt", guesses)


class CalibreMultiNormalizer(SFFCheckerTest):
    def setUp(self):
        super(CalibreMultiNormalizer, self).setUp()

    def tearDown(self):
        pass

    def test_reverse(self):
        guesses = normalize_authors("GOOGWILL, simon")
        self.assertIn("Simon Googwill", guesses)
        self.assertIn("S. Googwill", guesses)

    def test_multi_author1(self):
        guesses = normalize_authors("Adolfo Bioy Casares; Ruth L. C. Simms")
        self.assertIn("Ruth L. C. Simms", guesses)
        self.assertIn("Adolfo Bioy Casares", guesses)


class GroupByTitle(SFFCheckerTest):
    def setUp(self):
        super(GroupByTitle, self).setUp()

    def tearDown(self):
        pass

    def test_nogroup(self):
        titles = [
            {"title": "Title1.epub", "number": "01", "status": True, "extra": "extra1"},
            {"title": "Title2.epub", "number": "01", "status": True, "extra": "extra2"},
        ]
        g = group_by_title(titles)
        self.assertEqual(len(g), 2)
        self.assertEqual(len(g[0]["suffix"]), 1)
        self.assertEqual(len(g[1]["suffix"]), 1)
        self.assertEqual(g[0]["title"], "Title1")
        self.assertEqual(g[1]["title"], "Title2")
        self.assertEqual(g[0]["suffix"][0], "epub")
        self.assertEqual(g[1]["suffix"][0], "epub")

    def test_1group(self):
        titles = [
            {"title": "Title1.epub", "number": "01", "status": True, "extra": "extra1"},
            {"title": "Title1.mobi", "number": "01", "status": True, "extra": "extra1"},
        ]
        g = group_by_title(titles)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["title"], "Title1")
        self.assertEqual(len(g[0]["suffix"]), 2)
        self.assertEqual(g[0]["suffix"][0], "epub")
        self.assertEqual(g[0]["suffix"][1], "mobi")


class GroupByCollections(SFFCheckerTest):
    def setUp(self):
        super(GroupByCollections, self).setUp()

    def tearDown(self):
        pass

    def test_nogroup(self):
        status_title = [
            [True, "Author - Title1.epub"],
            [True, "Author - Title2.epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "__none__")

    def test_2titles(self):
        status_title = [
            [True, "Author - Title1.epub"],
            [True, "Author - Title2.epub"],
            [True, "Author - Title2.mobi"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "__none__")

    def test_1collection(self):
        status_title = [
            [True, "Author - Collection1 - Title1.epub"],
            [True, "Author - Collection1 - Title2.epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "Collection1")

    def test_2collections(self):
        status_title = [
            [True, "Author - Collection1 - Title1.epub"],
            [True, "Author - Collection1 - Title2.epub"],
            [True, "Author - Collection2 - Title3.epub"],
            [True, "Author - Collection2 - Title4.epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 2)
        self.assertEqual(g[0]["collection"], "Collection1")
        self.assertEqual(g[1]["collection"], "Collection2")

    def test_1collection_with_numbers(self):
        status_title = [
            [True, "Author - Collection 1 - Title1.epub"],
            [True, "Author - Collection 2 - Title2.epub"],
            [True, "Author - Collection 2 - Title2.epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "Collection")
        self.assertEqual(g[0]["titles"][0]["title"], "Title1")
        self.assertEqual(g[0]["titles"][0]["suffix"][0], "epub")
        self.assertEqual(g[0]["titles"][1]["title"], "Title2")
        self.assertEqual(g[0]["titles"][1]["suffix"][0], "epub")

    def test_1collection_with_numbers_and_dash(self):
        status_title = [
            [True, "Author - Collection - 1 - Title1.epub"],
            [True, "Author - Collection - 2 - Title2.epub"],
            [True, "Author - Collection - 2 - Title2.epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "Collection")
        self.assertEqual(g[0]["titles"][0]["title"], "Title1")
        self.assertEqual(g[0]["titles"][0]["suffix"][0], "epub")
        self.assertEqual(g[0]["titles"][1]["title"], "Title2")
        self.assertEqual(g[0]["titles"][1]["suffix"][0], "epub")

    def test_dash(self):
        status_title = [
            [True, "author - collection 01 - title1 # (v1.0).epub"],
            [False, "author - collection 02 - title2 # (v1.1).epub"],
        ]
        g = group_by_collection(status_title)
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["collection"], "collection")
        self.assertEqual(g[0]["titles"][0]["title"], "title1")
        self.assertEqual(g[0]["titles"][0]["number"], "01")
        self.assertEqual(g[0]["titles"][0]["status"], True)
        self.assertEqual(g[0]["titles"][0]["extra"], "(v1.0)")
        self.assertEqual(g[0]["titles"][1]["title"], "title2")
        self.assertEqual(g[0]["titles"][1]["number"], "02")
        self.assertEqual(g[0]["titles"][1]["status"], False)
        self.assertEqual(g[0]["titles"][1]["extra"], "(v1.1)")


class CheckOnGoldDatas(SFFCheckerTest):
    def setUp(self):
        super(CheckOnGoldDatas, self).setUp()
        self.dir_calibre = "./tests/t1/calibre"
        self.dir_sffupdate = "./tests/t1/sff"
        self.calibre = scan_dir(self.dir_calibre)
        self.sff = set(scan_dir(self.dir_sffupdate))
        self.author = None
        # print('(debug) len(calibre)={0} len(sff)={1}'.format(len(self.calibre), len(self.sff)))

    def tearDown(self):
        pass

    def test_sanity(self):
        exact, notfound = lookup_match_authors(self.calibre, self.sff, self.author)
        self.assertEqual(len(exact), 1)
        self.assertEqual(len(exact[0]), 2)
        self.assertEqual(len(notfound), 0)


if __name__ == "__main__":
    unittest.main()
