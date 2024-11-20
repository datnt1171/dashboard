import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from matplotlib.ticker import PercentFormatter

matplotlib.rcParams['font.family'] = ['SIMSUN','Times New Roman']

def plot_sales_order_target(df_fig, target_year, target_month):
    fig, ax1 = plt.subplots(figsize=(13, 6))

    width = 0.25  # Width of the bars
    x = np.arange(len(df_fig['month']))  # Label locations

    # Bars for sales and order quantities
    bars1 = ax1.bar(x - width/2, df_fig['sales_quantity'], width, 
                    label='年的每月送貨量 - Số lượng giao hàng mỗi tháng', color='#72BF78') #Sales Quantity
    bars2 = ax1.bar(x + width/2, df_fig['order_quantity'], width, 
                    label='年的每月訂單量 - Số lượng ĐĐH mỗi tháng', color='#7AB2D3') #Order Quantity

    # Stacked bars for timber
    bars3 = ax1.bar(x - width/2, df_fig['sales_quantity_timber'], width, bottom=df_fig['sales_quantity'], 
                    label='TIMBER每月的大森的送貨量 - SL giao hàng TIMBER', color='#C1FFC1') #Sales Quantity Timber
    bars4 = ax1.bar(x + width/2, df_fig['order_quantity_timber'], width, bottom=df_fig['order_quantity'], 
                    label='TIMBER每月的大森的訂單量 - SL ĐĐH TIMBER', color='#DFF2EB') #Order Quantity Timber

    # Labels and title
    ax1.set_xlabel('月 - Tháng') #Month
    ax1.set_ylabel('數量 - Số lượng') #Quantity
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_fig['month'])


    # Create a secondary y-axis
    ax2 = ax1.twinx()

    # Line plots for target percentages
    ax2.plot(x, df_fig['order_target%'], color='red', marker='o',
             label=f'相較{target_year}年{target_month}月訂單達成% - ĐĐH đạt % so với tháng {target_month}')
    ax2.plot(x, df_fig['sales_target%'], color='orange', marker='o',
             label=f'相較{target_year}年{target_month}月送貨達成% - Giao hàng đạt % so với tháng {target_month}')

    # Set secondary axis label and format ticks as percentage
    ax2.set_ylabel('Target %')
    ax2.yaxis.set_major_formatter(PercentFormatter(xmax=1))  # xmax=1 assumes that target percentages are in decimal format (e.g., 0.5 for 50%)

    ax1.legend(loc='upper left', bbox_to_anchor=(0, 1.22), borderaxespad=0.)  # Top left outside
    ax2.legend(loc='upper left', bbox_to_anchor=(0.35, 1.115), borderaxespad=0.)  # Top left outside


    for i, value in enumerate(df_fig['order_target%']):
        ax2.annotate(f'{value*100:.1f}%', 
                    (x[i], df_fig['order_target%'][i]), 
                    textcoords="offset points", 
                    xytext=(0, 5), 
                    ha='left',
                    color='red',
                    fontsize=14,
                    fontweight='bold')

    for i, value in enumerate(df_fig['sales_target%']):
        ax2.annotate(f'{value*100:.1f}%',
                    (x[i], 
                    df_fig['sales_target%'][i]),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha='right',
                    color='black',
                    fontsize=14,
                    fontweight='bold')
        
    plt.tight_layout()

    # Save figure to buffer and encode it
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'
    
    return fig_bar_matplotlib