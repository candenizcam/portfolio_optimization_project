from codes.dependencies import *
from codes.tools.OutputWriter import OutputWriter
from codes.tools.PlotClasses import SinglePlot
from codes.return_database.ReturnDataBase import ReturnDataBase
from codes.market_model_and_CAPM.SingleRegression import CAPMRegression


def capm_calculations(scatter_plots=False, save_table=False, save_market_line=False):
    """
    Does the calculations for part 6
    :param save_market_line: if true market line plot is saved
    :param scatter_plots: if true plots are recorded, not necessary for the project but is kept for users' convenience
    :param save_table: if true a table of regression results is recorded
    """
    rdb = ReturnDataBase(market="NQ=F")  # data base is initialized with NQ=F as market index

    index_array = rdb.get_market_returns().values.__array__()  # market index and risk free values are pulled
    rf_array = rdb.get_risk_free().values.__array__()

    # portfolios
    tp_with_shorts_weights = [0.215268283, -0.01422516, 0.061780474, 0.062071129, 0.073160682, 0.151843787, 0.048849873,
                              0.076326502, -0.037283025, 0.362207455]
    tp_without_shorts_weights = [0.206561131, 0, 0.059446747, 0.054590921, 0.065540249, 0.146906494, 0.043464515,
                                 0.070455068, 6.64074E-18, 0.353034875]
    ewp = (np.ones(10) / 10).tolist()  # equally weighted

    arrays_1 = [(i.key, i.values.__array__()) for i in rdb.get_stocks()]  # stock value arrays
    tp_short_array = ("TP", np.sum([arrays_1[x][1] * i for x, i in enumerate(tp_with_shorts_weights)], 0))
    tp_without_short_array = ("TPWS", np.sum([arrays_1[x][1] * i for x, i in enumerate(tp_without_shorts_weights)], 0))
    ewp_array = ("EWP", np.sum([arrays_1[x][1] * i for x, i in enumerate(ewp)], 0))
    arrays_1 += [tp_short_array, tp_without_short_array, ewp_array]  # portfolio arrays are merged

    if save_market_line:  # first part of market line plot, plots the line across beta=0,2, can be changed on code
        market_plot = SinglePlot(legend=True, title="SML plot", xlabel="expected returns", ylabel="β")
        rfm = np.mean(rf_array)
        em = rfm + 0 * (np.mean(index_array) - rfm)
        ex = rfm + 2 * (np.mean(index_array) - rfm)
        market_plot.plot_line_xy([em, ex], [0, 2], legend="SML")

    pd_list = []
    plot_pairs = []
    for x, i in enumerate(arrays_1):
        sr = CAPMRegression(index_array - rf_array, i[1] - rf_array)
        plot_pairs.append((sr.mean_y2, sr.beta_1))
        d = sr.get_dict()
        pd_list.append(pd.DataFrame(d.values(), index=d.keys(), columns=[i[0]]))
        if scatter_plots:
            sp = SinglePlot(legend=True, title=i[0] + " CAPM regression plot", xlabel="index returns",
                            ylabel=i[0] + " returns", ylim=(-1, 1))
            sp.scatter_xy(sr.x, sr.y, color="blue", legend="data")
            sp.plot_line_xy(sr.x, sr.y_hat, color="red", legend="regression line")
            sp.save("output/capm_regressions/" + i[0] + "_capm_regression.png")
        if save_market_line:  # market plot scatterings for TP with and without shorts
            if x == 10 or x == 9:
                market_plot.scatter_xy([sr.mean_y2], [sr.beta_1], legend=i[0] + "_half")  # chow results as demanded
                market_plot.scatter_xy([np.mean(sr.y)], [sr.beta], legend=i[0] + "_full")  # full regression as bonus

    if save_market_line:
        market_plot.save("output/misc_visuals/market_line.png")

    if save_table:
        merged = pd.concat(pd_list, 1)
        ow = OutputWriter("output/sheet_pages/Part6_capm_regression_results.xlsx")
        ow.write(df=merged, transpose=True)
