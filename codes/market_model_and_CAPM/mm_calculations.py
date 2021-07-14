from codes.dependencies import *
from codes.tools.OutputWriter import OutputWriter
from codes.tools.PlotClasses import SinglePlot
from codes.return_database.ReturnDataBase import ReturnDataBase
from codes.market_model_and_CAPM.SingleRegression import SingleRegression


def mm_calculations(scatter_plots=False, save_table=False):
    """
    Does the calculations for part 5
    :param scatter_plots: if true plots are recorded
    :param save_table: if true table is recorded
    :return:
    """
    rdb = ReturnDataBase(market="NQ=F")

    proxy_index = rdb.get_market_returns()

    index_array = proxy_index.values.__array__()

    pd_list = []
    for i in rdb.get_stocks():
        sr = SingleRegression(index_array, i.values.__array__())
        d = sr.get_dict()
        pd_list.append(pd.DataFrame(d.values(), index=d.keys(), columns=[i.key]))
        if scatter_plots:
            sp = SinglePlot(legend=True, title=i.key + " regression plot", xlabel="index returns",
                            ylabel=i.key + " returns", ylim=(-1, 1))
            sp.scatter_xy(sr.x, sr.y, color="blue", legend="data")
            sp.plot_line_xy(sr.x, sr.y_hat, color="red", legend="regression line")
            sp.save("output/regression_plots/" + i.key + "_regression.png")

    if save_table:
        concated = pd.concat(pd_list, 1)
        ow = OutputWriter("output/sheet_pages/Part5_regression_results.xlsx")
        ow.write(df=concated, transpose=True)
