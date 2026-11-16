"""Paired display of previously validated timing decompositions; no new models."""
import os
os.environ['MPLCONFIGDIR']='/tmp/circ-timing-matplotlib'
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter,ScalarFormatter
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parents[2]/'outputs/selected_figures/timing'
orpoints=pd.read_csv(OUT/'curve_points.csv');prob=pd.read_csv(OUT/'probability_curves.csv');black=pd.read_csv(OUT/'contribution_curves.csv')
shares=[.01,.015,.025,.05,.10];colors=['#25364B']*5
styles=[(0,(12,3)),(0,(8,3)),(0,(5,2.5)),(0,(3,2)),(0,(1,2))]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,'svg.fonttype':'none','pdf.fonttype':42})
fig,(b,a)=plt.subplots(1,2,figsize=(15.8,5.8));fig.subplots_adjust(left=.065,right=.84,bottom=.16,top=.85,wspace=.25)
for f,c,ls in zip(shares,colors,styles):
 q=orpoints.loc[np.isclose(orpoints.adult_share,f)]
 a.plot(q.adult_OR,q.early_OR,color=c,lw=1.8,ls=ls)
 if q.early_OR.iloc[-1]<1.00001:a.plot(q.adult_OR.iloc[-1],1,'o',color=c,ms=4.5,clip_on=False,zorder=6)
 else:a.annotate('',xy=(260,q.early_OR.iloc[-1]),xytext=(220,q.early_OR.iloc[-3]),annotation_clip=False,zorder=6,arrowprops=dict(arrowstyle='->',color=c,lw=1.8,mutation_scale=17,clip_on=False))
 q=prob.loc[np.isclose(prob.adult_share,f)]
 b.plot(q.adult_probability*100,q.early_probability*100,color=c,lw=1.8,ls=ls)
 b.plot(q.adult_probability.iloc[-1]*100,q.early_probability.iloc[-1]*100,'o',color=c,ms=4.5,zorder=6,clip_on=False)
patterns=[(.1,(0,(12,4)),'90% before 18'),(.25,(0,(8,4)),'75% before 18'),(.5,(0,(5,3)),'50% each'),(.75,(0,(2,2)),'75% adult'),(.9,(0,(1,2)),'90% adult')]
# Six translucent pride-color bands encode adult-excess ranges 0–10,
# 10–25, 25–50, 50–75, 75–90, and 90–100%, from top to bottom.
# Restrict shading to adult OR >= the fitted OR and early OR <= it,
# where these ordered bands describe admissible positive mixtures.
common=json.loads((OUT/'validation.json').read_text())['adjusted_OR']
gx=np.geomspace(common,250,1600)
bounds=[np.full_like(gx,common)]
for target,_,_ in patterns:
 q=black.loc[np.isclose(black.adult_excess_fraction,target)].sort_values('adult_OR')
 q=q.loc[q.adult_OR>common]
 bounds.append(np.interp(np.log(gx),np.r_[np.log(common),np.log(q.adult_OR)],np.r_[common,q.early_OR]))
bounds.append(np.ones_like(gx))
pride=['#E40303','#FF8C00','#FFED00','#008026','#004DFF','#750787']
for upper,lower,color in zip(bounds[:-1],bounds[1:],pride):
 assert np.all(upper>=lower-1e-9)
 a.fill_between(gx,lower,upper,color=color,alpha=.14,linewidth=0,zorder=0)
# Also show the complementary region: adult OR from 1 to the fitted OR,
# with the before-18 OR above the fitted OR. Both components remain nonnegative.
lx=np.geomspace(1,common,800)
left_bounds=[np.full_like(lx,common)]
for target,_,_ in patterns:
 q=black.loc[np.isclose(black.adult_excess_fraction,target)].sort_values('adult_OR')
 q=q.loc[q.adult_OR<common]
 vals=np.interp(np.log(lx),np.r_[np.log(q.adult_OR),np.log(common)],np.r_[q.early_OR,common],left=1.62)
 left_bounds.append(np.clip(vals,common,1.62))
left_bounds.append(np.full_like(lx,1.62))
for lower,upper,color in zip(left_bounds[:-1],left_bounds[1:],pride):
 assert np.all(upper>=lower-1e-8)
 a.fill_between(lx,lower,upper,color=color,alpha=.14,linewidth=0,zorder=0)
for boundary in left_bounds[1:-1]:
 a.plot(lx,np.where(boundary<1.62-1e-8,boundary,np.nan),color='#777777',lw=.65,zorder=1)
# Boundary curves are thin gray lines, directly labeled with excess allocation.
for boundary,(_,_,label) in zip(bounds[1:-1],patterns):
 a.plot(gx,boundary,color='#777777',lw=.65,zorder=1)
 a.text(235,boundary[-1]-.007 if label in ['50% each','75% adult'] else boundary[-1]+.007,label,fontsize=8,color='#555555',ha='right',va='top' if label in ['50% each','75% adult'] else 'bottom')
# Probability bands use component-weighted probabilities from the same model.
pc=json.loads((OUT/'probability_validation.json').read_text())['standardized_total_probability']*100
px=np.linspace(pc,100,1600)
pbounds=[np.full_like(px,pc)]
pcon=pd.read_csv(OUT/'probability_contributions.csv')
for target,_,_ in patterns:
 q=pcon.loc[np.isclose(pcon.adult_excess_fraction,target)].sort_values('adult_probability')
 q=q.loc[q.adult_probability*100>pc]
 pbounds.append(np.interp(px,np.r_[pc,q.adult_probability*100],np.r_[pc,q.early_probability*100]))
edge=pd.read_csv(OUT/'probability_full_adult_excess.csv').sort_values('adult_probability')
pbounds.append(np.interp(px,edge.adult_probability*100,edge.early_probability*100))
for upper,lower,color in zip(pbounds[:-1],pbounds[1:],pride):
 assert np.all(upper>=lower-1e-8)
 b.fill_between(px,lower,upper,color=color,alpha=.14,linewidth=0,zorder=0)
for boundary,(_,_,label) in zip(pbounds[1:-1],patterns):
 b.plot(px,boundary,color='#777777',lw=.65,zorder=1)
 b.text(98,boundary[-1]-.035 if label in ['50% each','75% adult'] else boundary[-1]+.025,('90% of modeled excess comes from\ncircumcision before age 18' if label=='90% before 18' else label),fontsize=8,color='#555555',ha='right',va='top' if label in ['50% each','75% adult'] else 'bottom')
# Complementary probability region, bounded by adult conditional OR=1.
# Work horizontally at fixed before-18 probability to preserve the curved boundary.
py=np.linspace(pc,7.0,1000)
zero=pd.read_csv(OUT/'probability_zero_adult_excess.csv').sort_values('early_probability')
left_pbounds=[np.interp(py,zero.early_probability*100,zero.adult_probability*100)]
for target,_,_ in patterns:
 q=pcon.loc[np.isclose(pcon.adult_excess_fraction,target)]
 q=q.loc[(q.adult_probability*100<pc)&(q.early_probability*100>pc)].sort_values('early_probability')
 left_pbounds.append(np.interp(py,np.r_[pc,q.early_probability*100],np.r_[pc,q.adult_probability*100]))
left_pbounds.append(np.full_like(py,pc))
for left,right,color in zip(left_pbounds[:-1],left_pbounds[1:],pride):
 assert np.all(right>=left-1e-8)
 b.fill_betweenx(py,left,right,color=color,alpha=.14,linewidth=0,zorder=0)
for boundary in left_pbounds[1:-1]:
 b.plot(boundary,py,color='#777777',lw=.65,zorder=1)
a.set_xscale('log');a.set_xlim(1,250);a.set_ylim(1,max(1.62,common*1.04));a.set_xticks([1,2,5,10,20,50,100,250]);a.xaxis.set_major_formatter(ScalarFormatter());a.minorticks_off()
a.set_xlabel('Odds ratio among men circumcised as adults\n(logarithmic scale)');a.set_ylabel('Odds ratio among men circumcised before 18')
a.set_title('B  Adjusted odds ratio of lifetime male–male sexual behavior\nin circumcised men versus intact men',loc='center',fontsize=12,pad=14)
b.set_xlim(float(np.min(left_pbounds[0])),100);b.set_ylim(float(np.min(pbounds[-1])),7.0);b.set_xticks([5,20,40,60,80,100]);b.set_yticks([5,5.5,6,6.5,7]);b.xaxis.set_major_formatter(PercentFormatter(100,decimals=0));b.yaxis.set_major_formatter(PercentFormatter(100,decimals=1))
b.set_xlabel('Probability among men circumcised as adults');b.set_ylabel('Probability among men circumcised before 18')
b.set_title('A  Adjusted probability of lifetime male–male sexual behavior\nin circumcised men',loc='center',fontsize=12,pad=14)
for ax in [a,b]:
 ax.grid(False);ax.spines[['top','right']].set_visible(False);ax.spines[['left','bottom']].set_color('#9AA3AA')
cl=[Line2D([0],[0],color=c,lw=1.8,ls=ls,label=f'{100*f:g}%'+('*' if f==.015 else '')) for f,c,ls in zip(shares,colors,styles)]
legend=fig.legend(handles=cl,loc='center left',bbox_to_anchor=(.865,.51),ncol=1,frameon=False,title='Assumed percentage of\ncircumcisions performed\nin adulthood',fontsize=10,title_fontsize=10,handlelength=4,labelspacing=1.8,borderaxespad=0)
legend.get_title().set_multialignment('center')
legend.get_title().set_horizontalalignment('center')
fig.canvas.draw()
legend_box=legend.get_window_extent().transformed(fig.transFigure.inverted())
fig.text((legend_box.x0+legend_box.x1)/2,.235,
 '*Extrapolated from 1996\nU.S. procedure counts\n(Owings & Kozak, 1998; NCHS).',
 ha='center',multialignment='center',va='top',fontsize=8,color='#4B555F',linespacing=1.4)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'timing_paired.{ext}',dpi=220,facecolor='white')
print('Saved paired PNG, PDF, and SVG.')
