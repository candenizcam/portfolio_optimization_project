from codes.dependencies import *


# this file has functions that are used in preprocessing the data, they include
# reading a stock, reading nasdaq index, reading 1 month bonds
# also, merges all the stocks to a single table, and a single function that yields relevant tables


#
def stock_reader(address, name, index="Adj Close", start_date=None, end_date=None, date_index=False):
    """
    stock reader reads a single stock, and creates a dataset between start end end for a given index
    :param address: address of the stock
    :param name: name for the stock
    :param index: the name of the index used for the stock
    :param start_date: dates
    :param end_date: dates
    :param date_index: if true, the date column is used as index
    :return: a df with date and stock prices
    """
    df = pd.read_csv(address)  # reading
    dates = [dt.datetime.strptime(i, "%Y-%m-%d").date() for i in df["Date"]]
    vals = df[index]
    (dates, vals) = time_bracket(dates, vals, start_date, end_date)
    if (date_index):
        return set_date_index(pd.DataFrame({"Date": dates, name: vals}), "Date")
    else:
        return pd.DataFrame({"Date": dates, name: vals})


def bond_reader(address, name, start_date=None, end_date=None, date_index=False):
    """
    bond reader reads 1 month bonds from the given csv file, fills gaps from the soonest past value
    :param address: address of the file
    :param name: name for the output
    :param start_date: dates
    :param end_date: dates
    :param date_index: if true, the date column is used as index
    :return:
    """
    df = pd.read_csv(address)  # reading
    dates = [dt.datetime.strptime(i, "%Y-%m-%d").date() for i in df["DATE"]]
    vals = df["DGS1MO"]
    d, v = gap_filler(dates, vals, start_date, end_date)
    p = pd.DataFrame({"DATE": d, name: v})
    p = p[[i.day == 1 for i in p["DATE"]]]
    if (date_index):
        return set_date_index(p, "DATE")
    else:
        return p


def index_reader(address, name, index="Adj Close", start_date=None, end_date=None, date_index=False):
    """Similar to bond, for nasdaq index"""
    df = pd.read_csv(address, na_filter=False)  # reading
    dates = [dt.datetime.strptime(i, "%Y-%m-%d").date() for i in df["Date"]]
    vals = df[index]
    d, v = gap_filler(dates, vals, start_date, end_date)
    p = pd.DataFrame({"Date": d, name: v})
    p = p[[i.day == 1 for i in p["Date"]]]
    if (date_index):
        return set_date_index(p, "Date")
    else:
        return p


def gap_filler(dates, vals, start_date, end_date):
    """
    fills gaps in dates and values, gaps may come as "." or empty date
    :param dates: dates list
    :param vals: vals list
    :param start_date: dates
    :param end_date:
    :return: gap filled dates and values
    """
    d = []
    v = []
    for j in pd.date_range(start=start_date, end=(end_date, dt.datetime.today())[end_date is None], freq="D"):
        i = j.date()
        d.append(i)
        if i not in dates:
            v.append(v[-1])
        else:
            v1 = vals[dates.index(i)]
            try:
                v.append(float(v1))
            except:
                for m in range(1, 10):
                    v2 = vals[dates.index(i) - m]
                    try:
                        v.append(float(v2))
                        break
                    except:
                        pass
    return d, v


def set_date_index(df, key):
    return df.sort_values(key).set_index(key)


def time_bracket(dates, vals, start_date, end_date):
    """ breaks the dates between start and end """
    if start_date is not None:  # time bracketing
        v = [start_date <= i for i in dates].index(True)
        vals = vals[v:]
        dates = dates[v:]
    if end_date is not None:
        v = [end_date < i for i in dates].index(True)
        dates = dates[:v]
        vals = vals[:v]
    return dates, vals


def nasdaq_dataset(l, start_date=None, end_date=None):
    """
    this creates a dataset for nasdaq input given, it is purpose built, and not a flexible function
    :param l: list of stock addresess
    :param start_date: dates
    :param end_date:
    :return: a dataset of stocks with given list of indices
    """
    ss = pd.DataFrame({"Date": []})
    for i in l:
        sr = stock_reader("data/raw_companies/" + i, i.split(".")[0], start_date=start_date, end_date=end_date)
        ss = pd.merge(ss, sr, on="Date", how="outer")
    return ss.sort_values("Date").set_index("Date")


def get_tables():
    """
    this one is used for the project as a fast handle
    :return: bonds, nasdaq100 and full stocks table
    """
    start_date = dt.datetime.strptime("2003.1.1", "%Y.%m.%d").date()
    raw_bonds = bond_reader("data/DGS1MO.csv", "DGS1MO", start_date=start_date, date_index=True)
    nasdaq_index_1 = index_reader("data/market_indices/NQ=F.csv", "NQ=F", start_date=start_date, date_index=True)
    nasdaq_index_2 = index_reader("data/market_indices/^IXIC.csv", "^IXIC", start_date=start_date, date_index=True)
    snp = index_reader("data/market_indices/^GSPC.csv", "^GSPC", start_date=start_date, date_index=True)
    l = os.listdir("data/raw_companies")
    nd = nasdaq_dataset(l, start_date=start_date)
    return raw_bonds, [nasdaq_index_1, nasdaq_index_2, snp], nd


if __name__ == "__main__":
    l = os.listdir("data/raw_companies")
    start_date = dt.datetime.strptime("2003.1.1", "%Y.%m.%d").date()
    end_date = dt.datetime.strptime("2005.1.1", "%Y.%m.%d").date()
    ss = stock_reader("data/index.csv", "NQ=F", start_date=start_date, end_date=end_date)
    nasdaq_dataset(l, start_date=start_date, end_date=end_date)
