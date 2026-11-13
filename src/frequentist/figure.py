"""Rebuild the original two-panel research figure from executed outputs."""
from html import escape
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/frequentist'
models = pd.read_csv(OUT/'models.csv')
prevalence = pd.read_csv(OUT/'prevalence.csv')
sens = pd.read_csv(OUT/'sensitivities.csv')
flow = pd.read_csv(OUT/'sample_flow.csv')
diff = pd.read_csv(OUT/'prevalence_differences.csv')
validation = json.loads((OUT/'validation.json').read_text())
main = models[models['sample'].eq('available_for_model')]
fixed = models[models['sample'].eq('full_model_complete_cases')]

# Colors and marker shapes encode endpoints in both panels. Marker fill in the
# prevalence panel identifies circumcision status. Lines denote 95% limits.
COLORS = {'identity_gb':'#663D73','msm_ever':'#006C72'}
LABELS = {'identity_gb':'Gay/bisexual identity', 'msm_ever':'Lifetime sex with men',
          'identity_gay':'Gay versus heterosexual', 'identity_bi':'Bisexual versus heterosexual'}
MODEL_LABELS = {'unadjusted':'Unadjusted','age_cycle':'Age + survey cycle',
                'demographic':'+ race/ethnicity + education','full':'+ nativity'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
                     'axes.labelsize':11,'pdf.fonttype':42,'svg.fonttype':'none'})
fig = plt.figure(figsize=(12.8,5.8),facecolor='white')
left = fig.add_axes([.17,.29,.27,.46])
right = fig.add_axes([.67,.29,.24,.46])
fig.text(.055,.94,'Circumcision, sexual identity, and lifetime sex with men',fontsize=17,weight='bold')
fig.text(.055,.885,'NHANES 2005–2016  ·  Men aged 20–59  ·  Survey-weighted estimates with 95% confidence intervals',
         fontsize=11,color='#4b4b4b')
fig.text(.055,.81,'A   Reported prevalence',fontsize=12,weight='bold')
fig.text(.515,.81,'B   Association after adjustment',fontsize=12,weight='bold')
for y,outcome in zip([1,0],['identity_gb','msm_ever']):
    for c,offset in [(0,.14),(1,-.14)]:
        marker = 'o' if outcome == 'identity_gb' else 's'
        r = prevalence.query('outcome == @outcome and circ == @c').iloc[0]
        p,lo,hi = 100*r.prevalence,100*r.ci_low,100*r.ci_high
        left.errorbar(p,y+offset,xerr=[[p-lo],[hi-p]],fmt=marker,ms=7,
                      color=COLORS[outcome],mfc='white' if c==0 else COLORS[outcome],
                      mec=COLORS[outcome],capsize=3,lw=1.5)
        left.text(hi+.25,y+offset,f'{p:.2f}%',va='center',fontsize=10,color=COLORS[outcome])
left.set_yticks([1,0],['Gay/bisexual\nidentity','Lifetime sex\nwith men'])
left.set_ylim(-.48,1.48)
left.set_xlim(0,9)
left.set_xticks([0,2,4,6,8])
left.set_xlabel('Weighted prevalence (%)',labelpad=9)
left.legend(handles=[Line2D([],[],marker='o',ls='',mfc='white',mec='#333333',label='Uncircumcised'),
                     Line2D([],[],marker='o',ls='',color='#333333',label='Circumcised')],
            frameon=False,loc='upper center',bbox_to_anchor=(.48,-.28),ncol=2,fontsize=10,
            handletextpad=.5,columnspacing=1.)
for y,model in zip([3,2,1,0],MODEL_LABELS):
    for out,offset,marker in [('identity_gb',.12,'o'),('msm_ever',-.12,'s')]:
        r = fixed.query('outcome == @out and model == @model').iloc[0]
        right.errorbar(r.odds_ratio,y+offset,xerr=[[r.odds_ratio-r.ci_low],[r.ci_high-r.odds_ratio]],
                       fmt=marker,color=COLORS[out],ms=6,capsize=3,lw=1.5)
right.axvline(1,color='#777777',ls='--',lw=1,zorder=0)
right.set_xscale('log')
right.set_xlim(.65,2.7)
right.set_xticks([.75,1,1.5,2,2.5],[.75,1,1.5,2,2.5])
right.set_ylim(-.45,3.45)
right.set_yticks([3,2,1,0],list(MODEL_LABELS.values()),fontsize=10)
right.set_xlabel('Odds ratio, circumcised vs uncircumcised',labelpad=9,fontsize=10)
right.legend(handles=[Line2D([],[],marker='o',ls='',color=COLORS['identity_gb'],label='Identity'),
                      Line2D([],[],marker='s',ls='',color=COLORS['msm_ever'],label='Behavior')],
             frameon=False,loc='upper center',bbox_to_anchor=(.48,-.28),ncol=2,fontsize=10,
             handletextpad=.5,columnspacing=1.)
for ax in [left,right]:
    for side in ['top','right','left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#aaaaaa')
    ax.tick_params(axis='y',length=0,pad=10)
    ax.grid(axis='x',alpha=.12,zorder=0)
fig.text(.055,.065,'Panel A uses available endpoint records. Panel B holds each endpoint’s fully adjusted sample fixed.',
         fontsize=9,color='#555555')
fig.text(.055,.025,'Identity n = 8,962; behavior n = 9,161. Age includes a quadratic term. Associations do not establish causation.',
         fontsize=9,color='#555555')
for ext in ['png','svg','pdf']:
    fig.savefig(OUT/f'nhanes_associations.{ext}',dpi=200,facecolor='white')
    if ext == 'svg':
        path = OUT/f'nhanes_associations.{ext}'
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
plt.close(fig)
