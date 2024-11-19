"""
A plotly version of make_figure.py
"""

from make_figure import get_data, get_hwo_targets, get_mirecle_targets, apply_corrections
from make_figure import TRANSIT_COLOR, NONTRANSIT_COLOR, LINE_COLOR

from pathlib import Path
import numpy as np
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_PATH = Path(__file__).parent / 'nearby_exoplanets.csv'
DATA_SHELFLIFE_DAYS = 1
SIZEMODE = 'area'
A_VENUS = 0.723  # AU
A_MARS = 1.523



def is_stale()-> bool:
    if not DATA_PATH.exists():
        return True
    else:
        timestamp = DATA_PATH.stat().st_mtime
        m_time = datetime.datetime.fromtimestamp(timestamp)
        age = datetime.datetime.now() - m_time
        return age.days > DATA_SHELFLIFE_DAYS
        
def run_query()-> pd.DataFrame:
    _df = get_data(1000000,100000) # get everything
    _df.dropna(subset=['sy_dist','st_teff'], inplace=True)
    return _df

def get_df(
    max_teff: int,
    max_dist: float,
    max_period: float,
    max_mass: float,
    max_insolation: float,
)-> pd.DataFrame:
    if is_stale():
        _df = run_query()
        _df.to_csv(DATA_PATH, index=False)
    else:
        _df = pd.read_csv(DATA_PATH)
    _df = _df[_df['st_teff'] < max_teff]
    _df = _df[_df['sy_dist'] < max_dist]
    _df = apply_corrections(_df, max_period, max_mass, max_insolation)
    return _df
    
    


def main(
    max_teff: int,
    max_dist: float,
    max_period: float,
    max_mass: float,
    max_insolation: float,
    size: float,
    alpha: float,
    target_list: str,
    method: str,
)-> go.Figure:
    """
    Make the figure with the given parameters.
    
    Parameters
    ----------
    max_teff : int
        The maximum effective temperature in K
    max_dist : float
        The maximum distance in parsecs
    max_period : float
        The maximum orbital period
    max_mass : float
        The maximum planet mass
    max_insolation : float
        The maximum insolation
    size : float
        A scalar for the marker size.
    alpha : float
        The transparency of the markers
    target_list : str
        'mirecle', 'hwo', or 'none'
    method : str
        How to decide on marker colors. 'transit' to separate them into
        transiting and non-transiting planets. 'teff' to color by stellar
        effective temperature.
    
    Returns
    -------
    go.Figure
        The plotly figure.
    """
    
    def get_size(mass: float):
        """
        Determine marker size based on the planet's mass

        Parameters
        ----------
        mass : float
            The planet's mass relative to Earth.

        Returns
        -------
        float
            The marker size.
        """
        k = 20*size  # scales size of markers
        return k*mass
    
    _df = get_df(
        max_dist=max_dist,
        max_teff=max_teff,
        max_period=max_period,
        max_mass=max_mass,
        max_insolation=max_insolation,
    )
    is_transit = _df['tran_flag'].values.astype('bool')
    x_kw = 'sy_dist'
    y_kw = 'pl_approx_insol'
    c_kw = 'st_teff'
    hover_kw = ['pl_name','st_teff','pl_orbper','pl_bmasse','pl_eqt']
    size_kw = 'pl_bmasse'
    
    # fig = go.Figure()
    fig = make_subplots(rows=1, cols=1,
                        specs=[[{"secondary_y": False}]],  # Single primary y-axis
                        # inset_titles=["Inset Plot"]  # Add an inset title (optional)

                        )
    if method == 'transit':
        fig.add_trace(
            go.Scatter(
                x=_df.loc[is_transit,x_kw],
                y=_df.loc[is_transit,y_kw],
                mode='markers',
                name = 'Transiting',
                customdata=_df.loc[is_transit,hover_kw],
                marker=dict(
                size=get_size(_df.loc[is_transit,size_kw]),
                sizemode=SIZEMODE,
                color=f'#{TRANSIT_COLOR}',
                opacity=alpha,
                symbol='circle',
                line=dict(
                    color=LINE_COLOR,
                    width=1
                ),
            ),
            hovertemplate = 
            "<b>%{customdata[0]}</b><br>" +
            "Insol: %{y:.2f} <br>" +
            "Dist: %{x:.2f} pc<br>" +
            "Teff: %{customdata[1]:.0f} K<br>" +
            "Period: %{customdata[2]:.1f} days<br>" +
            "Mass: %{customdata[3]:.1f} M_earth<br>"+
            "Teq: %{customdata[4]:.0f} K<br>" +
            "<extra></extra>"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=_df.loc[~is_transit,x_kw],
                y=_df.loc[~is_transit,y_kw],
                mode='markers',
                name = 'Non-Transiting',
                customdata=_df.loc[~is_transit,hover_kw],
                marker=dict(
                size=get_size(_df.loc[~is_transit,size_kw]),
                sizemode=SIZEMODE,
                color=f'#{NONTRANSIT_COLOR}',
                opacity=alpha,
                symbol='circle',
                line=dict(
                    color=LINE_COLOR,
                    width=1
                ),
            ),
            hovertemplate = 
            "<b>%{customdata[0]}</b><br>" +
            "Insol: %{y:.2f} <br>" +
            "Dist: %{x:.2f} pc<br>" +
            "Teff: %{customdata[1]:.0f} K<br>" +
            "Period: %{customdata[2]:.1f} days<br>" +
            "Mass: %{customdata[3]:.1f} M_earth<br>"+
            "Teq: %{customdata[4]:.0f} K<br>" +
            "<extra></extra>"
            )
        )
    elif method == 'teff':
        fig.add_trace(
            go.Scatter(
                x=_df.loc[:,x_kw],
                y=_df.loc[:,y_kw],
                mode='markers',
                name = 'Planets',
                showlegend=False,
                customdata=_df.loc[:,hover_kw],
                marker=dict(
                    size=get_size(_df.loc[:,size_kw]),
                    sizemode=SIZEMODE,
                    color=_df.loc[:,c_kw],
                    colorscale='cividis',
                    opacity=alpha,
                    symbol='circle',
                    line=dict(
                        color=LINE_COLOR,
                        width=1
                    ),
                    colorbar = dict(
                        title='Teff (K)',
                        titlefont=dict(
                            color='black',
                            size=20
                        ),
                        tickfont=dict(
                            color='black',
                            size=18
                        )
                    )
                ),
                hovertemplate = 
                "<b>%{customdata[0]}</b><br>" +
                "Insol: %{y:.2f} <br>" +
                "Dist: %{x:.2f} pc<br>" +
                "Teff: %{customdata[1]:.0f} K<br>" +
                "Period: %{customdata[2]:.1f} days<br>" +
                "Mass: %{customdata[3]:.1f} M_earth<br>"+
                "Teq: %{customdata[4]:.0f} K<br>" +
                "<extra></extra>",
            )
        )
    
    fig.update_layout(
        shapes = [
            dict(
                type='rect',
                x0=0.93*max_dist,
                y0=0.625,
                x1=0.97*max_dist,
                y1=1.75,
                line=dict(color="black", width=2),  # Border color and width
                fillcolor=None,              # Fill color
                opacity=0.4                           # Transparency
            ),
            dict(
                type='line',
                x0=0,x1=1,xref='paper',
                y0=(1/A_VENUS**2), y1=(1/A_VENUS**2),
                line=dict(
                    color='black',
                    width=2,dash='dash'
                )
            ),
            dict(
                type='line',
                x0=0,x1=1,xref='paper',
                y0=(1/A_MARS**2), y1=(1/A_MARS**2),
                line=dict(
                    color='black',
                    width=2,dash='dash'
                )
            )
        ],
        annotations = [
            dict(
            x=0.95*max_dist,
            y=np.log10(1/A_VENUS**2),
            xref='x',
            yref='y',
            yanchor='bottom',
            text="Mass Key",
            showarrow=False,
            font=dict(
                color='black',
                size=20,
            ),
            align='center'
        ),
            dict(
                x = 0.01,
                y= np.log10(1/A_VENUS**2),
                xref='paper',
                yref='y',
                text="Venus",
                xanchor='left',
                yanchor='top',
                font=dict(
                    color='black',
                    size=20
                )
            ),
            dict(
                x = 0.01,
                y= np.log10(1/A_MARS**2),
                xref='paper',
                yref='y',
                text="Mars",
                xanchor='left',
                yanchor='top',
                font=dict(
                    color='black',
                    size=20
                )
            ),
            dict(
                x = 0.01,
                y=-0.01,
                xref='paper',
                yref='paper',
                text="Data from NExScI, Figure by Ted Johnson (UNLV, GSFC)",
                xanchor='left',
                yanchor='top',
                font=dict(
                    color='black',
                    size=16
                )
            )
            ]
    )
    
    if target_list == 'none':
        pass
    elif target_list == 'mirecle':
        mirecle_target_list = get_mirecle_targets()
        in_mirecle = _df.loc[:, 'pl_name'].isin(mirecle_target_list['name'])
        fig.add_trace(
            go.Scatter(
                x=_df.loc[in_mirecle, x_kw],
                y=_df.loc[in_mirecle, y_kw],
                mode='markers',
                name='MIRECLE Targets',
                hoverinfo='skip',
                marker=dict(
                    size=get_size(_df.loc[in_mirecle, size_kw]),
                    sizemode=SIZEMODE,
                    color='black',
                    opacity=1,
                    symbol='circle-open',
                    line=dict(
                        color=LINE_COLOR,
                        width=2
                    )
                )
            )
        )
    elif target_list == 'hwo':
        hwo_target_list = get_hwo_targets()
        in_hwo = (
            _df.loc[:, 'hip_name'].isin(hwo_target_list['ID(HIP)'])
            | _df.loc[:, 'hd_name'].isin(hwo_target_list['ID(HD)'])
            | _df.loc[:, 'hostname'].isin(hwo_target_list['Common Name'])
        )
        fig.add_trace(
            go.Scatter(
                x=_df.loc[in_hwo, x_kw],
                y=_df.loc[in_hwo, y_kw],
                mode='markers',
                name='HWO Targets',
                hoverinfo='skip',
                marker=dict(
                    size=get_size(_df.loc[in_hwo, size_kw]),
                    sizemode=SIZEMODE,
                    color='black',
                    opacity=1,
                    symbol='circle-open',
                    line=dict(
                        color=LINE_COLOR,
                        width=2
                    )
                )
            )
        )
    else:
        raise ValueError('Please choose a valid target list.')
    
    
    fig.add_trace(
        go.Scatter(
            x=[0.95*max_dist],
            y=[0.75],
            mode='markers',
            name='Mars-mass',
            showlegend=False,
            marker=dict(
                size=[get_size(0.107)],
                sizemode=SIZEMODE,
                color='black',
                opacity=alpha,
                symbol='circle',
                line=dict(
                    color=LINE_COLOR,
                    width=1
                )
            ),
            hovertemplate =
            "Mars-mass: 0.1 M_earth<extra></extra>"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0.95*max_dist],
            y=[1],
            mode='markers',
            name='Earth-mass',
            showlegend=False,
            marker=dict(
                size=[get_size(1.0)],
                sizemode=SIZEMODE,
                color='black',
                opacity=alpha,
                symbol='circle',
                line=dict(
                    color=LINE_COLOR,
                    width=1
                )
            ),
            hovertemplate =
            "Earth-mass<extra></extra>"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0.95*max_dist],
            y=[1.5],
            mode='markers',
            name='Neptune-mass',
            showlegend=False,
            marker=dict(
                size=[get_size(17.15)],
                sizemode=SIZEMODE,
                color='black',
                opacity=alpha,
                symbol='circle',
                line=dict(
                    color=LINE_COLOR,
                    width=1
                )
            ),
            hovertemplate =
            "Neptune-mass: 17 M_earth<extra></extra>"
        )
    )
    fig.update_layout(
        yaxis_type='log',
        xaxis_title='Distance (pc)',
        yaxis_title='Stellar Insolation Flux\n(relative to Earth)',
        xaxis_title_font_size=24,
        xaxis_title_font_family='serif',
        xaxis_tickfont_size=20,
        yaxis_title_font_size=24,
        yaxis_title_font_family='serif',
        yaxis_tickfont_size=20,
        # xaxis=dict(
        #     range=[0,max_dist],
        # ),
        # yaxis=dict(
        #     range=[-1,2.1],
        # ),
        # showlegend=method == 'transit',
        legend=dict(
            x=0.9,
            y=0.1,
            xanchor='right',
            yanchor='bottom',
            itemsizing="trace",
            tracegroupgap=30,
            font=dict(
                size=28,
                color='black'
            ),
        )
    )
    return fig


if __name__ == '__main__':
    fig = main(
        max_teff=4000,
        max_dist=20,
        max_insolation=20,
        max_period=20,
        max_mass=20,
        size=1,
        alpha=0.5,
        target_list='mirecle',
        method='transit',
    )
    fig.show()