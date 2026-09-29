"""Phase 4b — classify each cell's target recoverability A-D and emit figures.

Classes: A robust (|bias|<=0.5yr or <=10% of Amax AND rmse_rel<=0.4, fail<=0.1)
         B conditional (recoverable but sensitive: fail<=0.25, moderate error)
         C weak (estimates produced but error dominating)
         D not identifiable (fail>0.5 or degenerate)
"""
import pandas as pd, numpy as np, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

s = pd.read_csv('../output/tables/recoverability_map.csv')

def cls(row, t):
    if row['fail_freq'] > 0.5 or not np.isfinite(row.get(f'{t}_bias', np.nan)):
        return 'D'
    b = abs(row[f'{t}_bias']); rm = row[f'{t}_rmse_rel']
    if row['fail_freq'] <= 0.1 and (b <= 0.5 or row[f'{t}_relbias'] <= 0.10) and rm <= 0.4:
        return 'A'
    if row['fail_freq'] <= 0.25 and (b <= 1.5 or row[f'{t}_relbias'] <= 0.35):
        return 'B'
    if rm <= 0.8 or row[f'{t}_relbias'] <= 0.8:
        return 'C'
    return 'D'

for t in ['median', 'mean_age', 'q90', 'q95', 'E_M50']:
    s[f'class_{t}'] = [cls(r, t) for _, r in s.iterrows()]
s.to_csv('../output/tables/recoverability_map.csv', index=False)

# headline table: focal species, informed analyst
focal = ['Suricata_suricatta', 'Cervus_elaphus', 'Loxodonta_africana']
f = s[(s.species.isin(focal)) & (s.analyst == 'informed')]

# figure 1: median bias heatmap over n x scenario type (focal spp pooled)
scn = f.copy()
def scen(r):
    if r['assemblage'] == 'catastrophic':
        return f"catastrophic r={r['r']:+.2f}"
    if r['q'] != 'constant': return f"q={r['q']}"
    if r['resolution'] != 'exact': return f"res={r['resolution']}"
    if r['reporting'] != 'all': return f"report={r['reporting']}"
    return 'baseline'
scn['scenario'] = scn.apply(scen, axis=1)
pv = scn.groupby(['scenario', 'n'])['median_bias'].mean().unstack()
order = ['baseline', 'res=rounded', 'res=interval2', 'res=noisy', 'q=juv_moderate',
         'q=juv_severe', 'q=monotone_logistic', 'q=nonmonotone',
         'report=grouped', 'report=max_only', 'report=mixed',
         'catastrophic r=-0.05', 'catastrophic r=+0.00', 'catastrophic r=+0.05']
pv = pv.reindex([o for o in order if o in pv.index])
fig, ax = plt.subplots(figsize=(8, 5))
im = ax.imshow(pv.values, aspect='auto', cmap='RdBu_r', vmin=-8, vmax=8)
ax.set_xticks(range(pv.shape[1]), pv.columns)
ax.set_yticks(range(pv.shape[0]), pv.index, fontsize=8)
ax.set_xlabel('n specimens'); ax.set_title('Median age-at-death bias (yr), informed analyst\nmean over 3 focal malddaba populations')
for i in range(pv.shape[0]):
    for j in range(pv.shape[1]):
        if np.isfinite(pv.values[i, j]):
            ax.text(j, i, f'{pv.values[i,j]:+.1f}', ha='center', va='center', fontsize=7)
plt.colorbar(im, label='est − truth (yr)')
fig.tight_layout(); fig.savefig('../output/figures/fig_recoverability_map.png', dpi=170)

# figure 2: class distribution per target (informed, focal spp)
targs = ['median', 'mean_age', 'q90', 'q95', 'E_M50']
cd = {t: f[f'class_{t}'].value_counts(normalize=True).reindex(['A','B','C','D']).fillna(0)
      for t in targs}
cdf = pd.DataFrame(cd).T
fig, ax = plt.subplots(figsize=(7, 3.5))
bottom = np.zeros(len(cdf))
for c_, col in zip(['A', 'B', 'C', 'D'], ['#2ca02c', '#8bc34a', '#ff9800', '#d62728']):
    ax.barh(cdf.index, cdf[c_], left=bottom, color=col, label=c_)
    bottom += cdf[c_].values
ax.set_xlabel('fraction of scenarios'); ax.legend(title='recoverability', ncol=4)
ax.set_title('Recoverability class distribution by target (informed analyst)')
fig.tight_layout(); fig.savefig('../output/figures/fig_recoverability_classes.png', dpi=170)

print('class table (informed, focal spp):')
print(cdf.round(2).to_string())
print('\nmax_only rows:', s[(s.reporting=='max_only')]['class_median'].value_counts().to_dict())
