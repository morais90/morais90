#!/usr/bin/env python3

import json
import random
import re
import sys
from pathlib import Path
from typing import TypedDict

MAX_LINE_LENGTH = 80
SVG_WIDTH = 700
SVG_LINE_HEIGHT = 20
SVG_PADDING = 20
SVG_QUOTE_FONT_SIZE = 16
SVG_AUTHOR_FONT_SIZE = 14
QUOTE_MARKER_START = "<!-- QUOTE:START -->"
QUOTE_MARKER_END = "<!-- QUOTE:END -->"


class Quote(TypedDict):
    quote: str
    author: str


def get_base_path() -> Path:
    """
    Get the base directory path for the script.

    Returns
    -------
    Path
        Resolved absolute path to the script directory.
    """
    return Path(__file__).parent.resolve()


def load_quotes() -> list[Quote]:
    """
    Load programming quotes from JSON file.

    Returns
    -------
    list[Quote]
        List of quote dictionaries containing 'quote' and 'author' keys.
    """
    quotes_file = get_base_path() / "quotes.json"
    try:
        with open(quotes_file, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading quotes: {e}")
        sys.exit(1)


def wrap_text(text: str, max_length: int) -> list[str]:
    """
    Wrap text into lines based on maximum character length.

    Parameters
    ----------
    text : str
        The text to wrap.
    max_length : int
        Maximum characters per line.

    Returns
    -------
    list[str]
        List of wrapped text lines.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word) + (1 if current_line else 0)
        if current_length + word_length <= max_length:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def generate_quote_svg(quote_text: str, author: str) -> str:
    """
    Generate an SVG image with a formatted quote.

    Parameters
    ----------
    quote_text : str
        The quote text to display.
    author : str
        The author of the quote.

    Returns
    -------
    str
        SVG markup as a string.
    """
    lines = wrap_text(quote_text, MAX_LINE_LENGTH)
    height = len(lines) * SVG_LINE_HEIGHT + 60 + SVG_PADDING * 2

    svg_parts = [
        f'<svg width="{SVG_WIDTH}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        f'  <rect width="{SVG_WIDTH}" height="{height}" fill="none"/>',
        "  <g>",
    ]

    y_offset = SVG_PADDING + 25
    for line in lines:
        svg_parts.append(
            f'    <text x="50%" y="{y_offset}" '
            f'font-family="\'Segoe UI\', \'Helvetica\', \'Arial\', sans-serif" '
            f'font-size="{SVG_QUOTE_FONT_SIZE}" fill="#586069" '
            f'text-anchor="middle" font-style="italic">"{line}"</text>'
        )
        y_offset += SVG_LINE_HEIGHT

    svg_parts.append(
        f'    <text x="50%" y="{y_offset + 20}" '
        f'font-family="\'Segoe UI\', \'Helvetica\', \'Arial\', sans-serif" '
        f'font-size="{SVG_AUTHOR_FONT_SIZE}" fill="#6a737d" '
        f'text-anchor="middle">— {author}</text>'
    )
    svg_parts.extend(["  </g>", "</svg>"])

    return "\n".join(svg_parts)


def update_readme(quote_data: Quote) -> None:
    """
    Update README.md with a new quote.

    Parameters
    ----------
    quote_data : Quote
        Dictionary containing 'quote' and 'author' keys.
    """
    base_path = get_base_path()
    readme_file = base_path / "README.md"
    svg_file = base_path / "quote.svg"

    try:
        content = readme_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: {readme_file} not found.")
        sys.exit(1)

    if QUOTE_MARKER_START not in content:
        print(f"Error: Quote markers not found in README. Please add {QUOTE_MARKER_START} and {QUOTE_MARKER_END} markers.")
        sys.exit(1)

    svg = generate_quote_svg(quote_data["quote"], quote_data["author"])
    svg_file.write_text(svg, encoding="utf-8")

    pattern = rf"{QUOTE_MARKER_START}.*?{QUOTE_MARKER_END}"
    replacement = f'{QUOTE_MARKER_START}\n<img src="./quote.svg" alt="Quote" />\n{QUOTE_MARKER_END}'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    readme_file.write_text(new_content, encoding="utf-8")

    print(f'✅ Updated quote: "{quote_data["quote"]}" - {quote_data["author"]}')


def main() -> None:
    """
    Main entry point for updating the daily quote.
    """
    quotes = load_quotes()
    random_quote = random.choice(quotes)
    update_readme(random_quote)


if __name__ == "__main__":
    main()
