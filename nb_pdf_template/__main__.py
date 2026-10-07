"""Export the Chinese template directly from this Git checkout."""

import argparse
from pathlib import Path

import nbformat
from nbconvert import LatexExporter, PDFExporter
from nbconvert.writers import FilesWriter


def main():
    parser = argparse.ArgumentParser(description="Export a Chinese notebook with latex_authentic.")
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--to", choices=("pdf", "latex"), default="pdf")
    parser.add_argument("--layout", choices=("left", "above"), default="left")
    parser.add_argument("--fontset", choices=("fandol", "auto"))
    parser.add_argument("--hide-prompts", action="store_true")
    args = parser.parse_args()
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
    templates = Path(__file__).resolve().parents[1] / "share" / "templates"
    template_paths = [str(templates)] if templates.is_dir() else []
    exporter_type = PDFExporter if args.to == "pdf" else LatexExporter
    exporter = exporter_type(
        template_name="latex_authentic_zh",
        template_file="m.tex.j2" if args.layout == "above" else "index.tex.j2",
        extra_template_basedirs=template_paths,
        extra_template_paths=template_paths,
        exclude_input_prompt=args.hide_prompts,
        exclude_output_prompt=args.hide_prompts,
    )
    print("Exporting...", flush=True)
    body, resources = exporter.from_notebook_node(nb, resources={
        "metadata": {"name": notebook.stem, "path": str(notebook.parent)},
        "output_files_dir": output.stem + "_files",
    })

    resources["output_extension"] = output.suffix
    FilesWriter(build_directory=str(output.parent)).write(body, resources, notebook_name=output.stem)
    print(output, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
