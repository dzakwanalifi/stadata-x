# stadata_x/widgets/plot_widget.py

import plotext as plt
from textual.widgets import Static

class PlotWidget(Static):
    """Widget untuk merender dan menampilkan grafik dari plotext."""

    def on_mount(self) -> None:
        """Render plot awal saat widget dimuat."""
        self.update_plot()

    def update_plot(self) -> None:
        """Membuat plot sampel dan merendernya ke widget."""
        years = [2020, 2021, 2022]
        growth = [-2.52, 3.74, 5.45]

        plt.clf() 
        plt.bar(years, growth)
        plt.title("Laju Pertumbuhan Ekonomi")
        plt.xlabel("Tahun")
        plt.ylabel("Persen (%)")
        plt.theme("dark")

        self.update(plt.build())
