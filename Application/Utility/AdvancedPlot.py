import matplotlib.pyplot as plt

class advancedPlot:
    
    def __init__(self, rowNum, colNum, name= '', sharex= True) -> None:
        self.rowNum = rowNum
        self.colNum = colNum
        self.barWidth = 0.00015
        self.sharex = sharex
        self.fig, self.ax = plt.subplots(rowNum, colNum, sharex= sharex, figsize=(15,15), num= name)

    def run(self, saveFig= False):
        self.fig.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        if self.rowNum > 1 and self.colNum > 1:
            self.xline = [[0 for _ in range(self.colNum)] for _ in range(self.rowNum)]
            for i in range(self.rowNum):
                for j in range(self.colNum):
                    self.set_options(self.ax[i][j])
        elif self.rowNum == 1 and self.colNum != 1 or self.rowNum != 1 and self.colNum == 1:
            self.xline = [0 for _ in range(max(self.colNum, self.rowNum))]
            for i in range(len(self.xline)):
                self.set_options(self.ax[i])
        elif self.rowNum == 1 and self.colNum == 1:
            self.xline = 0
            self.set_options(self.ax)

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        rc = {'axes.edgecolor': 'red', 'axes.linewidth': 1.5, 'axes.labelsize': 'large', 'axes.labelweight': 'semibold', 'axes.grid': False, 'axes.grid.axis': 'y', 'grid.linewidth': 0.4, 'lines.linewidth': 2.0, 'font.weight': 'medium', 'font.size': 3, 'figure.titlesize': 'x-large', 'figure.titleweight': 'normal'}
        plt.rcParams.update({'font.size': 3})
        if saveFig:
            plt.show(block=False)
            plt.pause(0.1)
            plt.close()
            self.fig.savefig('telegram.jpg', dpi=200)
        else:
            plt.show()

    def save_fig(self, name):
        self.fig.savefig(name)

    def on_click(self, event):
        if event.inaxes:
            if self.rowNum > 1 and self.colNum > 1:
                for i in range(self.rowNum):
                    for j in range(self.colNum):
                        if self.sharex or event.inaxes == self.ax[i][j]:
                            if type(self.xline[i][j]) == int:
                                yMin, yMax = self.ax[i][j].get_ylim()
                                self.xline[i][j], = self.ax[i][j].plot([event.xdata, event.xdata],[yMin,yMax], linewidth= 1)  
                            else:  
                                self.xline[i][j].set_xdata(event.xdata)
            elif self.rowNum == 1 and self.colNum != 1 or self.rowNum != 1 and self.colNum == 1:
                for i in range(len(self.xline)):
                    if self.sharex or event.inaxes == self.ax[i]:
                        if type(self.xline[i]) == int:
                            yMin, yMax = self.ax[i].get_ylim()
                            self.xline[i], = self.ax[i].plot([event.xdata, event.xdata],[yMin,yMax], linewidth= 1)  
                        else:  
                            self.xline[i].set_xdata(event.xdata)
            elif self.rowNum == 1 and self.colNum == 1:  
                if self.sharex or event.inaxes == self.ax: 
                    if type(self.xline) == int:
                        yMin, yMax = self.ax.get_ylim()
                        self.xline, = self.ax.plot([event.xdata, event.xdata],[yMin,yMax], linewidth= 1)  
                    else:  
                        self.xline.set_xdata(event.xdata)
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def set_options(self, ax):
        ax.grid(linestyle = '--', linewidth = 0.5)
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        # ax.xaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white') 