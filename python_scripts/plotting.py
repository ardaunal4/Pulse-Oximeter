import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

df = pd.read_csv("C:\\Users\\ardau\\Desktop\\dersler\\mixed_ic\\proje\\cpp_code\\cpp_serial_com\\SerialCommunication\\SerialCommunication\\output.csv")
time_vals = [i*0.1 for i in range(len(df["spo2"]))]
plt.figure(figsize=(10, 8))
plt.plot(time_vals, df["spo2"], "b--", label = "SpO2")
plt.xlabel("Time(s)")
plt.ylabel("SpO2 Level")
plt.title("SpO2 Measurement")
plt.grid("on")
plt.show()