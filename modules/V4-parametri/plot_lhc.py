m = marker
from matplotlib import markers
m = markers.MarkerStyles().markers.keys()

df2 = pd.read_csv(fname)

for i,col in enumerate([col for col in df2.columns if "Capita" not in col]):
    sortedd = df2.sort_values(by=col)
    plt.plot(sortedd[col],sortedd.AverageEnergyPerCapita_median,m[i],label=col)
    plt.legend()
