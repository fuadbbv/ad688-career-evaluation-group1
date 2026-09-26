import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PANEL = "data/processed/career_market_panel.csv"
FIGDIR = "figures"
NUMBERS = "outputs/m2_baseline_numbers.md"

plt.style.use("Solarize_Light2")


BLUE = "#268bd2"
ORANGE = "#cb4b16"
AQUA = "#2aa198"
GREEN = "#859900"
MAGENTA = "#d33682"
YELLOW = "#b58900"
VIOLET = "#6c71c4"
RED = "#dc322f"
MUTED = "#93a1a1"
SURFACE = "#fdf6e3"
INK = "#073642"
INK_SOFT = "#586e75"


SOLARIZED_CYCLE = [BLUE, ORANGE, AQUA, GREEN, MAGENTA, YELLOW, VIOLET, RED]

plt.rcParams.update({
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK_SOFT,
    "xtick.color": INK_SOFT,
    "ytick.color": INK_SOFT,
})

df = pd.read_csv(PANEL, low_memory=False)
lines = ["# Market baseline - key numbers", "", f"Panel: {len(df)} postings", ""]


def note(text):
    print(text)
    lines.append(text)


def frame(ax, title, xlabel):
    # CHANGE: title is now bold and centered (was left-aligned, regular weight).
    ax.set_title(title, fontsize=12, color=INK, pad=12,
                 loc="center", fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK_SOFT)
    ax.grid(axis="x", color=MUTED, alpha=0.4, linewidth=0.8)
    ax.set_axisbelow(True)


def hbar(series, title, xlabel, filename, color=None, colors=None):
    series = series.iloc[::-1]

    if colors is None:
        colors = color if color is not None else BLUE
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(series) + 1.8))
    bars = ax.barh(series.index.astype(str), series.values,
                   color=colors, height=0.62)
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
hbar(soc, "Postings by Occupation (SOC)", "Postings", "fig_volume_by_soc.png",
     color=BLUE)
note(f"- Top occupation: **{soc.index[0]}** with {soc.iloc[0]:,} postings "
     f"({soc.iloc[0] / len(df):.0%} of the panel)")
note(f"- Top three occupations: " + "; ".join(f"{k} {v:,}" for k, v in soc.head(3).items()))

# 2. Volume by title

titles = df["normalized_title"].dropna().value_counts().head(12)
hbar(titles, "Most Common Job Titles", "Postings", "fig_volume_by_title.png",
     color=ORANGE)
note(f"- Most common title: **{titles.index[0]}** ({titles.iloc[0]:,} postings)")
note(f"- Distinct titles in the panel: {df['normalized_title'].nunique():,}")

# 2b.Top 3 job titles as a share of all postings

top3_titles = df["normalized_title"].dropna().value_counts().head(3)
top3_share_of_total = top3_titles.sum() / len(df)

pie_labels = list(top3_titles.index)
pie_values = list(top3_titles.values)
pie_colors = [SOLARIZED_CYCLE[i % len(SOLARIZED_CYCLE)] for i in range(3)]

fig, ax = plt.subplots(figsize=(7, 7))
wedges, _, autotexts = ax.pie(
    pie_values,
    labels=pie_labels,
    colors=pie_colors,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.75,
    textprops={"color": INK_SOFT, "fontsize": 10},
)
for autotext in autotexts:
    autotext.set_color(SURFACE)
    autotext.set_fontweight("bold")

ax.axis("equal")
fig.suptitle("Top 3 Job Titles by Share of Postings", fontsize=12, color=INK,
             fontweight="bold", y=0.98)
fig.text(0.5, 0.925,
         f"These 3 titles make up {top3_share_of_total:.0%} of all {len(df):,} postings",
         ha="center", fontsize=9.5, color=INK_SOFT)
fig.subplots_adjust(top=0.85)

fig.savefig(f"{FIGDIR}/fig_top3_titles_share.png", dpi=160)
plt.close(fig)
note(f"- Top 3 titles combined: {top3_titles.sum():,} postings "
     f"({top3_share_of_total:.0%} of the panel)")
note("- Top 3 title shares (relative to each other): " +
     "; ".join(f"{k} {v/top3_titles.sum():.1%}" for k, v in top3_titles.items()))

# 3. Salary distribution

sal = df[["annual_salary_min", "annual_salary_max"]].mean(axis=1).dropna()
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.hist(sal, bins=30, color=AQUA, edgecolor=SURFACE, linewidth=1.2)
frame(ax, f"Annual Salary Midpoint ({len(sal):,} Postings That Disclose Pay)",
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
hbar(states, "Top States by Posting Volume", "Postings", "fig_top_states.png",
     color=GREEN)
note(f"- Postings with a US state code: {df['state_code'].notna().sum():,} "
     f"({df['state_code'].notna().mean():.0%})")
note(f"- Leading states: " + "; ".join(f"{k} {v:,}" for k, v in states.head(5).items()))

# 5. Top cities

cities = df["city"].dropna().value_counts().head(10)
hbar(cities, "Top Hiring Cities", "Postings", "fig_top_cities.png",
     color=MAGENTA)
note(f"- Leading cities: " + "; ".join(f"{k} {v:,}" for k, v in cities.head(5).items()))

# 6. Experience requirements

exp = df["experience_years_raw"].dropna()
bins = [0, 1, 2, 3, 4, 5, 7, 10, 100]
labels = ["<1", "1", "2", "3", "4", "5-6", "7-9", "10+"]
buckets = pd.cut(exp, bins=bins, labels=labels, right=False).value_counts().reindex(labels)
fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.bar(buckets.index.astype(str), buckets.values, color=YELLOW, width=0.62)
for bar, value in zip(bars, buckets.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
            f"{int(value):,}", ha="center", fontsize=9, color=INK_SOFT)
frame(ax, f"Years of Experience Requested ({len(exp):,} Postings)", "Years")
ax.set_ylabel("Postings", color=INK_SOFT)
ax.grid(axis="x", visible=False)
ax.grid(axis="y", color=MUTED, alpha=0.4, linewidth=0.8)
fig.tight_layout()
fig.savefig(f"{FIGDIR}/fig_experience.png", dpi=160)
plt.close(fig)
note(f"- Experience signal found on {len(exp):,} postings ({len(exp)/len(df):.0%}); "
     f"median {exp.median():.0f} years")
note("- Experience buckets: " + "; ".join(f"{k} {int(v):,}" for k, v in buckets.items()))

# 7. Remote status

remote = df["remote_status"].value_counts()
order = [c for c in ["remote", "hybrid", "onsite", "unknown"] if c in remote.index]
remote = remote.reindex(order)
remote_colors = [MUTED if c == "unknown" else VIOLET for c in remote.index][::-1]
hbar(remote, "Remote, Hybrid, Onsite or Unrecorded", "Postings",
     "fig_remote.png", colors=remote_colors)
known = remote.drop("unknown", errors="ignore")
note(f"- Remote status recorded on {known.sum():,} of {len(df):,} postings "
     f"({known.sum()/len(df):.0%})")
note("- Among labelled postings: " +
     "; ".join(f"{k} {v/known.sum():.0%}" for k, v in known.items()))

# 8. Top employers

emp = df["company_name"].dropna().value_counts().head(10)
hbar(emp, "Top Employers by Posting Volume", "Postings", "fig_top_employers.png",
     color=RED)
note(f"- Distinct employers: {df['company_name'].nunique():,}")
note(f"- Largest employer: **{emp.index[0]}** with {emp.iloc[0]:,} postings "
     f"({emp.iloc[0]/len(df):.1%} of the panel)")
note(f"- Top 10 employers account for {emp.sum()/len(df):.0%} of all postings")

with open(NUMBERS, "w") as handle:
    handle.write("\n".join(lines) + "\n")
print(f"\nfigures written to {FIGDIR}/, numbers to {NUMBERS}")