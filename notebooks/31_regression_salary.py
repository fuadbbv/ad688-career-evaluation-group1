"""
Track 1 — regression: how skill requirements relate to compensation.

Target is the natural log of the annual salary midpoint. Pay is strongly
right-skewed, so a model on the raw figure would be dominated by a handful
of very large ranges; the log also lets each coefficient be read as an
approximate percentage effect on pay, which is what a job seeker wants.

Two specifications are fitted so the skill effect can be separated from
geography: skills alone, then skills plus state and work arrangement. The
difference between their R-squared says how much of the explainable
variation is really about skills rather than about where the job is.

Input : data/processed/model_features.parquet
Output: outputs/m5_regression_log.md, figures/fig_salary_coefficients.png
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

FEATURES = Path("data/processed/model_features.parquet")
LOG = Path("outputs/m5_regression_log.md")
FIG = Path("figures/fig_salary_coefficients.png")
SEED = 42

plt.style.use("Solarize_Light2")
BLUE, ORANGE, INK = "#268bd2", "#cb4b16", "#073642"

df = pd.read_parquet(FEATURES)
log = ["# Module 5 — regression on compensation", ""]


def note(text):
    print(text)
    log.append(text)


data = df[df["SALARY"].notna()].copy()
note(f"- postings with an annual salary midpoint: {len(data):,} of {len(df):,} "
     f"({len(data)/len(df):.0%})")
note(f"- salary range ${data['SALARY'].min():,.0f} to "
     f"${data['SALARY'].max():,.0f}, median ${data['SALARY'].median():,.0f}")

skill_cols = [c for c in df.columns if c.startswith("skill__")]
y = np.log(data["SALARY"])

# Specification A: skills only
X_a = data[skill_cols]

# Specification B: skills plus geography and work arrangement as controls
top_states = data["STATE"].value_counts().head(10).index
controls = pd.get_dummies(
    pd.DataFrame({
        "state": data["STATE"].where(data["STATE"].isin(top_states), "other"),
        "remote": data["REMOTE"].fillna("unrecorded"),
    }), drop_first=True).astype(float)
X_b = pd.concat([X_a, controls], axis=1)
note(f"- features: {len(skill_cols)} skill indicators; "
     f"specification B adds {controls.shape[1]} geography and "
     f"work-arrangement controls")

ALPHAS = np.logspace(-2, 3, 30)
results = {}
for name, X in [("A: skills only", X_a), ("B: skills + controls", X_b)]:
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25,
                                              random_state=SEED)
    model = RidgeCV(alphas=ALPHAS).fit(X_tr, y_tr)
    pred = model.predict(X_te)

    r2 = r2_score(y_te, pred)
    cv = cross_val_score(RidgeCV(alphas=ALPHAS), X, y, cv=5, scoring="r2")
    # back to dollars so the error is readable
    rmse = np.sqrt(mean_squared_error(np.exp(y_te), np.exp(pred)))
    mae = mean_absolute_error(np.exp(y_te), np.exp(pred))
    results[name] = (model, X, r2)

    note("")
    note(f"**{name}**")
    note(f"- held-out R-squared (log scale): {r2:.3f}")
    note(f"- 5-fold cross-validated R-squared: {cv.mean():.3f} "
         f"(sd {cv.std():.3f})")
    note(f"- RMSE ${rmse:,.0f} | MAE ${mae:,.0f}")

# Baseline: predict the training median for everyone
X_tr, X_te, y_tr, y_te = train_test_split(X_a, y, test_size=0.25,
                                          random_state=SEED)
base = np.full(len(y_te), y_tr.median())
note("")
note("**Baseline: predict the median for every posting**")
note(f"- R-squared: {r2_score(y_te, base):.3f}")
note(f"- RMSE ${np.sqrt(mean_squared_error(np.exp(y_te), np.exp(base))):,.0f} | "
     f"MAE ${mean_absolute_error(np.exp(y_te), np.exp(base)):,.0f}")

# Coefficients from specification B, read as a percentage effect on pay
model, X, _ = results["B: skills + controls"]
coef = pd.Series(model.coef_, index=X.columns)
coef = coef[[c for c in coef.index if c.startswith("skill__")]]
coef.index = [c.replace("skill__", "") for c in coef.index]
effect = (np.exp(coef) - 1) * 100

# A coefficient estimated from a handful of postings is noise, not a
# finding, so each skill is reported with the evidence behind it.
MIN_SUPPORT = 30
support = X_a.sum()
support.index = [c.replace("skill__", "") for c in support.index]
solid = effect[support >= MIN_SUPPORT]
note("")
note(f"Coefficients below are limited to the {len(solid)} skills appearing in "
     f"at least {MIN_SUPPORT} of the {len(data):,} postings that disclose pay. "
     f"{len(effect) - len(solid)} rarer skills are estimated but not reported, "
     f"because the data cannot support them.")

note("")
note("Skills associated with higher pay (percentage effect, specification B):")
for name, v in solid.sort_values(ascending=False).head(12).items():
    note(f"  {v:+6.1f}%   {name:<34} ({int(support[name]):>4} postings)")
note("")
note("Skills associated with lower pay:")
for name, v in solid.sort_values().head(12).items():
    note(f"  {v:+6.1f}%   {name:<34} ({int(support[name]):>4} postings)")

top = pd.concat([solid.sort_values(ascending=False).head(12),
                 solid.sort_values().head(12)]).sort_values()
fig, ax = plt.subplots(figsize=(8.5, 8))
ax.barh(top.index, top.values,
        color=[ORANGE if v < 0 else BLUE for v in top.values])
ax.axvline(0, color=INK, linewidth=1)
ax.set_title("Skills and Pay: Estimated Effect on Annual Salary",
             fontsize=13, fontweight="bold", color=INK, pad=12)
ax.set_xlabel("Estimated effect on pay, percent")
fig.tight_layout()
fig.savefig(FIG, dpi=150)
plt.close(fig)

LOG.write_text("\n".join(log) + "\n")
print(f"\nwritten {LOG} and {FIG}")
