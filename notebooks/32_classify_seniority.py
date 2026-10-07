"""
Track 2 — classification: advanced versus entry-level roles.

A job seeker leaving a programme needs to know which postings are
realistically open to them. The panel records a minimum experience
requirement on 1,702 postings; postings asking for two years or less are
labelled entry level, the rest advanced. The model asks whether the skills
a posting lists are enough to tell the two apart, and which skills carry
that signal.

Classes are imbalanced, 542 entry against 1,160 advanced, so the model is
fitted with balanced class weights and judged on precision and recall for
each class rather than on accuracy alone.

Input : data/processed/model_features.parquet
Output: outputs/m5_classification_log.md
        figures/fig_seniority_confusion.png
        figures/fig_seniority_coefficients.png
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             confusion_matrix, roc_auc_score,
                             classification_report)

FEATURES = Path("data/processed/model_features.parquet")
LOG = Path("outputs/m5_classification_log.md")
FIG_CM = Path("figures/fig_seniority_confusion.png")
FIG_CO = Path("figures/fig_seniority_coefficients.png")
SEED = 42
MIN_SUPPORT = 30

plt.style.use("Solarize_Light2")
BLUE, ORANGE, INK = "#268bd2", "#cb4b16", "#073642"

df = pd.read_parquet(FEATURES)
log = ["# Module 5 — classification of seniority", ""]


def note(text):
    print(text)
    log.append(text)


data = df[df["SENIORITY"].notna()].copy()
y = data["SENIORITY"].astype(int)
skill_cols = [c for c in df.columns if c.startswith("skill__")]
X = data[skill_cols]

note(f"- postings with a stated experience requirement: {len(data):,} of "
     f"{len(df):,} ({len(data)/len(df):.0%})")
note(f"- entry level (2 years or less): {(y == 0).sum():,} "
     f"({(y == 0).mean():.0%})")
note(f"- advanced (more than 2 years): {(y == 1).sum():,} "
     f"({(y == 1).mean():.0%})")
note(f"- features: {len(skill_cols)} binary skill indicators")

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, random_state=SEED, stratify=y)

model = LogisticRegressionCV(
    Cs=10, cv=5, class_weight="balanced", max_iter=3000,
    scoring="f1", random_state=SEED).fit(X_tr, y_tr)

pred = model.predict(X_te)
proba = model.predict_proba(X_te)[:, 1]

note("")
note("**Held-out performance (25 percent of postings, never seen in training)**")
note(f"- accuracy: {accuracy_score(y_te, pred):.3f}")
note(f"- ROC AUC: {roc_auc_score(y_te, proba):.3f}")
for label, name in [(0, "entry"), (1, "advanced")]:
    p, r, f, s = precision_recall_fscore_support(
        y_te, pred, labels=[label], average=None)
    note(f"- {name:<9} precision {p[0]:.3f} | recall {r[0]:.3f} | "
         f"F1 {f[0]:.3f} | n = {s[0]}")

majority = np.full(len(y_te), y_tr.mode()[0])
note("")
note("**Baseline: label every posting as the majority class**")
note(f"- accuracy: {accuracy_score(y_te, majority):.3f}")
note("- recall on the entry class: 0.000 — the baseline never identifies the "
     "postings a student can actually apply to, which is the whole point")

cm = confusion_matrix(y_te, pred)
note("")
note("Confusion matrix (rows = actual, columns = predicted):")
note(f"            predicted entry   predicted advanced")
note(f"  entry     {cm[0,0]:>13}   {cm[0,1]:>18}")
note(f"  advanced  {cm[1,0]:>13}   {cm[1,1]:>18}")
note("")
note("```")
note(classification_report(y_te, pred, target_names=["entry", "advanced"]))
note("```")

coef = pd.Series(model.coef_[0], index=X.columns)
coef.index = [c.replace("skill__", "") for c in coef.index]
support = X.sum()
support.index = coef.index
odds = np.exp(coef)
solid = odds[support >= MIN_SUPPORT]

# An odds ratio in the thousands is not a strong effect, it is separation:
# every posting listing that skill sits on one side of the split, the
# likelihood has no interior maximum, and the coefficient is held down only
# by the penalty. The share of advanced postings is reported alongside
# because it is bounded between 0 and 1 and the odds ratio is not.
adv_share = pd.Series(
    {c.replace("skill__", ""): y[X[c] == 1].mean() for c in skill_cols})
separated = solid.index[(adv_share[solid.index] >= 0.98)
                        | (adv_share[solid.index] <= 0.02)]

note("")
note(f"Odds ratios for the {len(solid)} skills appearing in at least "
     f"{MIN_SUPPORT} of these postings. Above 1 means the skill makes a "
     f"posting more likely to be advanced; below 1, more likely entry level.")

if len(separated):
    note("")
    note(f"Completely separated ({len(separated)} skills): every posting "
         f"listing these falls on one side of the split, so the odds ratio is "
         f"an artifact of that and only the direction can be read.")
    for name in separated:
        note(f"  {name:<34} ({int(support[name]):>4} postings, "
             f"{adv_share[name]:.0%} advanced)")

readable = solid.drop(index=separated)

# A coefficient is conditional on the other skills in the posting; the share
# is not. Where the two disagree the effect is a product of collinearity and
# cannot be stated to a job seeker as a property of the skill, so those are
# reported separately rather than mixed into the headline lists.
base = y.mean()
share = adv_share[readable.index]
agrees = ((readable > 1) & (share > base)) | ((readable < 1) & (share < base))
consistent, conflicting = readable[agrees], readable[~agrees]

note("")
note(f"Base rate: {base:.0%} of these postings are advanced. A skill is "
     f"reported below only when its coefficient and its raw share point the "
     f"same way; {len(conflicting)} of {len(readable)} do not and are listed "
     f"afterwards.")

note("")
note("Strongest markers of an advanced posting:")
for name, v in consistent.sort_values(ascending=False).head(12).items():
    note(f"  x{v:6.2f}   {name:<34} ({int(support[name]):>4} postings, "
         f"{adv_share[name]:.0%} advanced)")
note("")
note("Strongest markers of an entry-level posting:")
for name, v in consistent.sort_values().head(12).items():
    note(f"  x{v:6.2f}   {name:<34} ({int(support[name]):>4} postings, "
         f"{adv_share[name]:.0%} advanced)")

note("")
note("Coefficient and raw share disagree — conditional effects only, not "
     "reported as findings:")
for name, v in conflicting.reindex(
        (conflicting - 1).abs().sort_values(ascending=False).index).head(10).items():
    note(f"  x{v:6.2f}   {name:<34} ({int(support[name]):>4} postings, "
         f"{adv_share[name]:.0%} advanced)")

fig, ax = plt.subplots(figsize=(5.5, 4.6))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks([0, 1], ["entry", "advanced"])
ax.set_yticks([0, 1], ["entry", "advanced"])
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                fontsize=15, fontweight="bold",
                color="white" if cm[i, j] > cm.max() / 2 else INK)
ax.set_title("Seniority Classifier: Confusion Matrix",
             fontsize=12, fontweight="bold", color=INK, pad=12)
fig.tight_layout()
fig.savefig(FIG_CM, dpi=150)
plt.close(fig)

top = pd.concat([consistent.sort_values(ascending=False).head(12),
                 consistent.sort_values().head(12)]).sort_values()
fig, ax = plt.subplots(figsize=(8.5, 8))
ax.barh(top.index, top.values - 1,
        color=[ORANGE if v < 1 else BLUE for v in top.values])
ax.axvline(0, color=INK, linewidth=1)
ax.set_title("Which Skills Mark a Posting as Advanced or Entry Level",
             fontsize=13, fontweight="bold", color=INK, pad=12)
ax.set_xlabel("Odds ratio minus one: above zero = advanced, below = entry level")
fig.tight_layout()
fig.savefig(FIG_CO, dpi=150)
plt.close(fig)

LOG.write_text("\n".join(log) + "\n")
print(f"\nwritten {LOG}, {FIG_CM}, {FIG_CO}")
