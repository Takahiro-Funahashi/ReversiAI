from sklearn.datasets import fetch_openml
from sklearn.datasets import fetch_california_housing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_boston

dataset = load_boston()

x, t = dataset.data, dataset.target
colums = dataset.feature_names

print(type(x), x.shape)
