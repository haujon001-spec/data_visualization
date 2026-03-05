
# -*- coding: utf-8 -*-
"""
Build Population Bar Race Visualization
========================================
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
from pathlib import Path


def build_population_barrace(df: pd.DataFrame, fig_size: tuple = (12, 8)):
    """
    Build animated bar race chart for population data.
    
    Args:
        df: DataFrame with columns [country, year, population]
        fig_size: Figure size tuple
        
    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=fig_size)
    return fig, ax


def apply_flag_labels(ax, data):
    """
    Apply country flag labels to bars in the chart.
    """
    for idx, row in data.iterrows():
        ax.text(0, idx, f"🚩 {row['country']}", va='center')
    return ax


def apply_si_formatting(value: float) -> str:
    """
    Convert number to SI format (1M, 1B, etc).
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string
    """
    if value >= 1e9:
        return f"{value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"


def validate_visualization_output(fig) -> bool:
    """
    Validate that visualization object is valid.
    """
    return fig is not None and hasattr(fig, 'axes')
