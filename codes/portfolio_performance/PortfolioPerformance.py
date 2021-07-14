from codes.dependencies import *


class PortfolioPerformance:
    def __init__(self, asset_returns, market_returns, risk_free_returns):
        """
        This class computes various asset performance metrics using returns of the asset, market and risk free asset
        :param asset_returns: a numpy array that is the r returns of an asset
        :param market_returns: r returns of a market index
        :param risk_free_returns: r returns of a risk free asset
        """
        self.asset_returns = asset_returns
        self.market_returns, self.risk_free_returns = market_returns, risk_free_returns
        # library linregress is used as it computes alpha_ste internally which is simpler
        r = linregress(self.market_returns - self.risk_free_returns, self.asset_returns - self.risk_free_returns)
        self.beta = r.slope
        self.alpha = r.intercept
        self.r_value = r.rvalue
        self.p_value = r.pvalue
        self.beta_ste = r.stderr
        self.alpha_ste = r.intercept_stderr
        self.alpha_low = self.alpha - 1.96 * r.intercept_stderr  # confidence intervals
        self.alpha_high = self.alpha + 1.96 * r.intercept_stderr

    def get_dict(self):
        """
        :return: dict of results for tables
        """
        n = dict()
        n["alpha"] = self.alpha
        n["alpha ste"] = self.alpha_ste
        n["alpha 95% low"] = self.alpha_low
        n["alpha 95% high"] = self.alpha_high
        n["95% test for positive alpha"] = self.alpha_low > 0
        return n
