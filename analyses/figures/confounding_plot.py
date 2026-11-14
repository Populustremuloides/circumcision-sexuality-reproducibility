"""Marginal probability-mixture illustration; distinct from conditional-OR model."""
import os
os.environ['MPLCONFIGDIR']='/tmp/circ-confounding-matplotlib'
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
OUT=Path(__file__).resolve().parents[2]/'outputs/selected_figures/confounding'
meta=json.loads((OUT/'validation.json').read_text())
pI=meta['standardized_intact_probability']; pC=meta['standardized_circumcised_probability']; gap=pC-pI
contrasts=[.025,.05,.10,.20,.40]
styles=[(0,(12,3)),(0,(8,3)),(0,(5,2.5)),(0,(3,2)),(0,(1,2))]
navy='#25364B'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,'svg.fonttype':'none','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(10.8,7.0))
fig.subplots_adjust(left=.105,right=.71,bottom=.15,top=.84)
# Discrete soft rainbow bands, using approximately multiplicative thresholds.
# Mask probabilities outside [0,1]; gray is infeasible, not zero effect.
axis=np.linspace(0,1,1801)
QI,QC=np.meshgrid(axis,axis)
with np.errstate(divide='ignore',invalid='ignore'):
 required=gap/(QC-QI)
 a_grid=pI-QI*required
 b_grid=a_grid+required
feasible=(QC>QI)&(a_grid>=0)&(b_grid<=1)&(required<=1)
values=np.ma.array(required*100,mask=~feasible)
levels=[gap*100,5,10,20,40,80,100]
base=LinearSegmentedColormap.from_list('pride_effect',
 ['#E40303','#FF8C00','#FFED00','#008026','#004DFF','#750787'])
colors=base(np.linspace(0,1,6));colors[:,:3]=.23*colors[:,:3]+.77
cmap=ListedColormap(colors);cmap.set_bad('#E9ECEF')
norm=BoundaryNorm(levels,cmap.N)
ax.set_facecolor('#E9ECEF')
mesh=ax.pcolormesh(QI,QC,values,cmap=cmap,norm=norm,shading='nearest',
                  rasterized=True,linewidth=0)
# Exact boundaries of the effect-size bands, restricted to feasible probabilities.
for pp in levels[1:-1]:
 d=pp/100
 lo=max(0,(pI+d-1)/d);hi=min(1-gap/d,pI/d)
 q=np.linspace(lo,hi,500)
 ax.plot(q,q+gap/d,color='#81878D',lw=.55)
# Numerical checks on every feasible color sample.
assert np.max(abs((1-QI[feasible])*a_grid[feasible]+QI[feasible]*b_grid[feasible]-pI))<1e-12
assert np.max(abs((1-QC[feasible])*a_grid[feasible]+QC[feasible]*b_grid[feasible]-pC))<1e-12
rows=[]
for d,ls in zip(contrasts,styles):
 lo=max(0,(pI+d-1)/d)
 hi=min(1-gap/d,pI/d)
 assert hi>=lo
 qi=np.linspace(lo,hi,700); qc=qi+gap/d
 a=pI-qi*d; b=a+d
 assert a.min()>-1e-12 and b.max()<1+1e-12
 assert qc.min()>=0 and qc.max()<=1+1e-12
 ri=(1-qi)*a+qi*b; rc=(1-qc)*a+qc*b
 assert np.max(abs(ri-pI))<1e-12 and np.max(abs(rc-pC))<1e-12
 rows.extend(dict(outcome_probability_difference=d,intact_confounder_prevalence=float(u),circumcised_confounder_prevalence=float(v),outcome_probability_without=float(aa),outcome_probability_with=float(bb)) for u,v,aa,bb in zip(qi,qc,a,b))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal',adjustable='box')
ax.set_xticks(np.arange(0,1.01,.2)); ax.set_yticks(np.arange(0,1.01,.2))
ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0)); ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
ax.spines[['top','right']].set_visible(False); ax.spines[['left','bottom']].set_color('#9AA3AA')
ax.set_xlabel('Percentage of intact men\nwith the unmeasured characteristic',labelpad=10)
ax.set_ylabel('Percentage of circumcised men\nwith the unmeasured characteristic',labelpad=10)
ax.set_title('Confounding scenarios explaining the full adjusted gap\nProbability-space illustration',fontsize=12,pad=18)
labels=[f'{gap*100:.2f}–5','5–10','10–20','20–40','40–80','80–100']
handles=[Patch(facecolor=c,label=label) for c,label in zip(colors,labels)]
handles.append(Patch(facecolor='#E9ECEF',label='Infeasible'))
leg=fig.legend(handles=handles,loc='center',bbox_to_anchor=(.82,.51),frameon=False,
 title='Required increase in probability\nof reported lifetime male–male\nsexual behavior with the characteristic\n(percentage points)',
 title_fontsize=9.5,fontsize=10,labelspacing=1.4)
leg.get_title().set_multialignment('center')
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'confounding_probability_bands.{ext}',dpi=220,facecolor='white')
pd.DataFrame(rows).to_csv(OUT/'probability_bands_curve_points.csv',index=False)
(OUT/'probability_bands_validation.json').write_text(json.dumps(dict(model='marginal binary-confounder mixture, common outcome probabilities across circumcision groups',intact_probability=pI,circumcised_probability=pC,gap=gap,points=len(rows),feasible_color_samples=int(feasible.sum()),color_scale='discrete bands',band_boundaries_percentage_points=levels),indent=2)+'\n')
print('Saved probability figure; all 3500 curve points pass probability and mixture checks.')
