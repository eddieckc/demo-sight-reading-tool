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

    def test_saxophone_valid_range(self):
        # Saxophone standard written range: Low Bb3 (_B,) to High F6 (f')
        sample = (
            "X:1\n"
            "T:Valid Saxophone Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "_B,2 C2 D2 E2 | F2 G2 A2 B2 | c2 d2 e2 f2 | f'4 z4 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=4, instrument="saxophone", difficulty="intermediate"
        )
        self.assertTrue(is_valid)
        self.assertEqual(err, "")
        self.assertIn("_B,2", clean_abc)

    def test_saxophone_rejects_note_below_low_bb(self):
        # Saxophone cannot play below low Bb3 (_B,). Note A, (MIDI 57) or G, (MIDI 55) must be rejected!
        sample = (
            "X:1\n"
            "T:Out of Range Saxophone Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "A,2 C2 D2 E2 | F2 G2 A2 B2 | c2 d2 e2 f2 | g2 z2 z4 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=4, instrument="saxophone"
        )
        self.assertFalse(is_valid)
        self.assertIn("below the minimum playable pitch '_B,'", err)

    def test_saxophone_rejects_altissimo_note_above_high_f(self):
        # Saxophone standard range ends at High F6 (f') / F#6 (^f'). Notes like g' (MIDI 91) or c'' (MIDI 96) must be rejected!
        sample = (
            "X:1\n"
            "T:Altissimo Saxophone Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "C2 D2 E2 F2 | G2 A2 B2 c2 | d2 e2 f2 g2 | c''4 z4 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=4, instrument="saxophone"
        )
        self.assertFalse(is_valid)
        self.assertIn("above the maximum playable pitch 'f''", err)

    def test_flute_rejects_note_below_middle_c(self):
        # Standard flute cannot play below Middle C4 (C)
        sample = (
            "X:1\n"
            "T:Flute Low Note Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "G,2 B,2 C2 D2 | E2 F2 G2 A2 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=2, instrument="flute"
        )
        self.assertFalse(is_valid)
        self.assertIn("below the minimum playable pitch 'C'", err)

    def test_violin_rejects_note_below_open_g(self):
        # Violin lowest open string is G3 (G,). Notes below G, (e.g. F, or E,) must be rejected!
        sample = (
            "X:1\n"
            "T:Violin Out of Range\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "F,2 G,2 A,2 B,2 | C2 D2 E2 F2 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=2, instrument="violin"
        )
        self.assertFalse(is_valid)
        self.assertIn("below the minimum playable pitch 'G,'", err)

    def test_cello_enforces_bass_clef(self):
        sample = (
            "X:1\n"
            "T:Cello Exercise\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=90\n"
            "K:C\n"
            "C,,2 D,,2 E,,2 F,,2 | G,,2 A,,2 B,,2 C,2 |]"
        )
        is_valid, clean_abc, err = clean_and_validate_abc(
            sample, expected_bars=2, instrument="cello"
        )
        self.assertTrue(is_valid)
        self.assertIn("clef=bass", clean_abc)


if __name__ == "__main__":
    unittest.main()

