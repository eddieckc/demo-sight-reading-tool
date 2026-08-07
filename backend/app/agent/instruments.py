"""
Individualized Instrument Skills & Character Profiles for the Google ADK Sight-Reading Composer Agent.
Each instrument has tailored pedagogical rules specifying range, clef, phrasing, ABC pitch limits, and playing character.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentRange:
    clef: str
    min_midi: int  # Absolute lowest playable MIDI pitch
    max_midi: int  # Absolute highest standard playable MIDI pitch
    min_abc: str   # ABC notation string of lowest note
    max_abc: str   # ABC notation string of highest note
    min_name: str  # Human readable lowest note (e.g., "Low Bb3")
    max_name: str  # Human readable highest note (e.g., "High F6")
    difficulty_ranges: Dict[str, Dict[str, Any]]
    negative_rules: str
    playing_character: str
    idiomatic_technique: str


INSTRUMENT_CONFIGS: Dict[str, InstrumentRange] = {
    "saxophone": InstrumentRange(
        clef="treble",
        min_midi=58,  # Low Bb3 (_B, or ^A,)
        max_midi=90,  # High F#6 (^f') / High F6 (f' = 89)
        min_abc="_B,",
        max_abc="f'",
        min_name="Low Bb3",
        max_name="High F6",
        difficulty_ranges={
            "beginner": {
                "min_midi": 62, "max_midi": 72,
                "min_abc": "D", "max_abc": "c",
                "desc": "D4 to C5 (middle register, no palm keys, comfortable fingerings)"
            },
            "intermediate": {
                "min_midi": 58, "max_midi": 77,
                "min_abc": "_B,", "max_abc": "f",
                "desc": "Low Bb3 to F5 (two full octaves up to high F5)"
            },
            "advanced": {
                "min_midi": 58, "max_midi": 86,
                "min_abc": "_B,", "max_abc": "d'",
                "desc": "Low Bb3 to High D6 (including octave key upper register)"
            },
            "expert": {
                "min_midi": 58, "max_midi": 90,
                "min_abc": "_B,", "max_abc": "f'",
                "desc": "Low Bb3 to High F6 / F#6 (full standard acoustic range)"
            },
        },
        negative_rules=(
            "- ABSOLUTE RANGE CONSTRAINTS: Standard saxophone can ONLY play from Low Bb3 ('_B,') to High F6 ('f'') / High F#6 ('^f'').\n"
            "- CRITICAL PROHIBITION: NEVER use notes below '_B,' (e.g. 'A,', 'G,', 'F,', 'E,', 'D,', 'C,', 'C,,' DO NOT EXIST on saxophone!).\n"
            "- CRITICAL PROHIBITION: NEVER use altissimo notes above 'f'' / '^f'' (e.g. 'g'', 'a'', 'b'', 'c''')."
        ),
        playing_character="Lyrical jazz/classical woodwind phrasing, smooth scalar motion, arpeggiated figures, and syncopated rhythms.",
        idiomatic_technique="Include natural breathing rests ('z' or 'z2') suitable for woodwind breath control. Avoid awkward wide interval leaps."
    ),
    "flute": InstrumentRange(
        clef="treble",
        min_midi=60,  # Middle C4 (C) or Low B3 (B, = 59)
        max_midi=96,  # High C7 (c'')
        min_abc="C",
        max_abc="c''",
        min_name="Middle C4",
        max_name="High C7",
        difficulty_ranges={
            "beginner": {
                "min_midi": 65, "max_midi": 79,
                "min_abc": "F", "max_abc": "g",
                "desc": "F4 to G5 (comfortable beginner flute register)"
            },
            "intermediate": {
                "min_midi": 62, "max_midi": 86,
                "min_abc": "D", "max_abc": "d'",
                "desc": "D4 to D6 (agile two-octave middle/upper register)"
            },
            "advanced": {
                "min_midi": 60, "max_midi": 91,
                "min_abc": "C", "max_abc": "g'",
                "desc": "C4 to G6 (full standard range with agile upper register)"
            },
            "expert": {
                "min_midi": 60, "max_midi": 96,
                "min_abc": "C", "max_abc": "c''",
                "desc": "C4 to C7 (full three-octave virtuosic concert flute range)"
            },
        },
        negative_rules=(
            "- ABSOLUTE RANGE CONSTRAINTS: Standard concert flute begins at Middle C4 ('C') and reaches High C7 ('c''').\n"
            "- CRITICAL PROHIBITION: NEVER use notes below 'C' (e.g. 'B,', 'A,', 'G,', 'F,', 'E,', 'D,', 'C,' DO NOT EXIST on standard flute!)."
        ),
        playing_character="Bright, agile melodic phrasing, step-wise runs, and classical broken chords.",
        idiomatic_technique="Include frequent breathing rests ('z' or 'z2') for natural woodwind breath control."
    ),
    "violin": InstrumentRange(
        clef="treble",
        min_midi=55,  # Low G3 (G,) open G string
        max_midi=96,  # High C7 (c'') / A6 (a' = 93)
        min_abc="G,",
        max_abc="a'",
        min_name="Low G3 (open G string)",
        max_name="High A6",
        difficulty_ranges={
            "beginner": {
                "min_midi": 55, "max_midi": 83,
                "min_abc": "G,", "max_abc": "b",
                "desc": "G3 to B5 (1st position across G, D, A, E strings)"
            },
            "intermediate": {
                "min_midi": 55, "max_midi": 86,
                "min_abc": "G,", "max_abc": "d'",
                "desc": "G3 to D6 (1st and 3rd positions)"
            },
            "advanced": {
                "min_midi": 55, "max_midi": 91,
                "min_abc": "G,", "max_abc": "g'",
                "desc": "G3 to G6 (up to 5th position)"
            },
            "expert": {
                "min_midi": 55, "max_midi": 96,
                "min_abc": "G,", "max_abc": "c''",
                "desc": "G3 to C7 (virtuosic upper positions)"
            },
        },
        negative_rules=(
            "- ABSOLUTE RANGE CONSTRAINTS: Lowest string is open G3 ('G,'). Violin cannot play below G3.\n"
            "- CRITICAL PROHIBITION: NEVER use notes below 'G,' (e.g. 'F,', 'E,', 'D,', 'C,', 'B,,' DO NOT EXIST on violin!)."
        ),
        playing_character="Legato bowed phrasing, scalar runs, arpeggiated string crossings, and lyrical melodies.",
        idiomatic_technique="Ensure intervals lie comfortably across violin strings (G, D, A, E). Include rhythmic rests ('z')."
    ),
    "guitar": InstrumentRange(
        clef="treble",
        min_midi=52,  # Low E3 (E,) open 6th string (written)
        max_midi=88,  # High E6 (e') / B5 (b = 83)
        min_abc="E,",
        max_abc="b",
        min_name="Low E3 (written open 6th string)",
        max_name="High B5 (19th fret)",
        difficulty_ranges={
            "beginner": {
                "min_midi": 52, "max_midi": 72,
                "min_abc": "E,", "max_abc": "c",
                "desc": "E3 to C5 (1st position open strings and basic fretting)"
            },
            "intermediate": {
                "min_midi": 52, "max_midi": 79,
                "min_abc": "E,", "max_abc": "g",
                "desc": "E3 to G5 (up to 5th/7th fret positions)"
            },
            "advanced": {
                "min_midi": 52, "max_midi": 83,
                "min_abc": "E,", "max_abc": "b",
                "desc": "E3 to B5 (12th-19th frets)"
            },
            "expert": {
                "min_midi": 52, "max_midi": 88,
                "min_abc": "E,", "max_abc": "e'",
                "desc": "E3 to E6 (full fingerboard register)"
            },
        },
        negative_rules=(
            "- ABSOLUTE RANGE CONSTRAINTS: Lowest string in standard tuning is written Low E3 ('E,').\n"
            "- CRITICAL PROHIBITION: NEVER use notes below 'E,' (e.g. 'D,', 'C,', 'B,,' DO NOT EXIST in standard tuning!)."
        ),
        playing_character="Classical/fingerstyle guitar phrasing, scalar passages, and open string resonance intervals.",
        idiomatic_technique="Avoid unplayable wide stretches across frets. Include clean rests ('z')."
    ),
    "cello": InstrumentRange(
        clef="bass",
        min_midi=36,  # Low C2 (C,,) open C string
        max_midi=72,  # Middle C5 (c) / G4 (G = 67)
        min_abc="C,,",
        max_abc="c",
        min_name="Low C2 (open C string)",
        max_name="C5 / G4",
        difficulty_ranges={
            "beginner": {
                "min_midi": 36, "max_midi": 50,
                "min_abc": "C,,", "max_abc": "D,",
                "desc": "C2 to D3 (1st position in Bass Clef)"
            },
            "intermediate": {
                "min_midi": 36, "max_midi": 57,
                "min_abc": "C,,", "max_abc": "A,",
                "desc": "C2 to A3 (1st through 4th positions in Bass Clef)"
            },
            "advanced": {
                "min_midi": 36, "max_midi": 67,
                "min_abc": "C,,", "max_abc": "G",
                "desc": "C2 to G4 (upper neck positions in Bass Clef)"
            },
            "expert": {
                "min_midi": 36, "max_midi": 72,
                "min_abc": "C,,", "max_abc": "c",
                "desc": "C2 to C5 (thumb position and virtuosic bass clef register)"
            },
        },
        negative_rules=(
            "- ABSOLUTE RANGE CONSTRAINTS: Must use BASS CLEF ('clef=bass'). Lowest note is open C2 ('C,,').\n"
            "- CRITICAL PROHIBITION: NEVER use notes below 'C,,' (e.g. 'B,,,', 'A,,,' DO NOT EXIST on cello!).\n"
            "- CRITICAL RULE: Clef MUST be bass clef. Use 'K:C clef=bass' or 'V:1 clef=bass'."
        ),
        playing_character="Rich, sonorous low-register phrasing, expressive scalar bass lines, and arpeggiated figures.",
        idiomatic_technique="Use bass clef ('clef=bass') and ensure smooth bowed phrasing with rests ('z')."
    ),
    "piano": InstrumentRange(
        clef="treble",
        min_midi=48,  # C3 (C,)
        max_midi=84,  # C6 (c')
        min_abc="C,",
        max_abc="c'",
        min_name="C3",
        max_name="C6",
        difficulty_ranges={
            "beginner": {
                "min_midi": 60, "max_midi": 72,
                "min_abc": "C", "max_abc": "c",
                "desc": "C4 to C5 (Middle C 5-finger pattern)"
            },
            "intermediate": {
                "min_midi": 55, "max_midi": 79,
                "min_abc": "G,", "max_abc": "g",
                "desc": "G3 to G5 (balanced two-octave keyboard span)"
            },
            "advanced": {
                "min_midi": 48, "max_midi": 84,
                "min_abc": "C,", "max_abc": "c'",
                "desc": "C3 to C6 (three-octave keyboard range)"
            },
            "expert": {
                "min_midi": 45, "max_midi": 96,
                "min_abc": "A,,", "max_abc": "c''",
                "desc": "A2 to C7 (full concert grand piano span)"
            },
        },
        negative_rules="- Keep melody comfortably within the staff for clear sight-reading.",
        playing_character="Keyboard-idiomatic melodic phrasing, broken chords, scalar runs, and balanced hand positions.",
        idiomatic_technique="Rhythmic precision with clear phrase boundaries and rests ('z')."
    ),
}


def get_instrument_config(instrument_name: str) -> Optional[InstrumentRange]:
    """
    Returns the InstrumentRange configuration dataclass for the given instrument.
    """
    key = instrument_name.lower().strip()
    return INSTRUMENT_CONFIGS.get(key)


def get_instrument_profile(instrument_name: str, difficulty: str = "intermediate") -> str:
    """
    Returns the individualized pedagogical skill profile for the target instrument and difficulty level,
    including exact ABC notation pitch boundaries and negative constraints.
    """
    key = instrument_name.lower().strip()
    diff_key = difficulty.lower().strip()
    config = INSTRUMENT_CONFIGS.get(key)

    if not config:
        return (
            f"INSTRUMENT CHARACTER & SKILL PROFILE ({instrument_name.upper()}):\n"
            f"- Clef & Register: Treble clef, standard idiomatic range for {instrument_name}.\n"
            f"- Playing Character: Expressive, musically coherent phrasing with natural breathing rests ('z')."
        )

    diff_info = config.difficulty_ranges.get(diff_key, config.difficulty_ranges.get("intermediate", {}))
    diff_desc = diff_info.get("desc", f"{config.min_name} to {config.max_name}")
    diff_min_abc = diff_info.get("min_abc", config.min_abc)
    diff_max_abc = diff_info.get("max_abc", config.max_abc)

    clef_line = f"- Clef: {config.clef.title()} clef" + (" (specify 'clef=bass' in K: or V: header)" if config.clef == "bass" else "")
    register_line = (
        f"- Target Pitch Range for {difficulty.upper()} Level: {diff_min_abc} to {diff_max_abc} ({diff_desc}).\n"
        f"  (Absolute instrument physical limits: {config.min_abc} [{config.min_name}] to {config.max_abc} [{config.max_name}])."
    )

    return (
        f"INSTRUMENT CHARACTER & PEDAGOGICAL PROFILE ({instrument_name.upper()} - {difficulty.upper()} LEVEL):\n"
        f"{clef_line}\n"
        f"{register_line}\n"
        f"{config.negative_rules}\n"
        f"- Playing Character: {config.playing_character}\n"
        f"- Idiomatic Technique: {config.idiomatic_technique}"
    )

