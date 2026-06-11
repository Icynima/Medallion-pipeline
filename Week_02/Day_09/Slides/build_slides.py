r"""Build the Day 9 theory deck — 100+ slides, all text authored, all images
embedded as matplotlib charts or python-pptx shapes.

Run:
    .\.venv\Scripts\python.exe build_slides.py

Output:
    Day_09_Slides_v2.pptx (alongside this file)
"""
from __future__ import annotations
from pathlib import Path

import theme as T
import chart_helpers as ch
import slide_helpers as sh
import content_intro
import content_screenshots
import content_monitoring
import content_logging
import content_quality
import content_scaling
import content_lab


HERE = Path(__file__).parent
OUTPUT_PPTX = HERE / "Day_09_Slides_v2.pptx"


def build() -> int:
    print("[1/3] generating chart PNGs…")
    images = ch.generate_all()

    print("[2/3] composing slides…")
    prs = sh.new_presentation()

    sections = [
        ("intro", content_intro, T.ACCENT_TEAL),
        ("screens", content_screenshots, T.ACCENT_BLUE),
        ("monitoring", content_monitoring, T.ACCENT_TEAL),
        ("logging", content_logging, T.ACCENT_YELLOW),
        ("quality", content_quality, T.ACCENT_GREEN),
        ("scaling", content_scaling, T.ACCENT_BLUE),
        ("lab", content_lab, T.ACCENT_PURPLE),
    ]

    # First pass: collect total slide count from each module
    slide_specs = []
    for name, module, accent in sections:
        specs = module.specs(images, accent)
        slide_specs.extend(specs)
    total = len(slide_specs)
    print(f"      total slides: {total}")

    # Second pass: actually render
    for page, spec in enumerate(slide_specs, start=1):
        kind = spec["kind"]
        args = {k: v for k, v in spec.items() if k != "kind"}
        if kind == "title":
            sh.title_slide(prs, **args)
        elif kind == "divider":
            sh.section_divider(prs, **args)
        else:
            args["page"] = page
            args["total"] = total
            if kind == "content":
                sh.content_slide(prs, **args)
            elif kind == "table":
                sh.table_slide(prs, **args)
            elif kind == "chart":
                sh.chart_slide(prs, **args)
            elif kind == "code":
                sh.code_slide(prs, **args)
            elif kind == "quiz":
                sh.quiz_slide(prs, **args)
            elif kind == "answer":
                sh.answer_slide(prs, **args)
            elif kind == "lab":
                sh.lab_callout_slide(prs, **args)
            else:
                raise ValueError(f"unknown slide kind: {kind}")

    print(f"[3/3] writing {OUTPUT_PPTX.name}…")
    prs.save(OUTPUT_PPTX)
    print(f"      done · {total} slides · "
          f"{OUTPUT_PPTX.stat().st_size / 1024:.0f} KB")
    return total


if __name__ == "__main__":
    build()
