#!/usr/bin/env python3
"""
Part C: publication-quality figures (PDF + PNG) for the 3C 111 EPIC-pn spectral analysis.

Inputs
  results/qdp_fig0[1-5]_*.qdp      XSPEC 'wdata' dumps written by 02_fit_spectrum.xcm
  figures/raw/fig06_epatplot.pdf   epatplot output (pattern fractions are read from its vector paths)
Outputs
  figures/fig01 ... fig06 (.pdf and .png), results/epatplot_fractions.csv

Style: Computer Modern fonts, large labels, inward ticks on all four sides,
light dotted grid, thick model lines, units in square brackets, no titles.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FixedLocator, MultipleLocator

RES, FIG = Path("results"), Path("figures")
FIG.mkdir(exist_ok=True)
Z = 0.049
E_FE_OBS = 6.4 / (1 + Z)                     # Fe K-alpha, 6.4 keV rest -> 6.10 keV observed

# ---------------- house style ----------------
RED, ORANGE, GREEN, BLUE = "#B22222", "#FF8C00", "#2E8B57", "#4169E1"
DATA = "#2B2B2B"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10", "Computer Modern Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm", "axes.formatter.use_mathtext": True,
    "font.size": 17, "axes.labelsize": 20, "xtick.labelsize": 17, "ytick.labelsize": 17,
    "legend.fontsize": 15, "legend.frameon": False, "legend.handlelength": 1.8,
    "axes.linewidth": 1.2, "axes.unicode_minus": False,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.major.size": 7, "ytick.major.size": 7, "xtick.minor.size": 3.5, "ytick.minor.size": 3.5,
    "xtick.major.width": 1.1, "ytick.major.width": 1.1, "xtick.minor.width": 0.8, "ytick.minor.width": 0.8,
    "xtick.major.pad": 7, "ytick.major.pad": 6,
    "axes.grid": True, "grid.color": "0.75", "grid.linestyle": ":", "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "lines.linewidth": 2.6, "errorbar.capsize": 0,
    "savefig.bbox": "tight", "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42})

E_LABEL = r"Energy [keV]"
COUNTS = r"Counts [s$^{-1}$ keV$^{-1}$]"


# ---------------- helpers ----------------
def read_qdp(path):
    """List of arrays, one per plot panel (panels separated by 'NO' lines)."""
    blocks, cur = [], []
    for line in open(path):
        s = line.strip()
        if not s or s[0] in "!@" or s.upper().startswith(("READ", "SKIP")):
            continue
        if s.upper().startswith("NO"):
            if cur:
                blocks.append(cur); cur = []
            continue
        row = []
        for t in s.split():
            try:
                row.append(float(t))
            except ValueError:
                row.append(np.nan)
        cur.append(row)
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        n = min(len(r) for r in b)
        out.append(np.array([r[:n] for r in b]))
    return out


def energy_axis(ax, emin=0.3, emax=10.5, label=True):
    ax.set_xscale("log")
    ax.set_xlim(emin, emax)
    ticks = [t for t in (0.3, 0.5, 1, 2, 5, 10) if emin <= t <= emax]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.set_xticklabels([f"{t:g}" for t in ticks])
    ax.xaxis.set_minor_formatter(NullFormatter())
    if label:
        ax.set_xlabel(E_LABEL)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)
    print("wrote", FIG / f"{name}.pdf")


def data_points(ax, d, label="EPIC-pn data", color=DATA):
    ax.errorbar(d[:, 0], d[:, 2], xerr=d[:, 1], yerr=d[:, 3], fmt="none",
                ecolor=color, elinewidth=0.9, label=label, zorder=2)


def model_line(ax, d, label, color=RED):
    if d.shape[1] > 4 and np.isfinite(d[:, 4]).any():
        ax.plot(d[:, 0], d[:, 4], color=color, drawstyle="steps-mid", label=label, zorder=3)


def residual_panel(ax, r):
    ax.errorbar(r[:, 0], r[:, 2], xerr=r[:, 1], yerr=r[:, 3], fmt="none",
                ecolor=BLUE, elinewidth=0.9, zorder=2)
    ax.axhline(0, color="black", lw=1.4, zorder=3)
    ax.set_ylim(-6, 6)
    ax.yaxis.set_major_locator(FixedLocator([-4, 0, 4]))
    ax.set_ylabel(r"$\chi$")


# ---------------- Fig. 1: spectrum ----------------
def fig_spectrum():
    d = read_qdp(RES / "qdp_fig01_spectrum.qdp")[0]
    fig, ax = plt.subplots(figsize=(7.5, 5.4))
    data_points(ax, d)
    ax.set_yscale("log")
    energy_axis(ax)
    ax.set_ylabel(COUNTS)
    ax.set_ylim(0.05, 6)
    save(fig, "fig01_spectrum")


# ---------------- Figs. 2 and 4: fit + residuals ----------------
def fig_fit(qdp, model_label, name, mark_fe=False):
    d, r = read_qdp(RES / qdp)[:2]
    fig, (a1, a2) = plt.subplots(2, 1, sharex=True, figsize=(7.5, 6.8),
                                 gridspec_kw=dict(height_ratios=[3, 1.15], hspace=0))
    data_points(a1, d)
    model_line(a1, d, model_label)
    a1.set_yscale("log")
    a1.set_ylim(0.05, 6)
    a1.set_ylabel(COUNTS)
    a1.legend(loc="lower left")
    residual_panel(a2, r)
    if mark_fe:
        for a in (a1, a2):
            a.axvline(E_FE_OBS, ls="--", color=GREEN, lw=1.6, zorder=1)
    energy_axis(a2)
    fig.align_ylabels((a1, a2))
    save(fig, name)


# ---------------- Fig. 3: ratio ----------------
def fig_ratio():
    r = read_qdp(RES / "qdp_fig03_ratio_m1.qdp")[0]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.errorbar(r[:, 0], r[:, 2], xerr=r[:, 1], yerr=r[:, 3], fmt="none",
                ecolor=DATA, elinewidth=0.9, zorder=2)
    ax.axhline(1, color=RED, zorder=3)
    ax.axvline(E_FE_OBS, ls="--", color=GREEN, lw=1.8, zorder=1,
               label=r"Fe K$\alpha$, 6.4 keV (rest frame)")
    energy_axis(ax)
    ax.set_ylim(0.7, 1.42)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))
    ax.set_ylabel(r"Data / Model")
    ax.legend(loc="upper left", bbox_to_anchor=(0.15, 0.99))
    save(fig, "fig03_ratio_absorbed_powerlaw")


# ---------------- Fig. 5: unfolded spectrum ----------------
def fig_unfolded():
    d = read_qdp(RES / "qdp_fig05_unfolded_m2.qdp")[0]
    sel = d[:, 0] >= 0.6
    d = d[sel]
    fig, ax = plt.subplots(figsize=(7.5, 5.4))
    data_points(ax, d)
    model_line(ax, d, r"Absorbed power law + Fe K$\alpha$")
    ax.set_yscale("log")
    ax.set_ylim(0.5 * np.nanmin(d[:, 2]), 2.0 * np.nanmax(d[:, 2]))
    energy_axis(ax, emin=0.6)
    ax.set_ylabel(r"$E^{2}F(E)$ [keV$^{2}$ ph cm$^{-2}$ s$^{-1}$ keV$^{-1}$]")
    ax.legend(loc="lower right")
    save(fig, "fig05_unfolded_spectrum")


# ---------------- Fig. 6: pattern fractions (from epatplot) ----------------
def read_epatplot(pdf=FIG / "raw" / "fig06_epatplot.pdf"):
    """Recover observed and model single/double fractions from page 2 of the epatplot PDF.

    The axes are calibrated from the major tick marks (x: 10^2, 10^3, 10^4 eV; y: 0.0 ... 1.0).
    Colours used by epatplot: singles = purple, doubles = blue.
    """
    import pymupdf
    page = pymupdf.open(pdf)[1]
    draws = page.get_drawings()
    black = [g for g in draws if g.get("color") == (0.0, 0.0, 0.0) and g["type"] == "fs"]
    xt = sorted({round(g["rect"].x0, 3) for g in black
                 if abs(g["rect"].height - 3.5) < 0.05 and g["rect"].width < 0.01})
    yt = sorted({round(g["rect"].y0, 3) for g in black
                 if abs(g["rect"].width - 3.5) < 0.05 and g["rect"].height < 0.01}, reverse=True)
    x0, x1 = xt[0], xt[1]                          # 10^2 and 10^3 eV
    y0, y1 = yt[0], yt[-1]                         # 0.0 and 1.0

    def to_data(path):
        pts = []
        for it in path["items"]:
            if it[0] == "l":
                pts += [it[1], it[2]]
        xy = np.array([[10 ** (2 + (p.x - x0) / (x1 - x0)) / 1e3, (p.y - y0) / (y1 - y0)] for p in pts])
        keep = [0] + [k for k in range(1, len(xy)) if not np.allclose(xy[k], xy[k - 1])]
        return xy[keep]

    def colour(g, rgb):
        return g["type"] == "s" and g.get("color") is not None and \
            np.allclose(g["color"], rgb, atol=0.01)

    purple, blue = (0.478, 0.408, 0.651), (0.204, 0.541, 0.741)
    paths = {"s": [to_data(g) for g in draws if colour(g, purple)],
             "d": [to_data(g) for g in draws if colour(g, blue)]}
    out = {}
    for k, lst in paths.items():
        obs = max(lst, key=len)                    # histogram has the most vertices
        mod = min(lst, key=len)                    # smooth model curve
        lo, hi, v = [], [], []
        for i in range(len(obs) - 1):
            if abs(obs[i, 1] - obs[i + 1, 1]) < 1e-9 and obs[i + 1, 0] > obs[i, 0]:
                lo.append(obs[i, 0]); hi.append(obs[i + 1, 0]); v.append(obs[i, 1])
        out[k] = dict(lo=np.array(lo), hi=np.array(hi), obs=np.array(v), model=mod)
    return out


def fig_pattern():
    try:
        p = read_epatplot()
    except Exception as err:                      # pymupdf missing or file absent
        print("SKIPPED fig06:", err)
        return
    s, d = p["s"], p["d"]
    lo, hi = s["lo"], s["hi"]
    ok = lo >= 0.33                                # first bins (< 0.34 keV) are noise-dominated
    lo, hi = lo[ok], hi[ok]
    so, do = s["obs"][ok], d["obs"][ok]
    ec = np.sqrt(lo * hi)

    def interp(m, x):
        return np.interp(np.log(x), np.log(m[:, 0]), m[:, 1])

    # the clean event list keeps only PATTERN<=4, so compare with the model renormalised to s+d
    egrid = np.logspace(np.log10(0.25), np.log10(15), 400)
    ms, md = interp(s["model"], egrid), interp(d["model"], egrid)
    msn, mdn = ms / (ms + md), md / (ms + md)
    ms_c, md_c = interp(s["model"], ec), interp(d["model"], ec)
    rs, rd = so / (ms_c / (ms_c + md_c)), do / (md_c / (ms_c + md_c))

    band = (ec >= 0.5) & (ec <= 2.0)
    w = (hi - lo)[band]
    print("0.5-2 keV observed/model (renormalised): singles %.3f, doubles %.3f"
          % (np.sum(so[band] * w) / np.sum((so[band] / rs[band]) * w),
             np.sum(do[band] * w) / np.sum((do[band] / rd[band]) * w)))
    np.savetxt(RES / "epatplot_fractions.csv",
               np.column_stack([lo, hi, so, do, ms_c / (ms_c + md_c), md_c / (ms_c + md_c)]),
               delimiter=",", fmt="%.6g",
               header="E_lo_keV,E_hi_keV,single_obs,double_obs,single_model,double_model")

    fig, (a1, a2) = plt.subplots(2, 1, sharex=True, figsize=(7.5, 6.8),
                                 gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0))
    for a in (a1, a2):
        a.axvspan(0.5, 2.0, color="0.92", zorder=0)
    edges = np.append(lo, hi[-1])
    a1.stairs(so, edges, color=RED, lw=1.1, alpha=0.9, baseline=None, label="Singles (observed)")
    a1.stairs(do, edges, color=BLUE, lw=1.1, alpha=0.9, baseline=None, label="Doubles (observed)")
    a1.plot(egrid, msn, color="black", lw=2.2, label="Expected (no pile-up)")
    a1.plot(egrid, mdn, color="black", lw=2.2)
    a1.set_ylim(0, 1)
    a1.yaxis.set_major_locator(MultipleLocator(0.2))
    a1.set_ylabel(r"Pattern fraction")
    a1.legend(loc="center left", bbox_to_anchor=(0.01, 0.49), fontsize=14)

    a2.plot(ec, rs, ".", color=RED, ms=3.5)
    a2.plot(ec, rd, ".", color=BLUE, ms=3.5)
    a2.axhline(1, color="black", lw=1.4)
    a2.set_ylim(0.8, 1.2)
    a2.yaxis.set_major_locator(FixedLocator([0.9, 1.0, 1.1]))
    a2.set_ylabel(r"Obs. / Exp.")
    energy_axis(a2, emin=0.3, emax=15)
    a2.xaxis.set_major_locator(FixedLocator([0.3, 0.5, 1, 2, 5, 10]))
    a2.set_xticklabels(["0.3", "0.5", "1", "2", "5", "10"])
    fig.align_ylabels((a1, a2))
    save(fig, "fig06_pattern_fractions")


for job in (fig_spectrum,
            lambda: fig_fit("qdp_fig02_fit_m1.qdp", "Absorbed power law",
                            "fig02_fit_absorbed_powerlaw", mark_fe=True),
            fig_ratio,
            lambda: fig_fit("qdp_fig04_fit_m2.qdp", r"Absorbed power law + Fe K$\alpha$",
                            "fig04_fit_powerlaw_FeKa"),
            fig_unfolded,
            fig_pattern):
    try:
        job()
    except (FileNotFoundError, IndexError) as err:
        print("SKIPPED:", err)
