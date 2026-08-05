"""
Individualized Instrument Skills & Character Profiles for the Google ADK Sight-Reading Composer Agent.
Each instrument has tailored pedagogical rules specifying range, clef, phrasing, and playing character.
"""
from typing import Dict

INSTRUMENT_SKILLS: Dict[str, str] = {
    "saxophone": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (SAXOPHONE):\n"
        "- Clef & Register: Treble clef, written range Bb3 to F6 (avoid extreme altissimo for intermediate sight-reading).\n"
        "- Playing Character: Lyrical jazz/classical woodwind phrasing, smooth scalar motion, arpeggiated figures, and syncopated rhythms.\n"
        "- Idiomatic Technique: Include natural breathing rests ('z' or 'z2') suitable for woodwind breath control. Avoid awkward wide interval leaps."
    ),
    "violin": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (VIOLIN):\n"
        "- Clef & Register: Treble clef, range G3 to E6 (idiomatic violin strings: G, D, A, E).\n"
        "- Playing Character: Legato bowed phrasing, scalar runs, arpeggiated string crossings, and lyrical melodies.\n"
        "- Idiomatic Technique: Ensure intervals lie comfortably across violin strings. Include rhythmic rests ('z')."
    ),
    "flute": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (FLUTE):\n"
        "- Clef & Register: Treble clef, range C4 to G6 (light, agile middle/upper woodwind register).\n"
        "- Playing Character: Bright, agile melodic phrasing, step-wise runs, and classical broken chords.\n"
        "- Idiomatic Technique: Include frequent breathing rests ('z' or 'z2') for natural woodwind breath control."
    ),
    "piano": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (PIANO):\n"
        "- Clef & Register: Treble clef (or Grand staff for expert), register C3 to C6.\n"
        "- Playing Character: Keyboard-idiomatic melodic phrasing, broken chords, scalar runs, and balanced hand positions.\n"
        "- Idiomatic Technique: Rhythmic precision with clear phrase boundaries and rests ('z')."
    ),
    "guitar": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (GUITAR):\n"
        "- Clef & Register: Treble clef (written an octave higher than sounding), range E3 to B5.\n"
        "- Playing Character: Classical/fingerstyle guitar phrasing, scalar passages, and open string resonance intervals.\n"
        "- Idiomatic Technique: Avoid unplayable wide stretches across frets. Include clean rests ('z')."
    ),
    "cello": (
        "INSTRUMENT CHARACTER & SKILL PROFILE (CELLO):\n"
        "- Clef & Register: Bass clef, register C2 to G4 (idiomatic cello strings: C, G, D, A).\n"
        "- Playing Character: Rich, sonorous low-register phrasing, expressive scalar bass lines, and arpeggiated figures.\n"
        "- Idiomatic Technique: Use bass clef ('clef=bass') and ensure smooth bowed phrasing with rests ('z')."
    ),
}


def get_instrument_profile(instrument_name: str) -> str:
    """
    Returns the individualized pedagogical skill profile for the target instrument.
    """
    key = instrument_name.lower().strip()
    return INSTRUMENT_SKILLS.get(
        key,
        (
            f"INSTRUMENT CHARACTER & SKILL PROFILE ({instrument_name.upper()}):\n"
            "- Clef & Register: Idiomatic register and clef for the instrument.\n"
            "- Playing Character: Expressive, musically coherent phrasing with natural breathing rests ('z')."
        ),
    )
