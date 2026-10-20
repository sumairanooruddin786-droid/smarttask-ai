import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(12.3, 3.4), dpi=200)
ax.set_xlim(0, 12.3); ax.set_ylim(0, 3.4); ax.axis("off")

boxes = [
    ("User Input", "Natural-language\ntask message", "#e0e7ff", "#3730a3"),
    ("Node 1", "Task Extraction\n(Gemini)", "#dbeafe", "#1d4ed8"),
    ("Node 2", "Prioritization\nHigh / Medium / Low\n(Gemini)", "#fef3c7", "#b45309"),
    ("Node 3", "Format Results\n(Python)", "#dcfce7", "#15803d"),
    ("END", "Organized\nto-do list", "#f3e8ff", "#7e22ce"),
]
w, h, gap = 1.95, 1.9, 0.5
x = 0.25
centers = []
for title, body, fill, edge in boxes:
    ax.add_patch(FancyBboxPatch((x, 0.75), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fill, ec=edge, lw=2))
    ax.text(x + w/2, 0.75 + h - 0.35, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color=edge)
    ax.text(x + w/2, 0.75 + h/2 - 0.2, body, ha="center", va="center", fontsize=9.5, color="#1f2937")
    centers.append(x)
    x += w + gap

for i in range(len(boxes) - 1):
    x0 = centers[i] + w; x1 = centers[i+1]
    ax.add_patch(FancyArrowPatch((x0 + 0.03, 1.7), (x1 - 0.03, 1.7),
                                 arrowstyle="-|>", mutation_scale=18, lw=2, color="#475569"))
ax.text(6.1, 0.3, "Shared LangGraph state: user_input  ->  extracted  ->  prioritized  ->  output",
        ha="center", fontsize=9.5, color="#475569", style="italic")
plt.savefig("docs/workflow.png", bbox_inches="tight", facecolor="white")
