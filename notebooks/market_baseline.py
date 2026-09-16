









#remote?

remote_counts = df["remote_status"].value_counts()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie( remote_counts.values, labels=remote_counts.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
ax.set_title("remote vs onsite vs hybrid")
plt.tight_layout()
plt.show()


#top emp and hiring loc

top_employers = df["company_name"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=top_employers.values, y=top_employers.index, ax=ax, color="crimson")
ax.set_xlabel("Number of Postings")
ax.set_ylabel("Employer")
ax.set_title("Top 10 Employers by Volume")
plt.tight_layout()
plt.show()


top_cities = df["city"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=top_cities.values, y=top_cities.index, ax=ax, color="goldenrod")
ax.set_xlabel("Number of Postings")
ax.set_ylabel("City")
ax.set_title("Top 10 Hiring 0ities")
plt.tight_layout()
plt.show()