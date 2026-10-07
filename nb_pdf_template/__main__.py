"""Export the Chinese template directly from this Git checkout."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import nbformat
from nbconvert import LatexExporter


def main():
    parser = argparse.ArgumentParser(description="Export a Chinese notebook with latex_authentic.")
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--to", choices=("pdf", "latex"), default="pdf")
    parser.add_argument("--layout", choices=("left", "above"), default="left")
    parser.add_argument("--fontset", choices=("fandol", "auto"))
    parser.add_argument("--hide-prompts", action="store_true")
    args = parser.parse_args()
    for name in ["pandoc"] + (["xelatex"] if args.to == "pdf" else []):
        if not shutil.which(name):
            parser.error(f"Missing {name} on PATH; see README.md.")
    notebook = args.notebook.resolve()
    nb = nbformat.read(notebook, as_version=4)
    settings = dict(nb.metadata.get("latex_authentic_zh", {}))
    if args.fontset:
        settings["fontset"] = args.fontset
    if settings.get("fontset", "fandol") not in ("fandol", "auto"):
        parser.error("fontset must be fandol or auto.")
    nb.metadata["latex_authentic_zh"] = settings
    suffix = ".pdf" if args.to == "pdf" else ".tex"
    output = (args.output or notebook.with_name(notebook.stem + "_authentic_zh" + suffix)).resolve()
    if output == notebook:
        parser.error("The output path must differ from the notebook.")
    output.parent.mkdir(parents=True, exist_ok=True)
    templates = Path(__file__).resolve().parents[1] / "share" / "templates"
    exporter = LatexExporter(
        template_name="latex_authentic_zh",
        template_file="m.tex.j2" if args.layout == "above" else "index.tex.j2",
        extra_template_basedirs=[str(templates)] if templates.is_dir() else [],
        extra_template_paths=[str(templates)] if templates.is_dir() else [],
        exclude_input_prompt=args.hide_prompts,
        exclude_output_prompt=args.hide_prompts,
    )
    print("Rendering LaTeX...", flush=True)
    latex, resources = exporter.from_notebook_node(nb, resources={
        "metadata": {"name": notebook.stem, "path": str(notebook.parent)},
        "output_files_dir": output.stem + "_files",
    })

    def write_files(directory, tex_name):
        (directory / tex_name).write_text(latex, encoding="utf-8")
        for name, data in resources.get("outputs", {}).items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    if args.to == "latex":
        write_files(output.parent, output.name)
    else:
        with tempfile.TemporaryDirectory(prefix=".nb-pdf-", dir=output.parent) as temporary:
            build = Path(temporary)
            write_files(build, "report.tex")
            env = dict(os.environ)
            env["TEXINPUTS"] = str(notebook.parent) + os.pathsep + env.get("TEXINPUTS", "") + os.pathsep
            for number in range(1, 4):
                print(f"XeLaTeX {number}/3...", flush=True)
                result = subprocess.run([shutil.which("xelatex"), "-interaction=nonstopmode",
                                         "-halt-on-error", "report.tex"],
                                        cwd=build, env=env, capture_output=True)
                if result.returncode:
                    print((result.stdout + result.stderr).decode("utf-8", errors="replace")[-8000:])
                    return result.returncode
                if number == 3:
                    for line in result.stdout.decode("utf-8", errors="replace").splitlines():
                        if "Missing character:" in line:
                            print(line)
            output.write_bytes((build / "report.pdf").read_bytes())
    print(output, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
