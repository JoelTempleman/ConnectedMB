
#statistical libs
import scipy
from sklearn.utils import resample

#additional plotly modules
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

#from statsmodels.graphics.gofplots import qqplot
import matplotlib.pyplot as plt

from data_exploration import *

def qq_plot(x, axes = None,device_number=1):
    if axes is None:
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        ax1 = axes
    p = scipy.stats.probplot(x, plot = ax1)
    ax1.set_xlim(-3, 3)
    ax1.set_title("QQ plot for device"+str(device_number))
    return p

def dist_subplots(dataframe,title,device_numbers,plot_value,num_cols=4):
    num_cols=4
    num_rows=int(len(device_numbers)/num_cols)+1
    i=1
    j=1
    subplot_t = []
    for device in device_numbers:
        subplot_t.append("device "+str(device))
    fig = make_subplots(rows=num_rows, cols=num_cols,subplot_titles=tuple(subplot_t))
    for device in device_numbers:
        subset=dataframe[dataframe["SK_PI"]==device]
        #trace=go.Histogram(x=subset[plot_value],marker=dict(color=colors[device]))
        group_labels = ['device '+str(device)]
        hist_data = [subset[plot_value]]
        fig2=ff.create_distplot(hist_data,group_labels, bin_size=0.5, curve_type='normal',colors=[colors[device]])
        for trace in fig2['data']:
            fig.append_trace(trace, i, j)
#       fig.append_trace(trace, i, j)
        j=j+1
        if j>num_cols:
            j=1
            i=i+1
    fig['layout'].update(height=1000, width=1000, title=title)
    iplot(fig)
