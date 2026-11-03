#!/usr/bin/env python3
"""Part C: best-fit parameter table (Markdown + LaTeX) from results/fit_results.txt."""
from pathlib import Path
import numpy as np
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u

Z = 0.049
COSMO = FlatLambdaCDM(H0=70, Om0=0.27)     # same as XSPEC 'cosmo 70 0 0.73'
KEV_HZ = 2.417989e17                         # 1 keV in Hz
RES = Path("results")
DL = COSMO.luminosity_distance(Z).to(u.cm).value

d = {}
for line in open(RES / "fit_results.txt"):
    t = line.split()
    if len(t) < 2:
        continue
    v = []
    for x in t[1:]:
        try:
            v.append(float(x))
        except ValueError:
            v.append(x)
    d[t[0]] = v

NONE = ("–", "--")


def fmt(v, lo=None, hi=None, nd=3):
    """Value with asymmetric 90% errors (lo/hi are absolute confidence bounds)."""
    if v is None:
        return NONE
    if lo is None or hi is None or (lo == 0 and hi == 0):
        return f"{v:.{nd}f}", f"${v:.{nd}f}$"
    up, dn = hi - v, v - lo
    return (f"{v:.{nd}f} (+{up:.{nd}f}/−{dn:.{nd}f})",
            f"${v:.{nd}f}^{{+{up:.{nd}f}}}_{{-{dn:.{nd}f}}}$")


def par(tag, name, scale=1.0, nd=3):
    k = f"{tag}_{name}"
    if k not in d:
        return NONE
    v, lo, hi = (d[k] + [0, 0])[:3]
    return fmt(v * scale, lo * scale, hi * scale, nd)


def lgpar(key, scale=1.0, nd=3):
    if key not in d:
        return NONE
    v, lo, hi = d[key][:3]
    if lo == 0 and hi == 0:
        return fmt(10**v * scale, nd=nd)
    return fmt(10**v * scale, 10**lo * scale, 10**hi * scale, nd)


def chi(tag):
    k = f"{tag}_chi2"
    if k not in d:
        return NONE, NONE
    c, dof = d[k][:2]
    return (f"{c:.1f}/{int(dof)}", f"${c:.1f}/{int(dof)}$"), (f"{c/dof:.2f}", f"${c/dof:.2f}$")


def fnu(tag, kind):
    k = f"{tag}_{kind}_1keV"
    if k not in d:
        return NONE
    F = d[k][0] / 0.02                                   # erg cm^-2 s^-1 keV^-1
    return fmt(F / KEV_HZ / 1e-29, nd=2)                 # micro-Jansky


def lum_est(tag, band):
    """Rest-frame luminosity from observed-band unabsorbed flux, K-corrected."""
    k, g = f"{tag}_Funabs_{band}", f"{tag}_Gamma"
    if k not in d or g not in d:
        return None
    return 4 * np.pi * DL**2 * d[k][0] * (1 + Z)**(d[g][0] - 2)


def lum(tag, band):
    L = lum_est(tag, band)
    return NONE if L is None else fmt(L / 1e44, nd=2)


def unabs_m2(band):
    return lgpar(f"m2_cflux_{band}", 1e11) if f"m2_cflux_{band}" in d else par("m2", f"Funabs_{band}", 1e11)


def lum_m2(band):
    return lgpar(f"m2_clumin_{band}", 1e-44, 2) if f"m2_clumin_{band}" in d else lum("m2", band)


c1, r1 = chi("m1")
c2, r2 = chi("m2")
U_F = ("10^-11 erg cm^-2 s^-1", r"$10^{-11}$ erg cm$^{-2}$ s$^{-1}$")
rows = [
    ("N_H", r"$N_{\rm H}$", "10^22 cm^-2", r"$10^{22}$ cm$^{-2}$", par("m1", "nH"), par("m2", "nH")),
    ("Photon index Γ", r"$\Gamma$", "–", "--", par("m1", "Gamma"), par("m2", "Gamma")),
    ("PL norm (1 keV)", r"PL norm (1 keV)", "10^-2 ph keV^-1 cm^-2 s^-1",
     r"$10^{-2}$ ph keV$^{-1}$ cm$^{-2}$ s$^{-1}$", par("m1", "norm", 100), par("m2", "norm", 100)),
    ("Fe Kα energy (rest)", r"Fe K$\alpha$ $E$ (rest)", "keV", "keV", NONE, par("m2", "LineE")),
    ("Fe Kα σ", r"Fe K$\alpha$ $\sigma$", "keV", "keV", NONE, par("m2", "Sigma")),
    ("Fe Kα norm", r"Fe K$\alpha$ norm", "10^-5 ph cm^-2 s^-1", r"$10^{-5}$ ph cm$^{-2}$ s$^{-1}$",
     NONE, par("m2", "LineNorm", 1e5, 2)),
    ("Fe Kα EW (obs.)", r"Fe K$\alpha$ EW (obs.)", "eV", "eV", NONE, par("m2", "EW", 1e3, 0)),
    ("χ²/dof", r"$\chi^2$/dof", "–", "--", c1, c2),
    ("Reduced χ²", r"$\chi^2_\nu$", "–", "--", r1, r2),
    ("F_obs (0.3–10 keV)", r"$F_{\rm obs}$ (0.3--10 keV)", *U_F, par("m1", "Fobs_0.3-10", 1e11), par("m2", "Fobs_0.3-10", 1e11)),
    ("F_obs (2–10 keV)", r"$F_{\rm obs}$ (2--10 keV)", *U_F, par("m1", "Fobs_2-10", 1e11), par("m2", "Fobs_2-10", 1e11)),
    ("F_obs (0.5–2 keV)", r"$F_{\rm obs}$ (0.5--2 keV)", *U_F, par("m1", "Fobs_0.5-2", 1e11), par("m2", "Fobs_0.5-2", 1e11)),
    ("F_unabs (0.3–10 keV)", r"$F_{\rm unabs}$ (0.3--10 keV)", *U_F, par("m1", "Funabs_0.3-10", 1e11), unabs_m2("0.3-10")),
    ("F_unabs (2–10 keV)", r"$F_{\rm unabs}$ (2--10 keV)", *U_F, par("m1", "Funabs_2-10", 1e11), unabs_m2("2-10")),
    ("L (2–10 keV, rest)", r"$L$ (2--10 keV, rest)", "10^44 erg s^-1", r"$10^{44}$ erg s$^{-1}$", lum("m1", "2-10"), lum_m2("2-10")),
    ("L (0.3–10 keV, rest)", r"$L$ (0.3--10 keV, rest)", "10^44 erg s^-1", r"$10^{44}$ erg s$^{-1}$", lum("m1", "0.3-10"), lum_m2("0.3-10")),
    ("F_ν (1 keV, observed)", r"$F_\nu$ (1 keV, observed)", "μJy", r"$\mu$Jy", fnu("m1", "Fobs"), fnu("m2", "Fobs")),
    ("F_ν (1 keV, unabsorbed)", r"$F_\nu$ (1 keV, unabsorbed)", "μJy", r"$\mu$Jy", fnu("m1", "Funabs"), fnu("m2", "Funabs")),
]

H1, H2 = "Absorbed power law", "Absorbed power law + Fe Kα"
md = [f"| Quantity | Unit | {H1} | {H2} |", "|---|---|---|---|"]
md += [f"| {qm} | {um} | {a[0]} | {b[0]} |" for qm, qt, um, ut, a, b in rows]
(RES / "best_fit_table.md").write_text("\n".join(md) + "\n")

tex = [r"\begin{table}", r"\centering",
       r"\caption{Best-fitting EPIC-pn spectral parameters of 3C\,111 (0.3--10 keV, $z=0.049$). "
       r"Errors are 90 per cent confidence ($\Delta\chi^2=2.706$).}",
       r"\begin{tabular}{llcc}", r"\hline",
       r"Quantity & Unit & Absorbed power law & Absorbed power law + Fe K$\alpha$ \\", r"\hline"]
tex += [f"{qt} & {ut} & {a[1]} & {b[1]} \\\\" for qm, qt, um, ut, a, b in rows]
tex += [r"\hline", r"\end{tabular}", r"\end{table}"]
(RES / "best_fit_table.tex").write_text("\n".join(tex) + "\n")

print("\n".join(md))
print(f"\nD_L = {DL/3.0857e24:.1f} Mpc")
print("\nwrote results/best_fit_table.md and results/best_fit_table.tex")
