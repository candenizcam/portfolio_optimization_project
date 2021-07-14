from codes.dependencies import *

class PlotMother:
    def __init__(self, axes=[111], grid=True):
        self.fig = plt.figure()
        self.axes = [self.fig.add_subplot(i) for i in axes]
        [i.grid(grid) for i in self.axes]

    @staticmethod
    def ensure_dir(file_path):
        """
        ensures a directory exists, if it is not it is created
        :return:
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)


class BarPlot(PlotMother):
    def __init__(self, keys=None, vals= None, title="", width=0.6, line_width=0.5, edge_colour = "black"):
        super().__init__(grid=True)
        self.axes[0].set_title(title)
        self.width = width
        self.line_width = line_width
        self.edge_colour = edge_colour
        if keys is not None and vals is not None:
            self.plot_bars(keys, vals)

    def plot_bars(self, keys, vals):
        self.axes[0].bar(keys, vals, width=self.width, linewidth=self.line_width, edgecolor=self.edge_colour)

    def save(self, file_name, then_close=True):
        self.ensure_dir(file_name)
        self.fig.savefig(file_name)
        if then_close:
            plt.close(self.fig)



class MatrixPlot(PlotMother):
    def __init__(self, mat=None, title="", colour_bar = False):
        super().__init__(grid=False)
        self.axes[0].set_title(title)
        self.colour_bar = colour_bar
        if mat is not None:
            self.mat_plot = self.plot_matrix(mat)

    def plot_matrix(self, mat):
        mat_plot = self.axes[0].matshow(mat)
        if self.colour_bar:
            self.fig.colorbar(mat_plot)
        self.fig.show()
        return mat_plot

    def save(self, file_name):
        self.ensure_dir(file_name)
        self.fig.savefig(file_name)


class SinglePlot(PlotMother):
    def __init__(self, x=None, y=None, title="", legend=False, xlabel ="", ylabel="", xlim=None, ylim=None):
        super().__init__(grid=True)
        self.axes[0].set_title(title)
        self.legend = legend
        self.lines = []
        self.axes[0].set_xlabel(xlabel)
        self.axes[0].set_ylabel(ylabel)
        if y is not None:
            if x is None:
                self.plot_line_x(y)
            else:
                self.plot_line_xy(x, y)
        self.xlim = xlim
        self.ylim = ylim

    def plot_line_xy(self, x, y, legend=None, linestyle = "-",marker=None, color=None):
        p = self.axes[0].plot(x, y, label = self.getLegend(legend), linestyle = linestyle, marker=marker,color=color)
        self.lines.append(p)
        if self.legend:
            self.axes[0].legend()

    def plot_line_x(self, x, legend=None, linestyle = "-",marker=None, color=None):
        p = self.axes[0].plot(x, label = self.getLegend(legend), linestyle = linestyle,marker=marker,color=color)
        self.lines.append(p)
        if self.legend:
            self.axes[0].legend()

    def scatter_xy(self,x,y,legend=None,marker="o", color=None):
        p = self.axes[0].scatter(x, y, label=self.getLegend(legend), marker=marker, color=color)
        self.lines.append(p)
        if self.legend:
            self.axes[0].legend()


    def getLegend(self, legend=None):
        if legend is None:
            return "line: " + str(len(self.lines))
        else:
            return legend

    def save(self, file_name, then_close=True):
        self.ensure_dir(file_name)
        if self.xlim is not None:
            self.axes[0].set_xlim(self.xlim[0],self.xlim[1])
        if self.ylim is not None:
            self.axes[0].set_ylim(self.ylim[0], self.ylim[1])
        self.fig.savefig(file_name)
        if then_close:
            plt.close(self.fig)
