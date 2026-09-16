"""Step 3.3 - Market baseline figures.

Chart selection for remote status, top employers and top cities follows
Katie Bowles' draft (notebooks/market_baseline.py). Added here: volume by
occupation and title, salary distribution, experience requirements, and top
states; every figure is written to figures/ as PNG instead of shown on screen.
Remote status is drawn as bars rather than a pie so the four categories,
including "unknown", can be compared directly.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PANEL = "data/processed/career_market_panel.csv"
FIGDIR = "figures"
NUMBERS = "outputs/m2_baseline_numbers.md"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
MUTED = "#b5b4ad"
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK_SOFT,
    "xtick.color": INK_SOFT, "ytick.color": INK_SOFT,
})

df = pd.read_csv(PANEL, low_memory=False)
lines = ["# Market baseline - key numbers", "", f"Panel: {len(df)} postings", ""]


def note(text):
    print(text)
    lines.append(text)


def frame(ax, title, xlabel):
    ax.set_title(title, fontsize=12, color=INK, pad=12, loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d8d7d0")
    ax.grid(axis="x", color="#e8e7e0", linewidth=0.8)
    ax.set_axisbelow(True)


def hbar(series, title, xlabel, filename, colors=None):
    series = series.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(series) + 1.8))
    bars = ax.barh(series.index.astype(str), series.values,
                   color=colors if colors is not None else BLUE, height=0.62)
    for bar, value in zip(bars, series.values):
        ax.text(bar.get_width() + max(series.values) * 0.012,
                bar.get_y() + bar.get_height() / 2, f"{int(value):,}",
                va="center", fontsize=9, color=INK_SOFT)
    ax.set_xlim(0, max(series.values) * 1.12)
    frame(ax, title, xlabel)
    fig.tight_layout()
    fig.savefig(f"{FIGDIR}/{filename}", dpi=160)
    plt.close(fig)


# 1. Volume by occupation (SOC)
soc = df["soc_name"].dropna().value_counts().head(10)
hbar(soc, "Postings by occupation (SOC)", "Postings", "fig_volume_by_soc.png")
note(f"- Top occupation: **{soc.index[0]}** with {soc.iloc[0]:,} postings "
     f"({soc.iloc[0] / len(df):.0%} of the panel)")
note(f"- Top three occupations: " + "; ".join(f"{k} {v:,}" for k, v in soc.head(3).items()))

# 2. Volume by title
titles = df["normalized_title"].dropna().value_counts().head(12)
hbar(titles, "Most common job titles", "Postings", "fig_volume_by_title.png")
note(f"- Most common title: **{titles.index[0]}** ({titles.iloc[0]:,} postings)")
note(f"- Distinct titles in the panel: {df['normalized_title'].nunique():,}")

# 3. Salary distribution
sal = df[["annual_salary_min", "annual_salary_max"]].mean(axis=1).dropna()
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.hist(sal, bins=30, color=BLUE, edgecolor=SURFACE, linewidth=1.2)
frame(ax, f"Annual salary midpoint ({len(sal):,} postings that disclose pay)",
      "Annual salary, USD")
ax.set_ylabel("Postings", color=INK_SOFT)
ax.xaxis.set_major_formatter(lambda x, _: f"${x/1000:.0f}k")
fig.tight_layout()
fig.savefig(f"{FIGDIR}/fig_salary_distribution.png", dpi=160)
plt.close(fig)
note(f"- Salary disclosed on {len(sal):,} of {len(df):,} postings ({len(sal)/len(df):.0%})")
note(f"- Median midpoint **${sal.median():,.0f}**, quartiles "
     f"${sal.quantile(.25):,.0f} - ${sal.quantile(.75):,.0f}")

# 4. Top states
states = df["state_code"].dropna().value_counts().head(10)
hbar(states, "Top states by posting volume", "Postings", "fig_top_states.png")
note(f"- Postings with a US state code: {df['state_code'].notna().sum():,} "
     f"({df['state_code'].notna().mean():.0%})")
note(f"- Leading states: " + "; ".join(f"{k} {v:,}" for k, v in states.head(5).items()))

# 5. Top cities (Katie's chart)
cities = df["city"].dropna().value_counts().head(10)
hbar(cities, "Top hiring cities", "Postings", "fig_top_cities.png")
note(f"- Leading cities: " + "; ".join(f"{k} {v:,}" for k, v in cities.head(5).items()))

# 6. Experience requirements
exp = df["experience_years_raw"].dropna()
bins = [0, 1, 2, 3, 4, 5, 7, 10, 100]
labels = ["<1", "1", "2", "3", "4", "5-6", "7-9", "10+"]
buckets = pd.cut(exp, bins=bins, labels=labels, right=False).value_counts().reindex(labels)
fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.bar(buckets.index.astype(str), buckets.values, color=BLUE, width=0.62)
for bar, value in zip(bars, buckets.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
            f"{int(value):,}", ha="center", fontsize=9, color=INK_SOFT)
frame(ax, f"Years of experience requested ({len(exp):,} postings)", "Years")
ax.set_ylabel("Postings", color=INK_SOFT)
ax.grid(axis="x", visible=False)
ax.grid(axis="y", color="#e8e7e0", linewidth=0.8)
fig.tight_layout()
fig.savefig(f"{FIGDIR}/fig_experience.png", dpi=160)
plt.close(fig)
note(f"- Experience signal found on {len(exp):,} postings ({len(exp)/len(df):.0%}); "
     f"median {exp.median():.0f} years")
note("- Experience buckets: " + "; ".join(f"{k} {int(v):,}" for k, v in buckets.items()))

# 7. Remote status (Katie's chart, as bars)
remote = df["remote_status"].value_counts()
order = [c for c in ["remote", "hybrid", "onsite", "unknown"] if c in remote.index]
remote = remote.reindex(order)
colors = [MUTED if c == "unknown" else BLUE for c in remote.index][::-1]
hbar(remote, "Remote, hybrid, onsite or unrecorded", "Postings",
     "fig_remote.png", colors=colors)
known = remote.drop("unknown", errors="ignore")
note(f"- Remote status recorded on {known.sum():,} of {len(df):,} postings "
     f"({known.sum()/len(df):.0%})")
note("- Among labelled postings: " +
     "; ".join(f"{k} {v/known.sum():.0%}" for k, v in known.items()))

# 8. Top employers (Katie's chart)
emp = df["company_name"].dropna().value_counts().head(10)
hbar(emp, "Top employers by posting volume", "Postings", "fig_top_employers.png")
note(f"- Distinct employers: {df['company_name'].nunique():,}")
note(f"- Largest employer: **{emp.index[0]}** with {emp.iloc[0]:,} postings "
     f"({emp.iloc[0]/len(df):.1%} of the panel)")
note(f"- Top 10 employers account for {emp.sum()/len(df):.0%} of all postings")

with open(NUMBERS, "w") as handle:
    handle.write("\n".join(lines) + "\n")
print(f"\nfigures written to {FIGDIR}/, numbers to {NUMBERS}")
