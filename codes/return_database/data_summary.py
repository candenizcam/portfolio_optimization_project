from codes.return_database.ReturnDataBase import ReturnDataBase


def data_summary_calculations(save_summary=False, save_cov=False, save_corr=False, save_VaR=False):
    """
    does the computations for part 3
    :param save_summary: saves summary stats table
    :param save_cov: saves covariance table
    :param save_corr: saves correlation table
    :param save_VaR: saves value at risk table
    """
    rdb = ReturnDataBase()
    if save_summary:
        rdb.get_summary_table(True)
    if save_cov:
        rdb.get_cov_table(True)
    if save_corr:
        rdb.get_corr_table(True)
    if save_VaR:  # 1$ = 8.6₺ at 1 June, 8.71₺ at 30 June
        rdb.get_VaR_table(100000, (8.6, 8.71), True)
