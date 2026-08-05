import re
from typing import Tuple


def beautify_abc_line(line: str, note_length: str = "1/8") -> str:
    """
    Post-processing algorithm to beautify musical note display according to default note length (L):
    1. Makes quarter notes the basic beat unit separated by spaces.
    2. Strips redundant '1' duration markers (e.g., 'd1' -> 'd', 'e1' -> 'e', 'z1' -> 'z').
    3. Beams adjacent notes that form a single beat together so they read like published sheet music:
       - For L:1/8 (2 units/beat): beams single eighth note pairs (e.g., '| f2 e2 d1 e1 d2 |' -> '| f2 e2 de d2 |').
       - For L:1/16 (4 units/beat): beams eighth note pairs ('G2 B2' -> 'G2B2'), dotted eighth + sixteenth ('b3 a' -> 'b3a'),
         sixteenth + dotted eighth ('a b3' -> 'ab3'), and sixteenth groups by beat.
    """
    if line.startswith("V:") or line.startswith("P:") or line.startswith("%"):
        return line
    # 1. Ensure spaces between adjacent tokens so durations can be cleanly analyzed
    line = re.sub(r"([A-Ga-gz][0-9>/\.\-]*)(?=[A-Ga-gz^=_])", r"\1 ", line)
    # 2. Strip redundant '1' durations when not followed by another digit or slash
    line = re.sub(r"([A-Ga-gz^=_][,\']*)1(?![0-9/])", r"\1", line)

    if note_length == "1/16":
        # Under L:1/16, 4 duration units = 1 beat (quarter note is 4, eighth note is 2, sixteenth is 1)
        # Beams pitches that form a 1-beat group while leaving standalone rests un-beamed
        pair_2_2 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*2)\s+([A-Ga-g^=_][,\']*2)(?!\S*[0-9>/.-])"
        )
        pair_3_1 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*3)\s+([A-Ga-g^=_][,\']*)(?!\S*[0-9>/.-])"
        )
        pair_1_3 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*3)(?!\S*[0-9>/.-])"
        )
        pair_1_1_1_1 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)(?!\S*[0-9>/.-])"
        )
        pair_1_1_2 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*2)(?!\S*[0-9>/.-])"
        )
        pair_2_1_1 = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*2)\s+([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)(?!\S*[0-9>/.-])"
        )

        for pattern in [pair_2_2, pair_3_1, pair_1_3, pair_1_1_1_1, pair_1_1_2, pair_2_1_1]:
            while True:
                new_line = pattern.sub(lambda m: "".join(m.groups()), line)
                if new_line == line:
                    break
                line = new_line
    else:
        # Default L:1/8 (2 duration units = 1 beat)
        # Group adjacent single eighth notes within a beat so they beam beautifully together
        pair_pattern = re.compile(
            r"(?:^|(?<=[\s|\[]))([A-Ga-g^=_][,\']*)\s+([A-Ga-g^=_][,\']*)(?!\S*[0-9>/.-])"
        )
        while True:
            new_line = pair_pattern.sub(r"\1\2", line)
            if new_line == line:
                break
            line = new_line

    return re.sub(r"\s+", " ", line).strip()


def clean_and_validate_abc(
    raw_abc: str,
    default_title: str = "Sight-Reading Exercise",
    default_key: str = "C",
    default_meter: str = "4/4",
    default_tempo: int = 110,
    expected_bars: int = 4
) -> Tuple[bool, str, str]:
    """
    Cleans raw LLM response output, validates structural ABC Notation headers,
    enforces requested measure count, removes unnecessary ornamentation (trills/grace notes),
    beautifies note beaming and duration display according to L, and filters out commentary.

    Args:
        raw_abc: The raw string returned by the generative AI model.
        default_title: Fallback title if T: header is omitted.
        default_key: Fallback key signature if K: header is omitted.
        default_meter: Fallback time signature if M: header is omitted.
        default_tempo: Fallback tempo if Q: header is omitted.
        expected_bars: Number of measures required in the exercise.

    Returns:
        Tuple[bool, str, str]: (is_valid, cleaned_abc_string, error_message_if_any)
    """
    if not raw_abc or not raw_abc.strip():
        return False, "", "Empty response received from music generation engine."

    # 1. Strip markdown fenced code blocks if present (e.g., ```abc ... ``` or ``` ...)
    text = raw_abc.strip()
    markdown_pattern = re.compile(r"^```(?:abc|ABC)?\s*(.*?)\s*```$", re.DOTALL)
    match = markdown_pattern.match(text)
    if match:
        text = match.group(1).strip()

    # Also strip stray opening/closing markdown ticks if not matched by whole block
    lines = [line.strip() for line in text.splitlines() if not line.strip().startswith("```")]

    # 2. Extract canonical metadata headers (X, T, M, L, Q, K, C) vs body/melody lines (including V:1 voices)
    headers = {}
    body_lines = []
    header_regex = re.compile(r"^([A-Za-z]):\s*(.*)$")
    metadata_keys = {"X", "T", "M", "L", "Q", "K", "C"}
    seen_key_signature = False

    for line in lines:
        if not line:
            continue
        header_match = header_regex.match(line)
        key_char = header_match.group(1).upper() if header_match else ""

        # Treat only canonical metadata headers before K: as header dictionary entries.
        # Any voice lines (V:), lyrics (w:), or anything after K: is part of the musical body!
        if not seen_key_signature and header_match and len(key_char) == 1 and key_char in metadata_keys:
            headers[key_char] = header_match.group(2)
            if key_char == "K":
                seen_key_signature = True
        else:
            body_lines.append(line)

    # 3. Filter out non-musical conversational English text lines from body_lines
    musical_body_lines = []
    for line in body_lines:
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith("V:") or line_str.startswith("P:") or line_str.startswith("%"):
            musical_body_lines.append(line_str)
        elif "|" in line_str or (re.search(r"^[A-Ga-gz0-9\s|:\[\]()^=_/.\'-]+$", line_str) and len(line_str) > 2):
            musical_body_lines.append(line_str)

    body_lines = musical_body_lines

    # 4. Strip trills and ornamentation (TR skill is not necessary for sight-reading practice)
    # Strip ~ (ABC trill symbol), !trill!, "tr", and grace notes { ... }
    cleaned_body = []
    for line in body_lines:
        line = re.sub(r"~|!trill!|\"tr\"|\bT(?=[A-Ga-g])", "", line)
        line = re.sub(r"\{[^}]*\}", "", line)
        cleaned_body.append(line)
    body_lines = cleaned_body

    # 5. Ensure mandatory ABC headers are present and properly ordered
    x_val = headers.get("X", "1")
    t_val = headers.get("T", default_title)
    m_val = headers.get("M", default_meter)
    l_val = headers.get("L", "1/8")
    q_val = headers.get("Q", f"1/4={default_tempo}")
    k_val = headers.get("K", default_key)

    # 6. Beautify notes post-processing algorithm according to default note length (L):
    # Makes quarter notes the basic beat unit separated by spaces, strips redundant '1' durations,
    # and beams adjacent notes together by beat (e.g. '| f2 e2 d1 e1 d2 |' -> '| f2 e2 de d2 |' for L:1/8,
    # or '| G2 B2 d2 g2 b3 a g2 e2 |' -> '| G2B2 d2g2 b3a g2e2 |' for L:1/16)
    body_lines = [beautify_abc_line(line, note_length=l_val) for line in body_lines]

    # Validate that body_lines actually contains musical note/rest content
    has_musical_content = any(re.search(r"[A-Ga-gz|0-9]", line) for line in body_lines if not line.startswith("V:"))
    if not body_lines or not has_musical_content:
        return False, "", (
            "ABC notation is missing musical measure content. "
            "The AI generated only headers without notes."
        )

    # Validate measure/bar count: ensure at least `expected_bars` bar lines ('|' or '|]') exist
    total_bars_found = sum(line.count('|') for line in body_lines if not line.strip().startswith('%'))
    if expected_bars > 0 and total_bars_found < expected_bars:
        return False, "", (
            f"ABC notation has only {total_bars_found} measure(s), but {expected_bars} measures were required."
        )

    # 7. Construct canonical, validated ABC Notation string
    canonical_headers = [
        f"X:{x_val}",
        f"T:{t_val}",
        f"M:{m_val}",
        f"L:{l_val}",
        f"Q:{q_val}",
        f"K:{k_val}"
    ]

    clean_abc = "\n".join(canonical_headers + body_lines)
    return True, clean_abc, ""
