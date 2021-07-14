from codes.dependencies import *


class OutputWriter:
    """
    this class opens an excel file and progressively writes to sheets, example usage below
    address: address of the file to be written
    """
    def __init__(self, address):
        self.address = address
        self.ensure_dir(address)
        self.pages = 1

    def write(self, df, sheet_name=None, transpose=False):
        """writes df to the given output, as the sheet with the given name
        (or assigned by the sheet number if None is given)"""
        if self.pages > 1:
            mode = 'a'
        else:
            mode = 'w'
        if sheet_name is None:
            sheet_name = "Sheet" + str(self.pages)
        self.pages += 1
        if transpose:
            df = df.transpose()
        with pd.ExcelWriter(self.address, mode=mode, datetime_format="yyyy/mm/dd") as writer:
            df.to_excel(writer, sheet_name=sheet_name)

    def reset_file(self):
        """this resets the writing but does not erase the previous output,
        previous output is overwritten on first write call"""
        self.pages = 1

    @staticmethod
    def ensure_dir(file_path):
        """
        ensures a directory exists, if it is not it is created
        :return:
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)


if __name__ == "__main__":
    ow = OutputWriter('output/test.xlsx')
    example_df = pd.DataFrame({'Names': ['Stephen', 'Camilla', 'Tom'], 'Salary': [100000, 70000, 60000]})
    ow.write(df=example_df)
