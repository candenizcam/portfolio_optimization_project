from codes.tools.OutputWriter import OutputWriter
from codes.dependencies import *


class ReturnDataBase:
    def __init__(self, returns_frame=None, file="output/sheet_pages/Part2_returns.xlsx", index_col="Date", risk_free = "DGS1MO", market="NQ=F"):
        if returns_frame is None:
            returns_frame = pd.read_excel(file, index_col=index_col)
        self._returns_frame = returns_frame  # this is for reference and should not be called
        self.risk_free_key = risk_free
        self.market_index_key = market
        self.return_data = [ReturnData(i, returns_frame.index, returns_frame[i].array, returns_frame[self.risk_free_key],
                                       returns_frame[self.market_index_key]) for i in returns_frame.keys()]
        self.table_keys = ["mean", "median", "maximum", "minimum", "std_dev", "skewness", "kurtosis", "cv", "obs_no"]

    def get_keys(self, keys):
        """
        Returns the items with matching keys
        :param keys: a list of keys
        :return: a list of ReturnData
        """
        return list(filter(lambda x: x.key in keys, self.return_data))

    def get_stocks(self):
        """shorthand for returning the list of stocks"""
        return self.get_keys(self._returns_frame.keys()[:10])

    def get_market_returns(self):
        return self.get_keys(self.market_index_key)[0]

    def get_risk_free(self):
        return self.get_keys(self.risk_free_key)[0]

    def get_characteristic_table(self):
        df = pd.concat([pd.DataFrame(rd.table_stats.values(), index=rd.table_stats.keys(), columns=[rd.key]) for rd in self.return_data], 1)
        return df.reindex(self.table_keys)

    def get_jarque_bera_table(self):
        return pd.concat([pd.DataFrame(rd.jarque_bera.values(), index=rd.jarque_bera.keys(), columns=[rd.key]) for rd in self.return_data], 1)

    def get_confidence_interval_table(self):
        return pd.concat([pd.DataFrame(rd.confidence_intervals.values(), index=rd.confidence_intervals.keys(), columns=[rd.key]) for rd in self.return_data], 1)

    def get_acf_table(self):
        """
        what acf is is, it is correlation with the series lagged to a value (chopped from sides, not rolled)
        :return:
        """
        return pd.concat(
            [pd.DataFrame(rd.acf_vals.values(), index=rd.acf_vals.keys(), columns=[rd.key]) for
             rd in self.return_data], 1)

    def get_sharpe_table(self):
        return pd.concat(
            [pd.DataFrame(rd.sharpe, ["sharpe ratio"], columns=[rd.key]) for
             rd in self.return_data], 1)

    def get_summary_table(self, save = False):
        t = pd.concat([self.get_characteristic_table(), self.get_jarque_bera_table(), self.get_confidence_interval_table(), self.get_acf_table(), self.get_sharpe_table()], 0)
        if save:
            ow = OutputWriter("output/sheet_pages/Part3_summary_stats.xlsx")
            ow.write(df=t,transpose=True)
        return t

    def get_cov_table(self, save = False):
        t = self.get_stock_returns_table().cov()
        if save:
            ow = OutputWriter("output/sheet_pages/Part3_covariance_table.xlsx")
            ow.write(df=t)
        return t

    def get_corr_table(self, save = False):
        t = self.get_stock_returns_table().corr()
        if save:
            ow = OutputWriter("output/sheet_pages/Part3_correlation_table.xlsx")
            ow.write(df=t)
        return t


    def get_returns_table(self, keys=None):
        if keys is None:
            return self._returns_frame
        else:
            return self._returns_frame[keys]

    def get_stock_returns_table(self):
        return self.get_returns_table(self._returns_frame.keys()[:10])

    def pairwise_scatter(self, save=False):
        keys = self._returns_frame.keys()
        pd.plotting.scatter_matrix(self._returns_frame[keys[:10]], alpha=0.5, figsize=(10, 10))
        if save:
            plt.savefig("output/scatter_pairwise.png")
            plt.close()

    def get_VaR_table(self, investment, XR_pair = (1,1), save=False):
        """
        this returns the basic VaR table for %5 and %1
        :param investment: entry investment in asset
        :param XR_pair: foreign exchange rate, (old, new), (1,1) if investment is made in domestic
        :return:
        """
        xr_rate = XR_pair[1]/XR_pair[0]
        var_table = pd.concat(
            [pd.DataFrame(rd.get_VaR(investment * xr_rate).values(), index=rd.get_VaR(investment * xr_rate).keys(),
                          columns=[rd.key]) for
             rd in self.get_stocks()], 1)
        if save:
            ow = OutputWriter("output/sheet_pages/Part3_VaR_table.xlsx")
            ow.write(df=var_table,transpose=True)
        return var_table







class ReturnData:
    def __init__(self, key, index, values, rf_values, market_index_values):
        """
        This is a very wordy looking class but its usage is completely bound by the one above so its fine
        :param key: key of the return series such as AAPL
        :param index: time index for the series
        :param values: values of the series
        :param rf_values: risk free values for sharpe calculation
        :param market_index_values: for market beta calculation
        """
        self.key = key
        self.index = index
        self.values = values
        self.mean = np.mean(self.values)
        self.std =  np.std(self.values)
        self.table_stats = {"mean": np.mean(self.values), "median": np.median(self.values),
                            "maximum": np.max(self.values), "minimum": np.min(self.values),
                            "std_dev": np.std(self.values), "skewness": skew(self.values),
                            "kurtosis": kurtosis(self.values), "obs_no": len(self.values)}
        self.table_stats["cv"] = self.table_stats["std_dev"] / self.table_stats["mean"]
        jb_value, p = jarque_bera(self.values)
        self.jarque_bera = {"JB": jb_value, "p": p, "is normal": p > 0.05}
        ml, mh = norm.interval(alpha=0.95, loc=np.mean(self.values), scale=sem(self.values))
        sl, sh = norm.interval(alpha=0.95, loc=np.std(self.values), scale=sem(self.values))
        self.confidence_intervals = {"mean higher": mh, "mean lower": ml, "mean band": mh-ml, "std higher": sh, "std lower": sl, "std band": sh-sl}
        acf_vals = acf(self.values, nlags=12, fft=False, alpha=0.05)
        self.acf_vals = {"1M lag correlation":acf_vals[0][1],"1M lag lower conf":acf_vals[1][1,0],"1M lag upper conf":acf_vals[1][1,1],"1M conf band":acf_vals[1][1,1]-acf_vals[1][1,0],
                         "6M lag correlation":acf_vals[0][6],"6M lag lower conf":acf_vals[1][6,0],"6M lag upper conf":acf_vals[1][6,1],"6M conf band":acf_vals[1][6,1]-acf_vals[1][6,0],
                         "12M lag correlation":acf_vals[0][12],"12M lag lower conf":acf_vals[1][12,0],"12M lag upper conf":acf_vals[1][12,1],"12M conf band":acf_vals[1][12,1]-acf_vals[1][12,0]}
        self.sharpe = np.mean(values-rf_values)/np.std(values)
        self.VaR_coeffs = VaR(self.values+1)# R must be sent

        vm = np.cov(values,market_index_values.array)
        self.beta = vm[0, 1]/vm[1, 1]


    def get_VaR(self, investment):
        return self.VaR_coeffs.get_VaR_dict(investment)


class VaR:
    def __init__(self, values, invest=1):
        """
        This is an even more spesific data class it only makes VaR computations
        :param values: values of the series as R
        :param invest: invested amount, wont be relevant untill get_VaR_dict but can be defined in advance
        """
        self.values = values # converts to R
        self.mean = np.mean(values)
        self.std = np.std(values)
        self.p1 = self.mean - self.std*2.33
        self.p5 = self.mean - self.std * 1.65
        self.invest = invest
        self.emp1 = np.sort(values)[int(len(values)*0.01)]
        self.emp5 = np.sort(values)[int(len(values) * 0.05)]

    @staticmethod
    def perc_1(mean, std):
        """
        :param mean: mean of R
        :param std: std of R
        :return: 1 percent VaR coeff, can be multiplied with investment
        """
        return mean - std * 2.33

    @staticmethod
    def perc_5(mean, std): # mean for R
        """
        :param mean: mean of R
        :param std: std of R
        :return: 5 percent VaR coeff, can be multiplied with investment
        """
        return mean - std * 1.65

    def get_VaR_dict(self, investment=None, B=20, ci=0.95):
        """
        this returns the VaR dict
        :param investment: invested amount
        :param B: number of bootstrap tests
        :param ci: confidence interval, if 0.95 means %5 is used and sample no is length*0.95
        :return: the dict
        """
        np.random.seed(5) # seed for bootstrapping
        if investment is None:
            investment = self.invest
        bt = self.bootstrap(B,ci,investment)
        cvar5 = VaR(self.values[self.values < self.p5], investment)
        empc5 = np.sort(self.values)[int(len(self.values) * 0.05 * 0.05)]
        return {"1% VaR": self.p1 * investment, "1% ste": bt[0],"1% emprical VaR": self.emp1*investment,
                "5% VaR": self.p5 * investment, "5% ste": bt[1],"5% emprical VaR": self.emp5*investment,
                "5% CVaR": cvar5.p5 * investment, "5% emprical CVaR": empc5*investment
                }

    def bootstrap(self, B=20, ci = 0.95, investment = None):
        if investment is None:
            investment = self.invest
        size = len(self.values)
        a = []
        for i in range(B):
            ind = np.random.randint(size, size=int(size*ci))
            bt = self.values[ind]*investment
            v = VaR(bt)
            a.append([v.p1, v.p5])
        btt = np.array(a)
        ste = np.std(btt, 0) / (B ** 0.5)
        return ste