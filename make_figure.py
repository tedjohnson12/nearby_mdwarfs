"""
Script that creates querys the NExScI database
and creates a figure based on the data.

Created by Ted Johnson (NASA GSFC 693) in Oct 2022,
uploaded to Github 2023-04-07

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
from pathlib import Path
from os import system, chdir
from datetime import datetime
from astropy import units as u, constants as c

if __name__ in '__main__':

    WORKING_DIRECTORY = Path(__file__).parent
    chdir(WORKING_DIRECTORY)

    # Build the query
    q = 'select * from pscomppars where st_teff < 3700 and sy_dist < 20'
    query = '+'.join(q.split(' '))+'&format=csv'
    url = f'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query={query}'
    print(f'Querying {url}')
    # write the file
    filename = 'nearby_mdwarfs.csv'
    with open(filename,'w') as file:
        file.write(f'# {datetime.now().strftime("%Y/%m/%d %H:%M")}\n')
    system(f'wget "{url}" -O ->> nearby_mdwarfs.csv')

    #read the data
    df = pd.read_csv('nearby_mdwarfs.csv',comment='#')
    # make some corrections
    # GJ 667 C radius
    is_gj667c = df['hostname'] == 'GJ 667 C'
    df.loc[is_gj667c,'st_rad'] = 0.42
    df['pl_approx_insol'] = 10**(df['st_lum']) / (df['pl_orbsmax'])**2

    # make the figure
    plt.style.use('bmh')
    rc('font', weight='bold')
    fig,ax = plt.subplots(1,1,figsize=(11.5,6.5))
    ax.tick_params(axis='both', which='major', labelsize=14)

    #get date
    with open(filename,'r') as file:
        date = file.readline()[1:-1]
    dist_from_bottom = 0.05
    fig.text(0.01,dist_from_bottom,'NASA Exoplanet Archive '+date,fontfamily='serif',fontsize=14,weight='normal')
    fig.text(0.9,dist_from_bottom, 'Created by: Ted Johnson (GSFC)',fontfamily='serif',fontsize=14,ha='right',weight='normal')

    alpha=0.5 # transparency
    k = 20 # scales size of markers

    has_all = ~np.isnan(df['sy_dist']) & ~np.isnan(df['pl_bmasse']) & ~np.isnan(df['pl_orbper'])
    is_transit = df['tran_flag'].values.astype('bool')
    keep  = (df['pl_orbper'] < 25) & has_all & (df['pl_bmasse'] < 20) & (df['pl_approx_insol'] < 100)

    x_kw = 'sy_dist'
    y_kw = 'pl_approx_insol'

    ax.scatter(df.loc[~is_transit & keep,x_kw],(df.loc[~is_transit & keep,y_kw]),label='Non-Transiting',c='C0',s=k*(df.loc[~is_transit & keep,'pl_bmasse']),alpha=alpha)
    ax.scatter(df.loc[is_transit & keep,x_kw],(df.loc[is_transit & keep,y_kw]),label='Transiting',c='C4',s=k*(df.loc[is_transit & keep,'pl_bmasse']),alpha=alpha)
    ax.scatter(np.nan,-1,label='Mars-mass',c='k',s=k*0.107,alpha=alpha)
    ax.scatter(np.nan,-1,label='Earth-mass',c='k',s=k*1,alpha=alpha)
    ax.scatter(np.nan,-1,label='Neptune-mass',c='k',s=k*17.15,alpha=alpha)

    lw=1
    ls=(0,(5,10))
    stop = 1
    x=0.5
    A=0.8
    ha='left'
    rot = 0
    fontsize=13
    alpha = 1
    color = 'xkcd:terracotta'
    zorder = -100

    a_venus = 0.723 # AU
    ax.axhline(1/a_venus**2,0,stop,c=color,lw=lw,alpha=alpha,ls=ls,zorder=zorder)
    ax.text(x,A*1/a_venus**2,'Venus',ha=ha,rotation=rot,fontfamily='serif',fontsize=fontsize,alpha=alpha,weight='bold')

    a_mars = 1.523 # AU
    ax.axhline(1/a_mars**2,0,stop,c=color,lw=lw,alpha=alpha,ls=ls,zorder=zorder)
    ax.text(x,A*1/a_mars**2,'Mars',ha=ha,rotation=rot,fontfamily='serif',fontsize=fontsize,alpha=alpha,weight='bold')

    a_mercury = 0.387 # AU
    ax.axhline(1/a_mercury**2,0,stop,c=color,lw=lw,alpha=alpha,ls=ls,zorder=zorder)
    ax.text(x,A*1/a_mercury**2,'Mercury',ha=ha,rotation=rot,fontfamily='serif',fontsize=fontsize,alpha=alpha,weight='bold')

    ax.set_yscale('log')

    lgnd = ax.legend(prop={'size':14,'family':'serif'},framealpha=0.7,loc='lower right')
    legend_marker_size = 40
    lgnd.legendHandles[0]._sizes = [legend_marker_size]
    lgnd.legendHandles[1]._sizes = [legend_marker_size]

    ax.set_xlabel('Distance (pc)',fontfamily='serif',fontsize=14,fontweight='bold')
    ax.set_ylabel('Stellar Insolation Flux\n(relative to Earth)',fontfamily='serif',fontsize=14,fontweight='bold')
    # ax.set_yticks([0.5,0,5,10,50,100])
    ax.set_title('Known Planets Around M-stars Within 20 pc',fontsize=14,fontfamily='serif',fontweight='bold')
    fig.savefig('nearby_mdwarfs_insolation.png',dpi=120)
    # ax.get_yticks()