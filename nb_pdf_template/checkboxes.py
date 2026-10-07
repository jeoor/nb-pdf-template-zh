"""Render checkbox markers in Pandoc prose without changing notebook sources."""

import json
import re

from nbconvert.preprocessors import Preprocessor


MARKER = re.compile(r"(?<!\w)(?:- *)?\[([xX ])\]")
PROTECTED = {"Code", "CodeBlock", "Math", "RawInline", "RawBlock", "Link", "Image"}
VERBATIM = re.compile(
    r"(\\begin\{(?:verbatim|Verbatim|Highlighting)\}.*?"
    r"\\end\{(?:verbatim|Verbatim|Highlighting)\})", re.DOTALL)


def render_checkboxes(source):
    """Replace prose markers in Pandoc JSON, including markers split by spaces."""
    document = json.loads(source)

    def render_run(nodes):
        text = "".join(node["c"] if node["t"] == "Str" else " " for node in nodes)
        if not MARKER.search(text):
            return nodes
        text = MARKER.sub(lambda match: "☐" if match[1] == " " else "☑", text)
        return [{"t": "Space"} if part == " " else {"t": "Str", "c": part}
                for part in re.split("( )", text) if part]

    def walk(node):
        if isinstance(node, dict):
            if node.get("t") in PROTECTED:
                return node
            if "c" in node:
                node["c"] = walk(node["c"])
        elif isinstance(node, list):
            result, run = [], []
            for item in node:
                if isinstance(item, dict) and item.get("t") in {"Str", "Space"}:
                    run.append(item)
                else:
                    result.extend(render_run(run))
                    run = []
                    result.append(walk(item))
            result.extend(render_run(run))
            return result
        return node

    document["blocks"] = walk(document["blocks"])
    return json.dumps(document, ensure_ascii=False)


def render_task_checkmarks(latex):
    """Use a checkmark for Pandoc's checked task-list labels."""
    parts = VERBATIM.split(latex)
    for index in range(0, len(parts), 2):
        parts[index] = parts[index].replace(r"\item[$\boxtimes$]", r"\item[☑]")
    return "".join(parts)


class CheckboxPreprocessor(Preprocessor):
    def preprocess(self, nb, resources):
        resources["latex_authentic_zh"] = {
            "render_checkboxes": render_checkboxes,
            "render_task_checkmarks": render_task_checkmarks,
        }
        return nb, resources
