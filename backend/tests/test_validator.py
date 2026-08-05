import unittest
from app.utils.abc_validator import clean_and_validate_abc, beautify_abc_line


class TestAbcValidator(unittest.TestCase):
    def test_beautify_abc_line(self):
        # Explicitly tests the user's requested L:1/8 beautification algorithm:
        # '| f2 e2 d1 e1 d2 |' -> '| f2 e2 de d2 |'
        sample = "| f2 e2 d1 e1 d2 |"
        beautified = beautify_abc_line(sample, note_length="1/8")
        self.assertEqual(beautified, "| f2 e2 de d2 |")

    def test_beautify_abc_line_16th(self):
        # Tests the user's L:1/16 beautification example:
        # '| G2 B2 d2 g2 b3 a g2 e2 |' -> '| G2B2 d2g2 b3a g2e2 |'
        sample = "| G2 B2 d2 g2 b3 a g2 e2 | d3 e f2 g2 a2 d2 z2 c2 |"
        beautified = beautify_abc_line(sample, note_length="1/16")
        self.assertEqual(beautified, "| G2B2 d2g2 b3a g2e2 | d3e f2g2 a2d2 z2 c2 |")

    def test_validator_with_valid_abc(self):
        sample = (
            "X:1\n"
            "T:Test Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=120\n"
            "K:C\n"
            "CDEFGABc | cBAGFEDC |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample, expected_bars=2)
        self.assertTrue(is_valid)
        self.assertIn("X:1", clean_abc)
        self.assertIn("K:C", clean_abc)
        # Verify that eighth notes are grouped by beat pairs for beautiful beaming
        self.assertIn("CD EF GA Bc", clean_abc)

    def test_validator_with_voice_header_and_rests(self):
        sample = (
            "X:1\n"
            "T:Saxophone Rest Practice\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:G\n"
            "V:1\n"
            "G2 B2 z2 d2 | e2 d2 B2 z2 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample, expected_bars=2)
        self.assertTrue(is_valid)
        self.assertIn("V:1", clean_abc)
        self.assertIn("z2", clean_abc)
        self.assertIn("G2 B2 z2 d2", clean_abc)

    def test_validator_rejects_single_note_without_bars(self):
        sample = (
            "X:1\n"
            "T:Incomplete Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:G\n"
            "G4"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample, expected_bars=4)
        self.assertFalse(is_valid)
        self.assertTrue("measure(s)" in err or "missing musical measure content" in err)

    def test_validator_strips_trills_and_ornaments(self):
        sample = (
            "X:1\n"
            "T:Trill Test\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:G\n"
            "~G2 !trill!B2 \"tr\"d2 g2 | {cde}f2 d2 B2 G2 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample, expected_bars=2)
        self.assertTrue(is_valid)
        self.assertNotIn("~", clean_abc)
        self.assertNotIn("!trill!", clean_abc)
        self.assertNotIn("\"tr\"", clean_abc)
        self.assertNotIn("{cde}", clean_abc)
        self.assertIn("G2 B2 d2 g2", clean_abc)
        self.assertIn("f2 d2 B2 G2", clean_abc)

    def test_validator_rejects_headers_without_notes(self):
        sample = (
            "X:1\n"
            "T:Incomplete Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:G\n"
            "V:1"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample, expected_bars=4)
        self.assertFalse(is_valid)
        self.assertIn("missing musical measure content", err)

    def test_validator_strips_markdown_backticks(self):
        sample_with_ticks = (
            "```abc\n"
            "X:1\n"
            "T:Markdown Exercise\n"
            "K:G\n"
            "GABc d2 d2 |]\n"
            "```"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(sample_with_ticks, expected_bars=1)
        self.assertTrue(is_valid)
        self.assertNotIn("```", clean_abc)
        self.assertIn("X:1", clean_abc)
        self.assertIn("K:G", clean_abc)

    def test_validator_empty_response(self):
        is_valid, clean_abc, err = clean_and_validate_abc("")
        self.assertFalse(is_valid)
        self.assertIn("Empty response", err)


if __name__ == "__main__":
    unittest.main()
