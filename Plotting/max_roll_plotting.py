import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
from scipy.fft import fft, fftfreq, rfft, rfftfreq

# --- Load CSV data ---
df = pd.read_csv('Plotting\\Data\\FT1_primary.csv')
df = df.set_index('time')
df = df[~df.index.duplicated(keep='first')]

dt = 0.01
t_new = np.arange(df.index.min(), df.index.max(), dt)
df = df.reindex(df.index.union(t_new)).interpolate('index').loc[t_new]
df = df.reset_index()


# --- Basic plot ---
df_main = df[df['time'] > 70]
df_main = df_main[df_main['time'] < 80]

time = df_main['time']
roll = df_main['gyro_roll']

print(time)

roll_smooth = savgol_filter(roll, window_length=20, polyorder=3)
roll_dot = savgol_filter(roll, window_length=21, polyorder=3, deriv=1, delta=dt)

print(max(roll_dot)*(np.pi/180)*1)

fft_vals = rfft(roll_dot)
fft_freqs = rfftfreq(len(roll_dot), dt)
fft_magnitude = np.abs(fft_vals) / len(roll_dot) * 2  # scale amplitude



# Make subplots: 2 rows, 1 column
fig, ax = plt.subplots(3, 1, figsize=(8,6))

# Plot roll
ax[0].plot(time, roll_smooth, label='Smooth Roll')
ax[0].plot(time, roll, label='Raw Roll',linestyle=':')
ax[0].set_ylabel('Roll Rate [°/s]')
ax[0].legend()
ax[0].grid(True)

# Plot pitch
ax[1].plot(time, roll_dot, label='Roll Acceleration', color='orange')
ax[1].set_ylabel('Roll Acceleration [°/s^2]')
ax[1].set_xlabel('Time [s]')
ax[1].legend()
ax[1].grid(True)

ax[2].plot(fft_freqs, fft_magnitude)
ax[2].set_xlim([0,5])
ax[2].set_xlabel('Frequnecy [Hz]')
ax[2].set_ylabel('Magnitude')

#Tight layout for spacing
plt.tight_layout()
plt.show()