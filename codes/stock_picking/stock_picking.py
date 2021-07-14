from codes.dependencies import *
from codes.stock_picking.pre_process import get_tables
from codes.stock_picking.ReturnSeries import ReturnSeries



def naive_remove(l2, index, upto, remove_low=True):
    """
    This function generates a remover list, that is the list of the stocks to be removed, it does so starting from two
    highest correlating series, and removing the one that performs worse on the given index of ReturnsSeries.c
    :param l2: the list of pairwise correlations
    :param index: index of ReturnSeries.c, common choices are "mean", "std_dev"
    :param upto: the number of stocks to be removed
    :param remove_low: if true, the lower scoring stock is removed
    :return: a list of all stocks to be removed
    """
    remover = []
    for i in range(len(l2)):
        first = l2[-i - 1][0]
        second = l2[-i - 1][1]
        if (first.c[index] > second.c[index]) == remove_low:
            remover.append(second.name)
        else:
            remover.append(first.name)
        remover = list(set(remover))
        if len(l2) - len(remover) == upto:
            break
    return remover


def utility_remove(l2, U, upto, remove_low=True):
    """
    Similar to naive remover, but this function uses a utility function to pick from highest correlating pairs
    :param l2: list of correlation pairs
    :param U: utility function, applied to returns to change price into utility, mean of which is used to compare
    :param upto: the number of stocks to be removed
    :param remove_low: if true the lower expected utility is removed
    :return: a list of all stocks to be removed
    """
    remover = []
    for i in range(len(l2)):
        first = l2[-i - 1][0]
        second = l2[-i - 1][1]
        if (first.expected_utility(U) > second.expected_utility(U)) == remove_low:
            remover.append(second.name)
        else:
            remover.append(first.name)
        remover = list(set(remover))
        if len(remover) == upto:
            break
    return remover


def full_returns():
    """
    This is a simple function that reads the whole companies to pick best ones
    :return: list of ReturnSeries of all the companies
    """
    (bonds, indices, companies) = get_tables()
    return [ReturnSeries(i, companies.index, companies[i].array) for i in companies.keys()]


def correlations(companies_returned):
    """
    Generates a list of pairwise combinations, this was doable using the larger covariance matrix but i find this method
    to be easier to interpret
    :param companies_returned: the list of all companies ReturnSeries
    :return: the company pairs sorted by their correlation
    """
    l = []
    for i in combinations(companies_returned, 2):
        v = np.corrcoef(i[0].returns, i[1].returns)[0, 1]
        l.append((i[0], i[1], v))
    return sorted(l, key=lambda x: x[2])


def stock_picker():
    """
    Picks 10 stocks from the full list of stocks as described
    :return: a list of 10 str as the stock names picked by the utility function
    """
    companies_returned = full_returns()  # all stocks written as ReturnSeries objects
    corr_list = correlations(companies_returned)  # the list of correlations between returned companies
    remover = utility_remove(corr_list, lambda x: (x+1) ** 0.5, len(
        companies_returned) - 10)  # list of stocks to be removed, based on the utility function as given
    names = [i.name for i in companies_returned if i.name not in remover]  # the list of picked names
    return names


if __name__ == "__main__":
    """The tests for various stock picking approaches"""
    companies_returned = full_returns()
    l2 = correlations(companies_returned)

    for i in range(5, 15):
        pick_no = i
        # naive expected value approach
        remover = naive_remove(l2, "mean", len(companies_returned) - pick_no, remove_low=True)

        picked = [i for i in companies_returned if i.name not in remover]
        r = [i.returns for i in picked]
        names = [i.name for i in picked]
        V = np.cov(r)
        phi = np.ones(pick_no) / pick_no
        eq_cov = np.matmul(phi.T, np.matmul(V, phi))
        print(eq_cov)
        # naive std dev
        remover2 = naive_remove(l2, "std_dev", len(companies_returned) - pick_no, remove_low=False)
        picked2 = [i for i in companies_returned if i.name not in remover2]
        r2 = [i.returns for i in picked2]
        names2 = [i.name for i in picked2]
        V2 = np.cov(r2)
        eq_cov2 = np.matmul(phi.T, np.matmul(V2, phi))
        print(eq_cov2)
        # picked_companies = companies[picked]

        # utility function as return
        remover3 = utility_remove(l2, lambda x: (x + 1) ** 0.5, len(companies_returned) - pick_no)
        picked3 = [i for i in companies_returned if i.name not in remover3]
        r3 = [i.returns for i in picked3]
        names3 = [i.name for i in picked3]
        V3 = np.cov(r3)
        eq_cov3 = np.matmul(phi.T, np.matmul(V3, phi))
        print(eq_cov3)
        # picked_companies = companies[picked]

        print(set(names) - set(names3))

    alls = [i.returns for i in companies_returned]
    phi_all = np.ones(85) / 85
    V_all = np.cov(alls)
    all_cov = np.matmul(phi_all.T, np.matmul(V_all, phi_all))
    print(all_cov)
