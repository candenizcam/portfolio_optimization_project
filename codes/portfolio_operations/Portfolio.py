from codes.dependencies import *
from codes.tools.PlotClasses import BarPlot
from codes.return_database.ReturnDataBase import VaR


class Portfolio:
    def __init__(self, tag, w, keys, invalid):
        """
        data class for a portfolio
        :param w: weights as a list or 1d array
        :param keys: keys for weights
        :param invalid: if True, portfolio exists as placeholder and should be ignores
        """
        self.tag = tag
        self.w = w
        self.keys = keys
        self.invalid = invalid

    def plot_bar(self, save=False):
        bp = BarPlot(self.keys, self.w.flatten().tolist(), title="weights of " + self.tag)
        if save:
            bp.save("output/portfolios/" + self.tag + "_bar.png")
        return bp

    def weights(self):
        """
        :return: weights as a vector
        """
        return np.array(self.w).reshape(len(self.w), 1)


class EnhancedPortfolio(Portfolio):
    def __init__(self, tag, w, keys, expected_returns, covariance_matrix, asset_betas, rf, invalid=False):
        """
        This is the child of a plain portfolio it is more equipped to compute various of its traits
        :param tag: tag of the portfolio
        :param w: weights
        :param keys: keys of weights
        :param expected_returns: E(r) of assets
        :param covariance_matrix: covariance matrix of assets
        :param asset_betas: betas of assets
        :param rf: risk free return rate
        :param invalid: if True, portfolio exists as placeholder and should be ignores
        """
        super().__init__(tag, w, keys, invalid)
        self._expected_returns = expected_returns
        self._covariance_matrix = covariance_matrix
        self.expected_return = np.matmul(self._expected_returns.T, self.weights())[0, 0]
        self.std = (np.dot(self.weights().T, np.matmul(self._covariance_matrix, self.weights()))[0, 0]) ** 0.5
        self.var = (np.dot(self.weights().T, np.matmul(self._covariance_matrix, self.weights()))[0, 0])
        self.expected_return_annualized = self.expected_return * 12  # i retain my doubts
        self.std_annualized = self.std * (12 ** 0.5)
        self.perc_1_coef = VaR.perc_1(self.expected_return_annualized + 1, self.std_annualized)
        self.perc_5_coef = VaR.perc_5(self.expected_return_annualized + 1, self.std_annualized)
        self.asset_betas = asset_betas
        self.market_beta = np.matmul(asset_betas.T, self.weights()).flatten()[0]
        self.rf = rf
        self.capm_return = (1 - self.market_beta) * rf + self.market_beta * self.expected_return

    def get_pt_dict(self, investment, xr_pair=(1, 1)):
        xr_rate = xr_pair[1] / xr_pair[0]
        return {"E(r)": self.expected_return, "E(r) annualized": self.expected_return_annualized, "std(r)": self.std,
                "std(r) annualized": self.std_annualized, "1% VaR": self.perc_1_coef * investment * xr_rate,
                "5% VaR": self.perc_5_coef * investment * xr_rate, "market beta": self.market_beta,
                "capm return": self.capm_return
                }

    @staticmethod
    def enhance(p, expected_returns, covariance_matrix, asset_betas, rf, invalid=False):
        """
        this is a method that takes a Portfolio and retuns an EnhancedPortfolio
        :param p: portfolio
        :param expected_returns: E(r)_i of assets
        :param covariance_matrix: V
        :param asset_betas: betas of assets
        :param rf: risk free return rate
        :param invalid: if True, portfolio exists as placeholder and should be ignores
        :return: EnhancedVersion of plain Portfolio
        """
        if type(p) != Portfolio:
            raise AssertionError("this is not a Portfolio")
        return EnhancedPortfolio(p.tag, p.w, p.keys, expected_returns, covariance_matrix, asset_betas, rf, invalid)
