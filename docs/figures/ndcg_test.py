"""График для README: NDCG@10 на тесте по всем пользователям.

Числа берутся из сохранённого вывода ячейки 28 тетрадки final_project_two_stage.ipynb (таблица метрик на тесте).
Запуск из корня репозитория:  python docs/figures/ndcg_test.py
"""
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "final_project_two_stage.ipynb"
OUT = Path(__file__).with_name("ndcg_test.png")

LABELS = {
    "Итоговая система": "Итоговая система\n(кандидаты + CatBoostRanker)",
    "Mult-VAE": "Mult-VAE",
    "Эвристика (SegmentPopular)": "Сегментная популярность",
    "iALS": "iALS",
}


def ndcg_from_notebook() -> dict[str, float]:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for out in nb["cells"][28]["outputs"]:
        text = "".join(out.get("text", "")) + "".join(out.get("data", {}).get("text/plain", ""))
        if "NDCG@10" not in text:
            continue
        # первый блок таблицы: MAP@10 (активные, все, холодные), NDCG@10 (активные, все)
        first_block = text.split("\n\n")[0]
        values = {}
        for name in LABELS:
            m = re.search(re.escape(name) + r"\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", first_block)
            values[name] = float(m.group(5))
        return values
    raise RuntimeError("таблица метрик не найдена в выводе ячейки 28")


def main() -> None:
    values = ndcg_from_notebook()
    names = list(LABELS)[::-1]
    scores = [values[n] for n in names]
    colors = ["#94a3b8"] * (len(names) - 1) + ["#2563eb"]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    bars = ax.barh([LABELS[n] for n in names], scores, color=colors, height=0.6)
    for bar, s in zip(bars, scores):
        ax.text(s + 0.002, bar.get_y() + bar.get_height() / 2, f"{s:.3f}".replace(".", ","), va="center", fontsize=11)
    gain = values["Итоговая система"] / values["Mult-VAE"] - 1
    fig.suptitle(f"NDCG@10 на тесте: +{gain:.0%} к лучшей одиночной модели".replace("%", " %"),
                 fontsize=13, x=0.02, ha="left")
    ax.set_xlim(0, max(scores) * 1.18)
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.05))
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.2f}".replace(".", ","))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=11)
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT, facecolor="white")
    print(f"{OUT}: {values}")


if __name__ == "__main__":
    main()
