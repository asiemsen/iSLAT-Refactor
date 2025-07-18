class AppController():
    def __init__(self, moleculeManager, guiManager) -> None:
        self.moleculeManager = moleculeManager
        self.guiManager = guiManager

    def calculateSum(self):
        self.moleculeManager.calcSum(self.guiManager.ax1, self.guiManager.canvas)

    def drawCanvas(self):
        self.guiManager.canvas.draw()


        