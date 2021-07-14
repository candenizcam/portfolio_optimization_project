from codes.dependencies import *
from codes.tools.PlotClasses import SinglePlot
from codes.portfolio_operations.Portfolio import EnhancedPortfolio
from codes.portfolio_operations.PortfolioOptimizer import PortfolioOptimizer


class PortfolioFrontier:
    def __init__(self, cov, er, betas, keys, rf, shorts):
        self.risky_portfolio_optimizer = PortfolioOptimizer(cov, er, betas, cov.keys(),rf)
        self.keys = list(keys) + ["DGS1MO"]
        self.N = cov.shape[0]
        self.shorts = shorts
        self.risk_free_return = rf
        self.gmvp = self.risky_portfolio_optimizer.optimize_portfolio(tag=("GMWS","GMVP")[shorts], weight_sum=1,shorts=shorts)
        self.mvp = self.risky_portfolio_optimizer.optimize_portfolio(tag=("MVPW","MVP")[shorts], weight_sum=1, er_target=0.031340474,shorts=shorts)
        self.tp = self.risky_portfolio_optimizer.tangency_portfolio(rf, shorts=shorts)
        self.risk_free_portfolio_optimizer = self._get_risk_free_optimizer()
        self.rf = self._get_rf()
        self.op = self._get_op()
        self.tp_rf = self.get_tp_rf()
        self.assets = self._get_asset_portfolios()

    def get_portfolio_frame(self, with_assets=True):
        portfolios = []
        if with_assets:
            portfolios += self.assets
        portfolios += self.important_portfolios()
        df_list = []
        for i in portfolios:
            i_dict = i.get_pt_dict(100000, (8.6, 8.71))
            df_list.append(pd.DataFrame(i_dict.values(), i_dict.keys(), [i.tag]))
        return pd.concat(df_list, 1)

    def important_portfolios(self):
        return [self.gmvp, self.mvp, self.tp, self.op]


    def _get_asset_portfolios(self):
        assets = []
        for x in range(self.N+1):
            w = np.zeros((self.N+1,1))
            w[x] = 1
            assets.append(self.risk_free_weights_portfolio(self.keys[x],w))
        return assets

    def get_tp_rf(self):
        w = np.zeros((self.N+1,1))
        w[:self.N] = self.tp.weights()
        return self.risk_free_weights_portfolio(("TP_RF", "TP_RF")[self.shorts], w)

    def risky_frontier(self,low_bound, up_bound, arange=None, lin_comb = True):
        if arange is None:
            arange = np.arange(low_bound, up_bound, 0.05)
        if lin_comb:
            a = [self.risky_weights_portfolio("RA="+str(round(i,2)), self.gmvp.weights()*(1-i) + self.mvp.weights()*i) for i in
                 arange]
            return [i for i in a if not i.invalid]
        else:
            a = [self.risky_portfolio_optimizer.optimize_portfolio("tag", 1, i, shorts=self.shorts) for i in
             arange]
            return [i for i in a if not i.invalid]

    def risk_free_frontier(self,low_bound, up_bound, lin_comb=True):
        if lin_comb:
            a = [self.risk_free_weights_portfolio("RFA=" + str(round(i,2)),
                                                  self.rf.weights() * (1 - i) + self.tp_rf.weights() * i) for i in
                 np.arange(low_bound, up_bound, 0.05)]
            return [i for i in a if not i.invalid]
        else:
            a = [self.risk_free_portfolio_optimizer.optimize_portfolio("tag", 1, i, shorts=self.shorts) for i in
                 np.arange(low_bound, up_bound, 0.01)]
            return [i for i in a if not i.invalid]

    def _risky_keys(self):
        return self.keys[:self.N]

    def _get_risk_free_optimizer(self):
        cov_r = np.zeros((self.N + 1, self.N + 1))
        cov_r[:, :] = 0.000001484
        cov_r[:self.N, :self.N] = self.risky_portfolio_optimizer.covariance_matrix
        er_rf = np.zeros((self.N + 1, 1))
        er_rf[:self.N] = self.risky_portfolio_optimizer.expected_returns
        er_rf[self.N] = self.risk_free_return
        betas_rf = np.zeros((self.N + 1, 1))
        betas_rf[:self.N] = self.risky_portfolio_optimizer.market_betas
        return PortfolioOptimizer(cov_r, er_rf, betas_rf, self.keys, self.risk_free_return)

    def _get_rf(self):
        """
        :return: risk free asset only portfolio
        """
        rf_w = np.zeros((self.N + 1, 1))
        rf_w[self.N] = 1
        return self.risk_free_weights_portfolio("RF", rf_w)

    def _get_op(self, alpha=1.45):
        """
        Gets op, or another alpha portfolio
        :param alpha: linear combination: tp*alpha + rf*(1-alpha)
        :return: op portfolio
        """
        tpr_w = np.zeros((self.N + 1, 1))
        tpr_w[:self.N] = self.tp.weights()
        rf_w = np.zeros((self.N + 1, 1))
        rf_w[self.N] = 1
        op_w = alpha * tpr_w + (1 - alpha) * rf_w
        return self.risk_free_weights_portfolio(("OPWS","OP")[self.shorts], op_w)

    def risky_weights_portfolio(self, tag, w):
        """
        This is a great wrapper for risky portfolio from weights
        :param tag: portfolio tag
        :param w: weights
        :return: EnhancedPortfolio
        """
        return EnhancedPortfolio(tag, w, self._risky_keys(), self.risky_portfolio_optimizer.expected_returns,
                                 self.risky_portfolio_optimizer.covariance_matrix,
                                 self.risky_portfolio_optimizer.market_betas,
                                 self.risky_portfolio_optimizer.risk_free_return )

    def risk_free_weights_portfolio(self, tag, w):
        """
        This is a great wrapper for risk free portfolio from weights
        :param tag: portfolio tag
        :param w: weights
        :return: EnhancedPortfolio
        """
        return EnhancedPortfolio(tag, w, self.keys, self.risk_free_portfolio_optimizer.expected_returns,
                                 self.risk_free_portfolio_optimizer.covariance_matrix,
                                 self.risk_free_portfolio_optimizer.market_betas,
                                 self.risk_free_portfolio_optimizer.risk_free_return)

    def plot_risky_frontier(self, alpha_down, alpha_up, calculated=False):
        sp = SinglePlot(title=("portfolio frontier without shorts", "portfolio frontier")[self.shorts], legend=True,
                   xlabel="stdev", ylabel="E(r)")

        rf = self.risky_frontier(alpha_down, alpha_up)
        std_list = [i.std for i in rf]
        er_list = [i.expected_return for i in rf]
        sp.plot_line_xy(std_list, er_list, "linear combined risky frontier")

        if calculated:
            rf = self.risky_frontier(np.min(er_list), np.max(er_list), lin_comb=False)
            std_list = [i.std for i in rf]
            er_list = [i.expected_return for i in rf]
            sp.plot_line_xy(std_list, er_list, "calculated risky frontier",linestyle="--")

        sp.plot_line_xy([self.gmvp.std], [self.gmvp.expected_return], self.gmvp.tag, marker="o")
        sp.plot_line_xy([self.mvp.std], [self.mvp.expected_return], self.mvp.tag, marker="o")
        sp.save("output/frontiers/risky_frontier" + ("_ws","")[self.shorts] + ".png")

    def plot_risk_free_frontier(self, alpha_down, alpha_up, calculated=False):
        sp = SinglePlot(title=("portfolio frontier without shorts", "portfolio frontier")[self.shorts], legend=True,
                        xlabel="stdev", ylabel="E(r)")

        rf = self.risky_frontier(alpha_down, alpha_up)
        std_list = [i.std for i in rf]
        er_list = [i.expected_return for i in rf]
        sp.plot_line_xy(std_list, er_list, "linear combined risky frontier")

        rff = self.risk_free_frontier(alpha_down, alpha_up)
        std_f_list = [i.std for i in rff]
        er_f_list = [i.expected_return for i in rff]
        sp.plot_line_xy(std_f_list, er_f_list, "linear combined risk free frontier")


        if calculated:
            rf = self.risky_frontier(np.min(er_list), np.max(er_list), lin_comb=False)
            std_list = [i.std for i in rf]
            er_list = [i.expected_return for i in rf]
            sp.plot_line_xy(std_list, er_list, "calculated risky frontier",linestyle="--")

            rff = self.risky_frontier(np.min(er_f_list), np.max(er_f_list), lin_comb=False)
            std_f_list = [i.std for i in rff]
            er_f_list = [i.expected_return for i in rff]
            sp.plot_line_xy(std_f_list, er_f_list, "calculated risk free frontier",linestyle="--")

        sp.plot_line_xy([self.gmvp.std], [self.gmvp.expected_return], self.gmvp.tag, marker="o")
        sp.plot_line_xy([self.mvp.std], [self.mvp.expected_return], self.mvp.tag, marker="o")
        sp.plot_line_xy([self.rf.std], [self.rf.expected_return], self.rf.tag, marker="o")
        sp.plot_line_xy([self.tp.std], [self.tp.expected_return], self.mvp.tag, marker="o")
        sp.save("output/frontiers/risk_free_frontier" + ("_ws","")[self.shorts] + ".png")

    def plot_full_portfolio(self, alpha_down, alpha_up):
        sp = SinglePlot(title=("portfolio frontier with portfolios", "portfolio frontier")[self.shorts], legend=True,
                        xlabel="stdev", ylabel="E(r)")

        rf = self.risky_frontier(alpha_down, alpha_up)
        std_list = [i.std for i in rf]
        er_list = [i.expected_return for i in rf]
        sp.plot_line_xy(std_list, er_list, "linear combined risky frontier")

        rff = self.risk_free_frontier(alpha_down, alpha_up)
        std_f_list = [i.std for i in rff]
        er_f_list = [i.expected_return for i in rff]
        sp.plot_line_xy(std_f_list, er_f_list, "linear combined risk free frontier")

        sp.plot_line_xy([self.gmvp.std], [self.gmvp.expected_return], self.gmvp.tag, marker="o")
        sp.plot_line_xy([self.mvp.std], [self.mvp.expected_return], self.mvp.tag, marker="o")
        sp.plot_line_xy([self.rf.std], [self.rf.expected_return], self.rf.tag, marker="o")
        sp.plot_line_xy([self.tp.std], [self.tp.expected_return], self.mvp.tag, marker="o")
        sp.plot_line_xy([0.0762], [0.0313], "MVP", marker="o")
        sp.plot_line_xy([0.0447], [0.0115], "NQ=F", marker="o")
        sp.plot_line_xy([self.op.std], [self.op.expected_return], "OP", marker="o")
        sp.save("output/frontiers/full_frontier" + ("_ws","")[self.shorts] + ".png")



