from codes.dependencies import *
from codes.portfolio_operations.Portfolio import EnhancedPortfolio


class PortfolioOptimizer:
    def __init__(self, covariance_matrix, expected_returns, market_betas, asset_keys, rf):
        self.covariance_matrix = covariance_matrix
        self.expected_returns = expected_returns
        self.market_betas = market_betas
        self.asset_keys = asset_keys
        self.risk_free_return = rf

    def optimize_portfolio(self, tag, weight_sum=None, er_target=None, shorts=True):
        """
        this is a decorator class for optimization, returns a portfolio
        :param tag: tag of the portfolio
        :param weight_sum: if a number is given, it is used as the sum of weights
        :param er_target: if a number, used as target, if not given gmvp is calculated
        :param shorts: if False, short selling is not allowed
        :return: portfolio
        """
        er = self.expected_returns
        if er_target is None:
            er = None

        if shorts:
            w, success = self.with_shorts(self.covariance_matrix, weight_sum=weight_sum, expected_returns=er,
                                 er_target=er_target)
        else:
            w, success = self.without_shorts(self.covariance_matrix, weight_sum=weight_sum,
                                    expected_returns=er, er_target=er_target)
        return EnhancedPortfolio(tag, w, self.asset_keys, self.expected_returns, self.covariance_matrix,
                                 self.market_betas, self.risk_free_return,invalid=success)

    @staticmethod
    def with_shorts(V, weight_sum=None, expected_returns=None, er_target=0):
        """
        This does a general weight optimization for portfolio based on its inputs,
        WARNING! this function does not have a system that checks for invalid inputs, use at your own risk
        :param V: covarince matrix
        :param weight_sum: sum of weights, usually 1
        :param expected_returns: if given it will also impose a returns constraint
        :param er_target: target return, if none is given 0 is assumed as r, using r or R is users responsibility,
        would work either way but results may not make sense
        :return: weights
        """
        coef_number = V.shape[0]
        b = np.zeros((coef_number, 1))
        L = V
        if weight_sum is not None:
            lc = LinearConstraint(True, np.zeros((coef_number, 1)) + 1, weight_sum)
            L, b = lc.constrain(L, b)

        if expected_returns is not None:
            lc = LinearConstraint(True, expected_returns, er_target)
            L, b = lc.constrain(L, b)

        w = np.matmul(np.linalg.inv(L), b)
        return w[:coef_number], False

    @staticmethod
    def without_shorts(V, weight_sum=None, expected_returns=None, er_target=0):
        N = V.shape[0]
        bounds = [(0, np.inf) for i in range(N)]
        obj = lambda x: np.matmul(x.T, np.matmul(V, x))
        x0 = np.zeros((N, 1))
        lc_mat = []
        lc_up = []
        lc_down = []
        if weight_sum is not None:
            lc_up += [weight_sum]
            lc_down += [weight_sum]
            lc_mat += [np.ones(N).tolist()]

        if expected_returns is not None:
            lc_up += [er_target]
            lc_down += [er_target]
            lc_mat += [expected_returns.flatten().tolist()]

        if len(lc_up):
            lc = slc(lc_mat, lc_down, lc_up)
            a = minimize(obj, x0, constraints=lc, bounds=bounds)
        else:
            a = minimize(obj, x0, bounds=bounds)
        return a.x, a.success

    def tangency_portfolio(self, rf, shorts=True):
        N = self.covariance_matrix.shape[0]
        obj = lambda x: -(np.matmul(self.expected_returns.T, x) - rf) / (
                    np.matmul(x.T, np.matmul(self.covariance_matrix.__array__(), x)) ** 0.5)
        lc = slc([np.ones(N).tolist()], [1], [1])
        x0 = np.ones((N, 1))
        if shorts:
            a = minimize(obj, x0, constraints=lc)
            tag = "TP"
        else:
            bounds = [(0, np.inf) for i in range(N)]
            a = minimize(obj, x0, constraints=lc, bounds=bounds)
            tag = "TPWS"
        return EnhancedPortfolio(tag, a.x, self.asset_keys, self.expected_returns,
                                 self.covariance_matrix, self.market_betas, self.risk_free_return)


class LinearConstraint:
    def __init__(self, eq, coef_vector, scalar=0):
        """
        this is a class that handles linear constraints as scalar = coef_vector^Tvar_vector
        :param eq: true means equality, false means inequality, default inequal behavior is greater, lesser is given with negative coeffs
        :param coef_vector: a vector with variable multiplies
        :param scalar: the result, if 0 means equal to zero
        """
        self.eq = eq
        self.coef_vector = coef_vector
        self.scalar = scalar

    def constrain(self, L_old, b_old):
        l_size = L_old.shape[0]
        c_size = self.coef_vector.shape[0]
        L_new = np.zeros((l_size + 2, l_size + 2))
        b_new = np.zeros((l_size + 2, 1))
        b_new[:l_size] = b_old
        L_new[:l_size, :l_size] = L_old
        L_new[l_size, :c_size] = self.coef_vector.T
        L_new[:c_size, l_size] = self.coef_vector.T
        b_new[l_size] = self.scalar
        if self.eq:
            return L_new[:l_size + 1, :l_size + 1], b_new[:l_size + 1]
        L_new[l_size, l_size + 1] = -1
        L_new[l_size + 1, l_size] = -1
        return L_new, b_new
