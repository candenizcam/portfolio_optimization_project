from codes.dependencies import *
from codes.stock_picking.data_description import pick_companies, save_returns, data_descriptive_plots
from codes.tools.OutputWriter import OutputWriter
from codes.return_database.data_summary import data_summary_calculations
from codes.market_model_and_CAPM.mm_calculations import mm_calculations
from codes.market_model_and_CAPM.capm_calculations import capm_calculations
from codes.portfolio_performance.portfolio_performance_calculations import portfolio_performance_calculations
from codes.portfolio_operations.calculations import portfolio_operations_calculations

if __name__ == '__main__':
    # stock picking
    #p1_sheet = pick_companies(plot_all=True, plot_picked=True, save_output=True)
    #
    #returns = save_returns(save_outputs=True)
    #
    # data_descriptive_plots(time_series=True, histograms=True, box_plot=True, density_plot=True, qq_plot=True)  # plots

    # part 3
    data_summary_calculations(True, True, True, True)

    # part 4
    portfolio_operations_calculations(save_plots=True, save_tables=True)

    # part 5
    mm_calculations(scatter_plots=True, save_table=True)

    # part 6
    capm_calculations(scatter_plots=True, save_table=True, save_market_line=True)

    # part 7
    portfolio_performance_calculations(save_table=True, save_cumulative_table=True, save_cumulative_plot=True)

    merge_outputs = True
    if merge_outputs:
        pages_list = os.listdir("output/sheet_pages")
        ow = OutputWriter("output/project_spreadsheet.xlsx")
        for i in pages_list:
            s = pd.read_excel("output/sheet_pages/" + i, index_col=0)
            ow.write(df=s, sheet_name=i.split(".")[0])
