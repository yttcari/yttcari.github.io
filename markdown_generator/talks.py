#!/usr/bin/env python
# coding: utf-8

# Talks markdown generator for academicpages
#
# Takes a TSV or CSV of talks with metadata and converts them for use with
# the academicpages GitHub Pages template.
# Usage: python3 talks.py talks.tsv
#        python3 talks.py talks.csv
#        python3 talks.py talks.tsv _talks/
#
# Uses the Python standard library (csv) so it has no external dependencies.

import csv
import os
import re
import sys
from datetime import datetime

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    if isinstance(text, str):
        return "".join(html_escape_table.get(c, c) for c in text)
    else:
        return ""


def yaml_quote(text):
    """Double-quoted YAML string, safe for quotes and backslashes."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def valid_date(text):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return False
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def main(input_file, output_dir=None):
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "_talks")

    os.makedirs(output_dir, exist_ok=True)

    ext = os.path.splitext(input_file)[1].lower()
    delimiter = "\t" if ext in (".tsv", ".txt") else ","

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for line_no, row in enumerate(reader, start=2):
            # short rows give None, extra columns land under the None key
            if row.get(None):
                print("Skipping line %d: more columns than the header (%d extra). "
                      "Check for stray tabs/commas." % (line_no, len(row[None])), file=sys.stderr)
                continue

            def field(name):
                return (row.get(name) or "").strip()

            title = field("title")
            url_slug = field("url_slug")
            date = field("date")
            talk_type = field("type")
            venue = field("venue")
            location = field("location")
            talk_url = field("talk_url")
            description = field("description")

            if not title or not url_slug or not date:
                print("Skipping line %d: missing required field (title, url_slug, or date)" % line_no, file=sys.stderr)
                continue

            if not valid_date(date):
                print("Skipping line %d: date %r is not YYYY-MM-DD. "
                      "Columns are probably misaligned (expected order: %s)."
                      % (line_no, date, ", ".join(reader.fieldnames)), file=sys.stderr)
                continue

            if talk_url and not re.match(r"https?://", talk_url):
                print("Skipping line %d: talk_url %r does not start with http(s)://. "
                      "Columns are probably misaligned." % (line_no, talk_url), file=sys.stderr)
                continue

            if not re.fullmatch(r"[A-Za-z0-9_-]+", url_slug):
                print("Skipping line %d: url_slug %r may only contain letters, digits, '-' and '_'."
                      % (line_no, url_slug), file=sys.stderr)
                continue

            md_filename = date + "-" + url_slug + ".md"
            md_path = os.path.join(output_dir, md_filename)

            md = "---\n"
            md += "title: " + yaml_quote(title) + "\n"
            md += "collection: talks\n"
            md += "type: " + yaml_quote(talk_type if len(talk_type) > 3 else "Talk") + "\n"
            md += "permalink: /talks/" + date + "-" + url_slug + "\n"
            if venue:
                md += "venue: " + yaml_quote(venue) + "\n"
            md += "date: " + date + "\n"
            if location:
                md += "location: " + yaml_quote(location) + "\n"
            if talk_url:
                md += "link: " + yaml_quote(talk_url) + "\n"
            md += "---\n"

            if description:
                md += "\n" + html_escape(description) + "\n"

            with open(md_path, "w", encoding="utf-8") as out:
                out.write(md)
            print("Created: " + md_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 talks.py <input_file> [output_dir]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    main(input_file, output_dir)
