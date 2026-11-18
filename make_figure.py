"""Rebuild the published figure from this repository's results.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
TEAL, ORANGE, NAVY, SMOKE = "#006b68", "#ab4b26", "#223c57", "#717d87"
plt.rcParams.update({"font.size":9.5, "axes.spines.top":False, "axes.spines.right":False,
                     "figure.dpi":130, "savefig.dpi":250, "font.family":"DejaVu Sans"})


def read_results():
    with (ROOT / "results.csv").open(encoding="utf8", newline="") as stream:
        return list(csv.DictReader(stream))


def save_figure(fig):
    fig.tight_layout(pad=0.7)
    fig.savefig(ROOT / "figure.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def copper():
    tab=read_results()
    subset=[r for r in tab if r['temperature_range']=='at_least_77K' and r['holdout']=='interleaved'
            and r['coordinate']=='kelvin']
    fig,ax=plt.subplots(figsize=(6.3,2.45))
    for model, label, color, marker in [("cubic_rmse","Cubic",NAVY,"o"),("spline_rmse","Linear spline",ORANGE,"s")]:
        scores=[float(r[model]) for r in subset]
        ax.plot([0,1],scores,color=color,marker=marker,label=label)
        for i,s in enumerate(scores):
            ax.annotate(f"{s:.3f}",(i,s),xytext=(8 if i==1 else -8,1),textcoords="offset points",
                        ha="left" if i==1 else "right",color=color)
    ax.set(xlim=(-.32,1.32),ylim=(.34,.465),ylabel="Test RMSE",xticks=[0,1],
           xticklabels=["Equal observation weights","Equal total weight per occupied bin"])
    ax.legend(frameon=False,fontsize=8)
    save_figure(fig)


if __name__ == "__main__":
    copper()
