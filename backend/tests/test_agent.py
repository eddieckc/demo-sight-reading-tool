import unittest
from google.adk.agents import Agent
from app.agent import (
    create_sight_reading_agent,
    build_composition_prompt,
    validate_abc_score_tool,
    SYSTEM_INSTRUCTION,
)
from app.schemas.exercise import ExerciseRequest


class TestAdkAgentEngine(unittest.TestCase):
    def test_adk_agent_factory(self):
        agent = create_sight_reading_agent()
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.name, "sight_reading_composer")
        self.assertIn("sight-reading", agent.description)
        self.assertEqual(len(agent.tools), 1)

    def test_build_composition_prompt(self):
        req = ExerciseRequest(
            difficulty="intermediate",
            key_signature="G",
            instrument="saxophone",
            time_signature="4/4",
            tempo=110,
            bars=4,
        )
        prompt = build_composition_prompt(req)
        self.assertIn("SAXOPHONE", prompt)
        self.assertIn("INTERMEDIATE LEVEL", prompt)
        self.assertIn("_B,", prompt)
        self.assertIn("EXACTLY 4 BARS REQUIRED", prompt)
        self.assertIn("no TR skill", prompt)

    def test_build_composition_prompt_with_retry_error(self):
        req = ExerciseRequest(
            difficulty="intermediate",
            key_signature="G",
            instrument="saxophone",
            time_signature="4/4",
            tempo=110,
            bars=4,
        )
        retry_err = "Pitch 'A,' (MIDI 57) is below the minimum playable pitch '_B,' for Saxophone."
        prompt = build_composition_prompt(req, previous_error=retry_err)
        self.assertIn("PREVIOUS ATTEMPT CORRECTION NEEDED", prompt)
        self.assertIn(retry_err, prompt)

    def test_build_composition_prompt_16_bars(self):
        req = ExerciseRequest(
            difficulty="advanced",
            key_signature="G",
            instrument="violin",
            time_signature="4/4",
            tempo=120,
            bars=16,
        )
        prompt = build_composition_prompt(req)
        self.assertIn("VIOLIN", prompt)
        self.assertIn("Line 4: bar 13 | bar 14 | bar 15 | bar 16 |]", prompt)
        self.assertIn("no TR skill", prompt)

    def test_validate_abc_score_tool(self):
        sample = (
            "X:1\n"
            "T:Test Score\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:G\n"
            "G2 B2 d2 g2 | f2 d2 z2 G2 | c2 e2 d2 B2 | A4 G2 z2 |]"
        )
        result = validate_abc_score_tool(sample, expected_bars=4, instrument="violin")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["expected_bars"], 4)
        self.assertIn("G2 B2 d2 g2", result["cleaned_abc"])

    def test_validate_abc_score_tool_rejects_out_of_range(self):
        sample = (
            "X:1\n"
            "T:Test Score\n"
            "M:4/4\n"
            "L:1/8\n"
            "Q:1/4=110\n"
            "K:C\n"
            "A,2 C2 D2 E2 | F2 G2 A2 B2 | c2 d2 e2 f2 | g2 z2 z4 |]"
        )
        result = validate_abc_score_tool(sample, expected_bars=4, instrument="saxophone")
        self.assertFalse(result["is_valid"])
        self.assertIn("below the minimum playable pitch '_B,'", result["error_message"])


if __name__ == "__main__":
    unittest.main()

