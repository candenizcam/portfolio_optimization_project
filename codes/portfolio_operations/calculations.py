from codes.dependencies import *
from codes.tools.OutputWriter import OutputWriter
from codes.return_database.ReturnDataBase import ReturnDataBase
from codes.portfolio_operations.PortfolioFrontier import PortfolioFrontier


def portfolio_operations_calculations(save_plots=False, save_tables=False):
    """
    this function computes portfolio operations calculations, it is mostly a wrapper for various classes
    :param save_plots: saves plots for part 4
    :param save_tables: saves tables for part 4
    :return:
    """
    rdb = ReturnDataBase()
    rf = np.mean(rdb.get_risk_free().values)  # average risk free rate
    cov = rdb.get_cov_table()  # covariance table for stocks
    e_r = [i.mean for i in rdb.get_stocks()]  # mean of the stocks
    betas_list = [i.beta for i in rdb.get_stocks()]  # list of market betas
    betas = np.array([betas_list]).T
    er = np.array([e_r]).T

    # frontiers with and without shorts
    pf_shorts = PortfolioFrontier(cov, er, betas, cov.keys(), rf, True)
    pf_no_shorts = PortfolioFrontier(cov, er, betas, cov.keys(), rf, False)

    if save_plots:
        for i in pf_shorts.important_portfolios() + pf_no_shorts.important_portfolios():
            i.plot_bar(True)
        # PortfolioFrontier class comes with its own plotters, one only needs to call
        pf_shorts.plot_risky_frontier(-2, 2, True)
        pf_shorts.plot_risk_free_frontier(-2, 2, True)
        pf_shorts.plot_full_portfolio(-2, 2)

        pf_no_shorts.plot_risky_frontier(-2, 2, True)
        pf_no_shorts.plot_risk_free_frontier(-2, 2, True)
        pf_no_shorts.plot_full_portfolio(-2, 2)

    if save_tables:
        w_list = [(i.weights().flatten().tolist(), i.tag) for i in
                  pf_shorts.important_portfolios() + pf_no_shorts.important_portfolios() if not i.invalid]
        dfs = []
        for i in w_list:
            if len(i[0]) == 10:
                dfs.append(pd.DataFrame(i[0], list(cov.keys()), [i[1]]))
            else:
                dfs.append(pd.DataFrame(i[0], list(cov.keys()) + ["DGS1MO"], [i[1]]))
        ow = OutputWriter("output/sheet_pages/Part4_portfolio_weights.xlsx")
        ow.write(df=pd.concat(dfs, 1),transpose=True)

        ar = np.arange(-1, 1, 0.1)
        ar[ar == 0] = 0.01
        ps = pf_shorts.risky_frontier(-1, 1, arange=ar)
        alpha_list = []
        for i in ps:
            i_dict = i.get_pt_dict(100000, (8.6, 8.71))
            alpha_list.append(pd.DataFrame(i_dict.values(), i_dict.keys(), [i.tag]))
        af = pd.concat(alpha_list, 1)
        ow = OutputWriter("output/sheet_pages/Part4_linear_combined_portfolios.xlsx")
        ow.write(df=af, transpose=True)

    df = pd.concat([pf_shorts.get_portfolio_frame(), pf_no_shorts.get_portfolio_frame(False)], 1)
    if save_tables:
        ow = OutputWriter("output/sheet_pages/Part4_portfolio_table.xlsx")
        ow.write(df=df, transpose=True)
