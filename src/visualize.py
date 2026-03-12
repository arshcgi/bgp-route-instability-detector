import seaborn as sns
import matplotlib.pyplot as plt

sns.histplot(grouped['update_count'], log_scale=True)
plt.title("Distribution of BGP Update Counts per Prefix")
plt.show()
