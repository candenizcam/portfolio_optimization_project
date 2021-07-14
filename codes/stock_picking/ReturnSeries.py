from codes.dependencies import *


class ReturnSeries:
    """
        This is actually a data class but it also has methods to compute various useful information from a price series in time
        """

    def __init__(self, name, index, vals, series_type="Stock"):
        self.name = name
        self.index = list(index)
        self.raw_price = np.array(vals)
        self.series_type = series_type
        self.returns = self.returns_calculator(series_type, self.raw_price)
        self.c = self.q3c()

    @staticmethod
    def returns_calculator(series_type, raw_price):
        """
        Calculates returns for various series type
        :return: the returns as r (0 means returns are equal (R=1))
        """
        if series_type == "Stock":
            returns = np.zeros(len(raw_price))
            returns[1:] = np.log(raw_price[1:] / raw_price[:-1])
        elif series_type == "Bond":
            returns = np.log(1 + raw_price / 100) / 12
        else:
            raise print("incorrect input")
        return returns

    def q3c(self):
        """calculates a dict for necessary information at q3 part c"""
        c = {"mean": np.mean(self.returns), "median": np.median(self.returns), "maximum": np.max(self.returns),
             "minimum": np.min(self.returns), "std_dev": np.std(self.returns), "skewness": skew(self.returns),
             "kurtosis": kurtosis(self.returns), "obs_no": len(self.returns)}
        c["cv"] = c["std_dev"] / c["mean"]
        return c

    def q3(self):
        # d
        jb_value, p = jarque_bera(self.returns)

    def expected_utility(self, f):
        return np.mean(list(map(f, self.returns)))
