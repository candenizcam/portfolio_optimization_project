from codes.dependencies import *
from codes.portfolio_performance.PortfolioPerformance import PortfolioPerformance
from codes.return_database.ReturnDataBase import ReturnDataBase
from codes.tools.OutputWriter import OutputWriter
from codes.tools.PlotClasses import SinglePlot


def portfolio_performance_calculations(save_table=False, save_cumulative_table=False, save_cumulative_plot=False):
    rdb = ReturnDataBase(market="NQ=F")  # database is initialized with NQ=F as market
    arrays_1 = [(i.key, i.values.__array__()) for i in rdb.get_stocks()]  # stock return arrays are pulled
    tp_with_shorts = [0.215268283, -0.01422516, 0.061780474, 0.062071129, 0.073160682, 0.151843787, 0.048849873,
                      0.076326502, -0.037283025, 0.362207455]  # short selling tangential portfolio weights
    tp_array = ("TP", np.sum([tp_with_shorts[x] * i.values.__array__() for x, i in enumerate(rdb.get_stocks())], 0))
    ewp = (np.ones(10) / 10).tolist()  # equally weighted weights
    ewp_array = ("EWP", np.sum([ewp[x] * i.values.__array__() for x, i in enumerate(rdb.get_stocks())], 0))
    op = [0.31213901, -0.020626482, 0.089581687, 0.090003137, 0.106082989, 0.220173492, 0.070832315, 0.110673428,
          -0.054060387, 0.52520081, -0.45]  # op weights
    op_array = (
        "OP", np.sum([op[x] * i.values.__array__() for x, i in enumerate(rdb.get_stocks() + [rdb.get_risk_free()])], 0))

    arrays_1 += [tp_array, ewp_array, op_array]  # arrays added to array list
    pd_list = []
    for x, i in enumerate(arrays_1):  # Jensen's alpha calculations
        sr = PortfolioPerformance(i[1], rdb.get_market_returns().values, rdb.get_risk_free().values)
        d = sr.get_dict()
        pd_list.append(pd.DataFrame(d.values(), index=d.keys(), columns=[i[0]]))

    if save_table:  # table is recorded
        merged = pd.concat(pd_list, 1)
        ow = OutputWriter("output/sheet_pages/Part7_portfolio_performance.xlsx")
        ow.write(df=merged, transpose=True)

    # cumulative calculations
    if save_cumulative_table:
        t = []
        if save_cumulative_plot:  # cumulative plot is done in three parts, this is where it is initialized
            cumulative_plot = SinglePlot(legend=True, title="Cumulative returns over time", xlabel="date",
                                         ylabel="Cumulative Returns")
        # compound returns are calculated by multiplying each new member with the oldest cumulative and a new return
        for x, i in enumerate(
                [("NQ=F", rdb.get_market_returns().values), ("DGS1MO", rdb.get_risk_free().values)] + arrays_1):
            compound_returns = i[1] + 1
            c = [compound_returns[0] * 10000]
            for y in range(len(compound_returns) - 1):
                c.append(c[-1] * compound_returns[y + 1])
            t.append(pd.DataFrame(np.array(c), index=rdb.get_risk_free().index, columns=[i[0]]))
            if save_cumulative_plot:  # this is where cumulative plot is drawn
                if x < 3 or x > 11:
                    cumulative_plot.plot_line_xy(rdb.get_risk_free().index, np.array(c), legend=i[0])
        if save_cumulative_plot:  # this is where it is recorded
            cumulative_plot.save("output/misc_visuals/cumulative_returns.png")
        # table is saved
        merged = pd.concat(t, 1)
        ow = OutputWriter("output/sheet_pages/Part7_portfolio_cumulative.xlsx")
        ow.write(df=merged)
