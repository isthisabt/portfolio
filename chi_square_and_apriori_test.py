
# Import necessary libraries
import io
import os
import math
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as ss
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
from itertools import combinations
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# Contexts Barplot
binary_sum = new_df.sum()
binary_sum_sorted = binary_sum.sort_values()
plt.figure(figsize=(8, 6))
colors = sns.color_palette("turbo", len(binary_sum_sorted))
sns.barplot(x=binary_sum_sorted.index, y=binary_sum_sorted.values, palette=colors)
plt.title('Contexts found in sampled tweets')
plt.xticks(rotation=35, ha='right')
plt.xlabel('')
plt.show()
print(binary_sum_sorted)

# Chi-square calculations
chi2_results = pd.DataFrame(index=new_df.columns, columns=new_df.columns, dtype=float)
for col1 in new_df.columns:
    for col2 in new_df.columns:
        if col1 != col2:
            observed = pd.crosstab(new_df[col1], new_df[col2])
            chi2, _, _, _ = chi2_contingency(observed)
            chi2_results.at[col1, col2] = chi2

# Create a mask and blended cmap for displaying heatmap
mask = np.triu(np.ones_like(chi2_results, dtype=bool))
colors = ['#363673', '#37AD86', '#F7E092', '#FDBD28', '#F04848', '#B03030']
custom_cmap = LinearSegmentedColormap.from_list("custom_gradient", colors)


def blend_cmap(cmap, blend_factor=0.5):
    original_cmap = plt.get_cmap(cmap)
    colors = original_cmap(np.arange(original_cmap.N))
    white = np.ones((original_cmap.N, 4))
    new_colors = colors * (1 - blend_factor) + white * blend_factor
    return LinearSegmentedColormap.from_list('blended_cmap', new_colors)


blended_cmap = blend_cmap(custom_cmap, blend_factor=0.1)

# Visualize chi-square results as heatmap
plt.figure(figsize=(12, 8))
sns.set(font_scale=1.2)
sns.heatmap(chi2_results, annot=True, cmap=blended_cmap, fmt=".2f", mask=mask,
            linewidths=0.5, linecolor='lightgray')
plt.title('Chi-square Correlation Test', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
plt.show()

# Example Contingency Table
varA = 'context A'
varB = 'context B'
obs_tab = pd.crosstab(new_df[varA], new_df[varB])
print("Contingency Table for", varA, "and", varB)
print(obs_tab)

# Calculate chi-squared statistic
chi2, p, dof, expected = chi2_contingency(obs_tab)

# Calculate the phi coefficient for 2x2 table
if obs_tab.shape == (2, 2):
    phi = np.sqrt(chi2 / obs_tab.sum().sum())
    cross_product_diff = (obs_tab.iloc[0, 0] * obs_tab.iloc[1, 1]) -                          (obs_tab.iloc[0, 1] * obs_tab.iloc[1, 0])
    if phi > 0:
        correlation = "positively correlated" if cross_product_diff > 0 else "negatively correlated"
    else:
        correlation = "not a 2x2 table, phi coefficient not applicable"
else:
    correlation = "not a 2x2 table, phi coefficient not applicable"
    phi = None

print(f"The variables are {correlation}. (Chi2: {chi2}, p-value: {p}, Phi: {phi})")

# Apriori analysis
new_df = new_df.astype(bool)
freqItemsAP = apriori(new_df, min_support=0.1, use_colnames=True)
pd.set_option('display.max_colwidth', None)
print(freqItemsAP)

# Generate rules
rulesAP = association_rules(freqItemsAP, metric='confidence', min_threshold=0.6, support_only=False)
print(rulesAP)

# Support Heat Map
new_df = new_df.fillna(False).astype(bool)
freqItemsAP = apriori(new_df, min_support=0.1, use_colnames=True)
freqItemsAP_pairs = freqItemsAP[freqItemsAP['itemsets'].apply(lambda x: len(x) == 2)]

# Extract unique items
unique_items = sorted(set().union(*(set(itemset) for itemset in freqItemsAP_pairs['itemsets'])))
support_matrix = np.zeros((len(unique_items), len(unique_items)))
item_index = {item: idx for idx, item in enumerate(unique_items)}

# Fill support matrix
for _, row in freqItemsAP_pairs.iterrows():
    items = row['itemsets']
    support = row['support']
    if len(items) > 1:
        for pair in combinations(items, 2):
            i, j = item_index[pair[0]], item_index[pair[1]]
            support_matrix[i, j] = support
            support_matrix[j, i] = support

support_df = pd.DataFrame(support_matrix, index=unique_items, columns=unique_items)
blended_cmap = blend_cmap(custom_cmap, blend_factor=0.1)

# Visualize support matrix heatmap
plt.figure(figsize=(12, 8))
sns.set(font_scale=1.2)
sns.heatmap(support_df, annot=True, cmap=blended_cmap, fmt=".2f", linewidths=0.5)
plt.title('Pairwise Support Analysis Heatmap', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.show()

# Comparative Barplot
categories = ['Derogatory Language', 'Gender Based Hatred']
values = {
    'Derogatory Language': [61.9, 64.6],
    'Gender Based Hatred': [11.1, 36.4]
}
bar_width = 0.25
index = np.arange(len(categories))

fig, ax = plt.subplots(figsize=(10, 6))
bar1 = ax.bar(index - bar_width / 2, [values[cat][0] for cat in categories], bar_width,
              label='Male Journalist', color='#363673')
bar2 = ax.bar(index + bar_width / 2, [values[cat][1] for cat in categories], bar_width,
              label='Journalist Z', color='#B03030')

ax.set_ylabel('Percentage', fontsize=14)
ax.set_title('Tweet Context Percentage Comparison: Male Journalist vs Journalist Z', fontsize=16)
ax.set_xticks(index)
ax.set_xticklabels(categories, fontsize=12)
ax.legend()
ax.set_ylim(0, 70)

def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=12)

add_labels(bar1)
add_labels(bar2)
plt.grid(True, linestyle='--', linewidth=0.5, color='gray')
plt.show()
