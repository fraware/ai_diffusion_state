"""Conceptual diffusion-state architecture diagram (main-text Figure 1)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from diffusion_state.utils import PROJECT_ROOT

OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

LAYERS = [
    "Frontier AI capability",
    "National designation\n(AI pilot zones)",
    "Municipal implementation capacity",
    "Industrial ecosystems",
    "Administrative recognition\n(MIIT smart-factory lists)",
    "Sectoral & export-relevant adoption",
]


def build_diffusion_architecture_figure() -> Path:
    fig, ax = plt.subplots(figsize=(6.5, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(LAYERS) + 1)
    ax.axis("off")

    box_w, box_h = 7.5, 0.85
    x0 = 1.25
    colors = ["#2c3e50", "#34495e", "#4a6fa5", "#5d8aa8", "#6b8e9f", "#7a9e7e"]

    for i, (label, color) in enumerate(zip(LAYERS, colors)):
        y = len(LAYERS) - i
        box = FancyBboxPatch(
            (x0, y - box_h / 2),
            box_w,
            box_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2,
            edgecolor=color,
            facecolor=color,
            alpha=0.92,
        )
        ax.add_patch(box)
        ax.text(
            x0 + box_w / 2,
            y,
            label,
            ha="center",
            va="center",
            fontsize=11,
            color="white",
            fontweight="bold" if i == 0 else "normal",
        )
        if i < len(LAYERS) - 1:
            ax.annotate(
                "",
                xy=(x0 + box_w / 2, y - box_h / 2 - 0.12),
                xytext=(x0 + box_w / 2, y - box_h / 2 - 0.55),
                arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.8),
            )

    ax.text(
        5,
        len(LAYERS) + 0.55,
        "Diffusion capacity: embedding AI into production",
        ha="center",
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()

    out = OUTPUT_FIGURES / "fig_diffusion_state_architecture.png"
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(build_diffusion_architecture_figure())
