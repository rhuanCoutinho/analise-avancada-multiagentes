---
name: data-visualization
description: Create effective data visualizations with Python (matplotlib, seaborn, plotly). Use when building charts, choosing the right chart type for a dataset, creating publication-quality figures, or applying design principles like accessibility and color theory.
user-invocable: false
---

# Data Visualization Skill

Chart selection guidance, Python visualization code patterns, design principles, and accessibility considerations for creating effective visualizations.

## Chart Selection Guide

### Choose by Data Relationship

| What You're Showing | Best Chart | Alternatives |
|---|---|---|
| **Trend over time** | Line chart | Area chart (if showing cumulative or composition) |
| **Comparison across categories** | Vertical bar chart | Horizontal bar (many categories), lollipop chart |
| **Ranking** | Horizontal bar chart | Dot plot, slope chart (comparing two periods) |
| **Part-to-whole composition** | Stacked bar chart | Treemap (hierarchical), waffle chart |
| **Composition over time** | Stacked area chart | 100% stacked bar (for proportion focus) |
| **Distribution** | Histogram | Box plot (comparing groups), violin plot, strip plot |
| **Correlation (2 variables)** | Scatter plot | Bubble chart (add 3rd variable as size) |
| **Correlation (many variables)** | Heatmap (correlation matrix) | Pair plot |
| **Geographic patterns** | Choropleth map | Bubble map, hex map |
| **Flow / process** | Sankey diagram | Funnel chart (sequential stages) |
| **Relationship network** | Network graph | Chord diagram |
| **Performance vs. target** | Bullet chart | Gauge (single KPI only) |
| **Multiple KPIs at once** | Small multiples | Dashboard with separate KPIs |

### When NOT to Use Certain Charts

- **Pie charts**: Avoid unless there are fewer than 6 categories and rough proportions matter more than exact comparisons. Bar charts are usually easier to compare.
- **3D charts**: Never; they distort perception without adding information.
- **Dual-axis charts**: Use cautiously, with both axes clearly labeled; they can imply misleading correlation.
- **Stacked bars with many categories**: Middle segments are hard to compare; use small multiples or grouped bars.
- **Donut charts**: Same limitations as pies; reserve for a single KPI at most.

## Python Visualization Patterns

### Setup and Style

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (10, 6), 'figure.dpi': 150, 'font.size': 11,
    'axes.titlesize': 14, 'axes.titleweight': 'bold',
    'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10,
})
PALETTE_CATEGORICAL = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860']
```

### Line Chart (Time Series)

```python
fig, ax = plt.subplots(figsize=(10, 6))
for label, group in df.groupby('category'):
    ax.plot(group['date'], group['value'], label=label, linewidth=2)
ax.set(title='Metric Trend by Category', xlabel='Date', ylabel='Value')
ax.legend(loc='upper left')
ax.spines[['top', 'right']].set_visible(False)
fig.autofmt_xdate()
plt.tight_layout()
```

### Bar Chart (Comparison)

```python
ordered = df.sort_values('metric', ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(ordered['category'], ordered['metric'], color=PALETTE_CATEGORICAL[0])
ax.set(title='Metric by Category (Ranked)', xlabel='Metric Value')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
```

### Histogram (Distribution)

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['value'], bins=30, color=PALETTE_CATEGORICAL[0], edgecolor='white', alpha=.8)
ax.axvline(df['value'].mean(), color='red', linestyle='--', label='Mean')
ax.axvline(df['value'].median(), color='green', linestyle='--', label='Median')
ax.set(title='Distribution of Values', xlabel='Value', ylabel='Frequency')
ax.legend()
plt.tight_layout()
```

### Heatmap

```python
pivot = df.pivot_table(index='row_dim', columns='col_dim', values='metric', aggfunc='sum')
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(pivot, annot=True, fmt=',.0f', cmap='YlOrRd', linewidths=.5, ax=ax)
ax.set(title='Metric by Dimension', xlabel='Column dimension', ylabel='Row dimension')
plt.tight_layout()
```

### Interactive Charts with Plotly

```python
import plotly.express as px

fig = px.line(df, x='date', y='value', color='category',
              title='Metric Trend by Category',
              labels={'value': 'Metric Value', 'date': 'Date'})
fig.update_layout(hovermode='x unified')
fig.show()
```

## Number Formatting

```python
def format_number(value, kind='number'):
    if kind == 'currency':
        return f'${value:,.2f}'
    if kind == 'percent':
        return f'{value:.1f}%'
    return f'{value:,.0f}'

ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda value, position: format_number(value, 'currency'))
)
```

## Design Principles

### Color

- Use color to encode information, not only as decoration.
- Use a sequential palette for ordered values and a diverging palette around a meaningful midpoint.
- Limit categorical palettes to roughly 6–8 distinguishable colors.
- Avoid relying only on red/green; use blue/orange or other accessible contrasts.

### Typography and Layout

- Prefer an informative title that states the finding over a generic chart name.
- Add context such as date range, filters, and source in a subtitle or note.
- Label axes and units; use readable text and avoid unnecessary rotation.
- Sort categories meaningfully. Keep whitespace and remove chart junk.
- Bar-chart axes should start at zero. Use consistent scales when comparing panels.
- Show uncertainty or caveats when the data does not support a precise conclusion.

## Accessibility

### Color and Screen Readers

- Do not rely on color alone; use labels, patterns, or different line styles.
- Include alt text describing the chart and its main message.
- Provide a table or other text alternative for chart data.
- Use semantic titles, labels, and sufficient contrast.

### Checklist

- [ ] Meaning is understandable without color alone.
- [ ] Labels are readable at normal zoom and axes include units.
- [ ] The title accurately describes the chart.
- [ ] Data source and date range are stated.
- [ ] Scales and baselines do not mislead.
- [ ] A text or tabular alternative is available.
