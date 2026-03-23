import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV
df = pd.read_csv('data.csv')

# Show first 5 rows
print(df.head())

# Describe statistics
print(df.describe())

# ds it fits with depcham
df['column_name'].hist()
plt.xlabel('column_name')
plt.ylabel('Frequency')
plt.title('sebes')
plt.show()