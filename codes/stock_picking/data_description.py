from codes.dependencies import *
from codes.stock_picking.pre_process import get_tables
from codes.stock_picking.stock_picking import stock_picker
from codes.tools.OutputWriter import OutputWriter
from codes.stock_picking.ReturnSeries import ReturnSeries
from codes.tools.PlotClasses import MatrixPlot
from codes.tools.PlotClasses import SinglePlot


def pick_companies(plot_all=False, plot_picked=False, save_output=False):
    """
    pick companies picks companies from all the stocks in data/raw_companies retrieved from yahoo finance, it also saves
     the picked companies to excel file
    :param plot_all: if True plots correlation matrix for all stocks
    :param plot_picked: if True plots correlation matrix for selected stocks
    :param save_output: if True saves the output to excel file
    :return: picked companies as pandas file
    """
    names = stock_picker()  # names are generated
    (bonds, indices, companies) = get_tables()
    if plot_all:
        mp = MatrixPlot(companies.corr(), "correlation matrix of all the stocks")
        mp.save("output/misc_visuals/all_matrix.png")
    picked_companies = companies[names]
    if plot_picked:
        mp = MatrixPlot(companies.corr(), "correlation matrix of the picked stocks")
        mp.save("output/misc_visuals/picked_matrix.png")
    for i in indices:
        key = i.keys()[0]
        picked_companies[key] = i[key]
    #picked_companies["NQ=F"] = indices[]nasdaq100["NQ=F"]
    picked_companies["DGS1MO"] = bonds["DGS1MO"]
    if save_output:
        ow = OutputWriter("output/sheet_pages/Part1_raw_data.xlsx")
        ow.write(df=picked_companies)
    return picked_companies


def save_returns(save_outputs=False):
    """
    Saves the returns to excel file after computing for stocks bonds and described portfolios
    :param save_outputs: if true, output is also saved
    :return: the selected returns as pandas file
    """
    comps = pd.read_excel("output/sheet_pages/Part1_raw_data.xlsx", index_col="Date")
    returns = pd.DataFrame(index=comps.index)
    for i in comps.keys():
        if i == "DGS1MO":
            returns[i] = ReturnSeries.returns_calculator("Bond", comps["DGS1MO"])
        else:
            returns[i] = ReturnSeries.returns_calculator("Stock", comps[i].array)
    stocks = returns[returns.keys()[:10]]
    returns["EQWP"] = stocks.dot(np.ones(10) / 10)

    # market cap 27/06/2021
    # AAPL: 2.221T, AKAM: 19.062B, BKNG: 93.669B, GILD: 85.134B, ILMN: 69.3B, MNST: 48.691B, NFLX: 233.704B,
    # NTES: 72.815B, VRTX: 50.308B, XEL: 36.114B
    weights = [2221, 19.062, 93.669, 85.134, 69.3, 48.691, 233.704, 72.815, 50.308, 36.114]
    nw = np.array(weights)
    norm_w = nw / np.sum(nw)
    returns["MCWP"] = stocks.dot(norm_w)
    if save_outputs:
        ow = OutputWriter("output/sheet_pages/Part2_returns.xlsx")
        ow.write(df=returns)
    return returns


def data_descriptive_plots(returns=None, time_series=False, histograms=False, box_plot=False, qq_plot=False, density_plot=False):
    """
    This is a function that plots and saves from calculated returns, it reads from the relevant excel file
    :param returns: pandas object for returns, if None, relevant excel file is read
    :param time_series: if True time series plots are plotted an saved
    :param histograms: if True histograms are plotted an saved
    :param box_plot: if True box plot is plotted an saved
    :param qq_plot: if True qq plots are plotted and saved
    :param density_plot: if True density plots are plotted and saved
    """
    if returns is None:
        returns = pd.read_excel("output/sheet_pages/Part2_returns.xlsx", index_col="Date")
    if time_series:
        for key in returns.keys():
            sp = SinglePlot(title="r_t of " + key, legend=True, xlabel="r_t", ylabel="time")
            sp.plot_line_xy(returns.index, y=returns[key], legend="time series")
            axis = np.arange(len(returns[key]))
            p = np.poly1d(np.polyfit(axis, returns[key], 1))
            sp.plot_line_xy(returns.index, p(axis), linestyle="--", legend="linear trend")
            sp.save("output/data_description/time_series/ts_"+key+".png")

    radius = 0
    for key in returns.keys():
        n_min = abs(np.min(returns[key]))
        n_max = abs(np.max(returns[key]))
        if n_min > radius:
            radius = n_min
        if n_max > radius:
            radius = n_max
    radius += 0.1
    if histograms:

        ax = np.arange(-radius, radius, 0.01)

        for key in returns.keys():
            plt.hist(returns[key], ax)  # hist
            plt.grid(True)
            plt.title("histogram of " + key)
            plt.xlabel("return bins of 0.01 width")
            plt.ylabel("samples")
            MatrixPlot.ensure_dir("output/data_description/histograms/hist_"+key+".png")
            plt.savefig("output/data_description/histograms/hist_"+key+".png")
            plt.close()

    if density_plot:
        for key in returns.keys():
            returns[key].plot(kind='density')  # density plot
            plt.grid(True)
            plt.title("density plot of " + key)
            plt.xlabel("return value")
            MatrixPlot.ensure_dir("output/data_description/density/dense_" + key + ".png")
            plt.savefig("output/data_description/density/dense_" + key + ".png")

            plt.close()

    if qq_plot:
        for key in returns.keys():
            probplot(returns[key], dist="norm", plot=plt)
            plt.title("Q-Q Plot for "+key)
            plt.grid()
            MatrixPlot.ensure_dir("output/data_description/qq_plot/qq_" + key + ".png")
            plt.savefig("output/data_description/qq_plot/qq_" + key + ".png")
            plt.close()

    if box_plot:
        returns.boxplot(figsize=(12, 6))  # boxplot
        plt.title("boxplot")
        MatrixPlot.ensure_dir("output/data_description/box_plot.png")
        plt.savefig("output/data_description/box_plot.png")
        plt.close()
