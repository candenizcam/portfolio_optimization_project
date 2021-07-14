from codes.dependencies import *


class SingleRegression:
    def __init__(self, x, y):
        """
        this is a single regression that does the necessary calculations for part 5
        :param x: market samples
        :param y: other samples
        """
        self.x = np.array(x).flatten()
        self.y = np.array(y).flatten()
        self.vandermonde = np.ones((self.x.shape[0], 2))
        self.vandermonde[:, 1] = self.x
        v = np.linalg.lstsq(self.vandermonde, self.y, rcond=-1)  # regression
        self.beta = v[0][1]  # coefficients
        self.alpha = v[0][0]
        self.y_hat = self.alpha + self.beta * self.x
        self.residuals = self.y - self.y_hat
        self.null_test_dict = self.null_test()  # null test values are put in a dict
        self.shape_test_dict = self.shape_test()  # shape test values are put in a dict
        self.unsystematic_risk = 1 - self.null_test_dict["R2"]  # risk measures
        self.estimated_var = self.unsystematic_risk ** 2 + self.null_test_dict["R2"]

    def shape_test(self):
        """
        does the shape test bit (part b after jb)
        :return:
        """
        shape_test = dict()
        jb_value, p = jarque_bera(self.residuals)
        shape_test["jb value"] = jb_value
        shape_test["jb test: normal"] = p > 0.05
        acf_vals = acf(self.residuals, nlags=12, fft=False, alpha=0.05, qstat=True)
        autocor_dict = {"1M lag correlation": acf_vals[0][1], "1M lag lower conf": acf_vals[1][1, 0],
                        "1M lag upper conf": acf_vals[1][1, 1], "1M conf band": acf_vals[1][1, 1] - acf_vals[1][1, 0],
                        "6M lag correlation": acf_vals[0][6], "6M lag lower conf": acf_vals[1][6, 0],
                        "6M lag upper conf": acf_vals[1][6, 1], "6M conf band": acf_vals[1][6, 1] - acf_vals[1][6, 0],
                        "12M lag correlation": acf_vals[0][12], "12M lag lower conf": acf_vals[1][12, 0],
                        "12M lag upper conf": acf_vals[1][12, 1],
                        "12M conf band": acf_vals[1][12, 1] - acf_vals[1][12, 0]}
        shape_test.update(autocor_dict)
        shape_test["q test"] = acf_vals[-2][11]
        shape_test["q test p"] = acf_vals[-1][11]
        white_test = het_white(self.residuals, self.vandermonde)
        shape_test["white LM"] = white_test[0]
        shape_test["white LM p"] = white_test[1]
        shape_test["heteroscedasticity"] = shape_test[
                                               "white LM p"] < 0.05  # if true is heteroscedastic, if false homoscedastic
        return shape_test

    def null_test(self):
        """
        does null test bit (part b up to jb) of q5 and assembles it as a dict
        :return: the dict
        """
        nt = dict()
        n = len(self.x)
        standard_error_b = np.sqrt(
            1 / (n - 2) * np.sum((self.y_hat - self.y) ** 2) / np.sum((self.x - np.mean(self.x)) ** 2))
        standard_error_a = standard_error_b * np.sqrt(1 / n * np.sum(self.x ** 2))
        nt["ste alpha"] = standard_error_a
        nt["ste beta"] = standard_error_b
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
        ss_res = np.sum((self.y - self.y_hat) ** 2)
        nt["R2"] = 1 - ss_res / ss_tot
        nt["beta conf. down"] = self.beta - 1.96 * standard_error_b
        nt["beta conf. up"] = self.beta + 1.96 * standard_error_b
        nt["null test for beta=1"] = (nt["beta conf. up"] > 1) and (nt["beta conf. down"] < 1)
        return nt

    def get_dict(self):
        """
        :return: the dict for part 5
        """
        d = {"alpha": self.alpha, "beta": self.beta}
        d.update(self.null_test_dict)
        d.update(self.shape_test_dict)
        d["unsystematic risk"] = self.unsystematic_risk
        d["estimated var"] = self.estimated_var
        return d


class CAPMRegression(SingleRegression):
    def __init__(self, x, y):
        """
        This is a child version of regular SingleRegression that also does chow test
        :param x: independent variable
        :param y: dependent variable
        """
        super().__init__(x, y)
        self.chow, self.chow_result, self.mean_y2, self.beta_1 = self.chow_test()

    def chow_test(self):
        """
        Conducts chow test by separating samples into two groups, regressing on both and finding chow measure
        :return: a tuple of chow test output, the result as a bool, mean y2 and beta1 for plots
        """
        midpoint = len(self.x) // 2
        x1 = self.x[:midpoint]
        y1 = self.y[:midpoint]
        x2 = self.x[midpoint:]
        y2 = self.y[midpoint:]

        # parts are regressed individually
        sr1 = SingleRegression(x1, y1)
        sr2 = SingleRegression(x2, y2)

        # s are computed
        Sc = np.sum(self.residuals ** 2)
        S1 = np.sum(sr1.residuals ** 2)
        S2 = np.sum(sr2.residuals ** 2)

        # num and denum are computed separately for clarity
        num = (Sc - (S1 + S2)) / 2
        denum = (S1 + S2) / (len(x1) + len(x2) - 2 * 2)
        s = num / denum  # chow test output
        return s, s < 0.05, np.mean(y2), sr1.beta  # if true, data has a break point

    def null_test(self):
        """
        does null test for q6 to alpha and assembles it as a dict
        :return: the dict
        """
        nt = dict()
        n = len(self.x)
        standard_error_b = np.sqrt(
            1 / (n - 2) * np.sum((self.y_hat - self.y) ** 2) / np.sum((self.x - np.mean(self.x)) ** 2))
        standard_error_a = standard_error_b * np.sqrt(1 / n * np.sum(self.x ** 2))
        nt["ste alpha"] = standard_error_a
        nt["ste beta"] = standard_error_b
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
        ss_res = np.sum((self.y - self.y_hat) ** 2)
        nt["R2"] = 1 - ss_res / ss_tot
        nt["alpha conf. down"] = self.alpha - 1.96 * standard_error_a
        nt["alpha conf. up"] = self.alpha + 1.96 * standard_error_a
        nt["null test for alpha=0"] = (nt["alpha conf. down"] < 0) and (nt["alpha conf. up"] > 0)
        return nt

    def get_dict(self):
        """
        :return: the dict for the table
        """
        d = {"alpha": self.alpha, "beta": self.beta}
        d.update(self.null_test_dict)
        d["chow"] = self.chow
        d["chow test"] = self.chow_result
        d["unsystematic risk"] = self.unsystematic_risk
        d["estimated var"] = self.estimated_var
        return d
