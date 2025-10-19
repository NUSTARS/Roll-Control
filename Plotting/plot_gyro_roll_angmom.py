#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt

def build_datetime(row):
    try:
        return datetime(
            int(row["year"]),
            int(row["month"]),
            int(row["day"]),
            int(row["hour"]),
            int(row["minute"]),
            int(row["second"]),
            tzinfo=timezone.utc,
        )
    except Exception:
        return pd.NaT

def main():
    ap = argparse.ArgumentParser(description="Plot gyro_roll vs time from rocket CSV, showing flight states")
    ap.add_argument("csv", help="Path to CSV file")
    ap.add_argument("-o", "--output", help="Path to save PNG (if omitted, shows window)")
    ap.add_argument("--use-datetime", action="store_true",
                    help="Use combined year/month/day/hour/minute/second as x-axis instead of the 'time' column")
    ap.add_argument("--compute-velocity", action="store_true",
                    help="Compute maximum wheel velocity by integrating 'acceleration' between 'main' and 'landing' states")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, skipinitialspace=True, engine="python")

    needed = ["gyro_roll", "state_name"]
    # velocity computation needs acceleration + time
    if args.compute_velocity:
        needed += ["acceleration", "time"]
    if args.use_datetime:   # ✅ fixed underscore
        needed += ["year", "month", "day", "hour", "minute", "second"]
    else:
        needed += ["time"]
    for col in needed:
        if col not in df.columns:
            raise SystemExit(f"Missing required column: {col}")

    # Prepare time axis
    if args.use_datetime:   # ✅ fixed underscore
        x = df.apply(build_datetime, axis=1)
        x_label = "Timestamp (UTC)"
    else:
        x = df["time"]
        x_label = "Time (s)"


    y = df["gyro_roll"]

    # If requested, compute maximum velocity from main -> landing
    if args.compute_velocity:
        # normalize state strings
        s = df["state_name"].astype(str).str.strip().str.lower()

        # find main span
        main_idx = s[s == "main"].index
        if len(main_idx) == 0:
            print("No 'main' state found; cannot compute velocity.")
        else:
            start = int(main_idx[0])
            # find first index after main span where state changes
            end = start + 1
            while end < len(s) and s.iloc[end] == "main":
                end += 1

            # If we didn't find an explicit 'landing', try common alternatives
            landing_candidates = ["landing", "land", "touchdown"]
            landing_idx = None
            for cand in landing_candidates:
                found = s[s == cand].index
                if len(found) > 0:
                    landing_idx = int(found[0])
                    break

            # If we did find a landing after main use it; otherwise use first non-main state after main
            if landing_idx is not None and landing_idx > start:
                stop = landing_idx
                reason = f"found landing state '{s.iloc[landing_idx]}' at index {landing_idx}"
            elif end < len(s):
                stop = end
                reason = f"no explicit landing; using first state after main at index {end} ('{s.iloc[end]}')"
            else:
                stop = len(s) - 1
                reason = f"no state after main; using end of file index {stop}"

            # Extract time and acceleration for integration
            try:
                t = df["time"].astype(float).iloc[start:stop].to_numpy()
                a = df["acceleration"].astype(float).iloc[start:stop].to_numpy()
            except Exception as e:
                print(f"Failed to extract numeric time/acceleration: {e}")
                t = None
                a = None

            if t is None or a is None or len(t) < 2:
                print("Not enough samples to integrate velocity in the selected interval.")
            else:
                # numerical trapezoidal integration (v[0]=0)
                import numpy as _np

                v = _np.zeros_like(a)
                for i in range(1, len(a)):
                    dt = t[i] - t[i - 1]
                    v[i] = v[i - 1] + 0.5 * (a[i] + a[i - 1]) * dt

                imax = int(_np.argmax(_np.abs(v)))
                print("\n--- Velocity Computation (main -> landing) ---")
                print(f"main start index: {start}, stop index used: {stop} ({reason})")
                print(f"interval time: {t[0]} .. {t[-1]}  (n={len(t)})")
                print(f"max velocity in interval = {v.max():.6f} (at t={t[_np.argmax(v)]:.6f})")
                print(f"min velocity in interval = {v.min():.6f} (at t={t[_np.argmin(v)]:.6f})")
                print(f"max abs velocity = {float(_np.max(_np.abs(v))):.6f} (index {imax}, t={t[imax]:.6f}, v={v[imax]:.6f}, a={a[imax]:.6f})")
                print("Note: Units depend on 'acceleration' (assumed m/s^2) and 'time' (assumed s).")

    # Plotting
    # If compute_velocity was requested and we computed v, show acceleration (top) and velocity (bottom)
    has_velocity = args.compute_velocity and 'v' in locals() and isinstance(locals().get('v'), (list, tuple, __import__('numpy').ndarray))
    if has_velocity:
        fig, (ax_acc, ax_vel) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        # plot acceleration on top (use same slice used for integration)
        try:
            ax_acc.plot(x.iloc[start:stop], df["acceleration"].astype(float).iloc[start:stop], color="tab:blue", label="Acceleration (deg/s^2)")
        except Exception:
            # fallback: plot full series if slice failed
            ax_acc.plot(x, df["acceleration"].astype(float), color="tab:blue", label="Acceleration (deg/s^2)")

        # plot velocity on bottom
        ax_vel.plot(x.iloc[start:stop], v, color="tab:green", label="Velocity (deg/s)")

        # add zero line to both for reference
        ax_acc.axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.8)
        ax_vel.axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.8)

        ax = ax_acc  # primary axis for shared decorations
    else:
        # Plot gyro_roll as before
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, y, color="black", label="Gyro Roll")

        # Add horizontal zero line
        ax.axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.8, label="Zero Line")

    # Identify where state changes
    df["state_change"] = df["state_name"].ne(df["state_name"].shift())
    change_indices = df.index[df["state_change"]].tolist()
    change_indices.append(len(df) - 1)

    # Color palette for states
    colors = plt.cm.tab20.colors
    color_map = {}
    color_i = 0

    for i in range(len(change_indices) - 1):
        start = change_indices[i]
        end = change_indices[i + 1]
        state = df.loc[start, "state_name"]
        color = color_map.setdefault(state, colors[color_i % len(colors)])
        color_i += 1

        x_start = x.iloc[start]
        x_end = x.iloc[end]
        # apply span to either single ax or both subplots
        if has_velocity:
            ax_acc.axvspan(x_start, x_end, color=color, alpha=0.2)
            ax_vel.axvspan(x_start, x_end, color=color, alpha=0.2)
            # label on top plot
            ax_acc.text((x_start + (x_end - x_start) / 2), ax_acc.get_ylim()[1] * 0.95, state,
                         ha="center", va="top", fontsize=8, color=color)
        else:
            ax.axvspan(x_start, x_end, color=color, alpha=0.2)
            ax.text((x_start + (x_end - x_start) / 2), max(y)*0.95, state,
                    ha="center", va="top", fontsize=8, color=color)

    ax.set_xlabel(x_label)
    ax.set_ylabel("Gyro Roll (°/s or rad/s)")
    ax.set_title("Gyro Roll vs Time with Flight States")
    ax.legend()
    plt.tight_layout()

    if args.output:
        plt.savefig(args.output, dpi=150)
        print(f"Saved plot to {args.output}")
    else:
        # Print summary stats for main state
        if "state_name" in df.columns:
            main_data = df[df["state_name"].str.lower().str.contains("main", na=False)]
            if not main_data.empty:
                print("\n--- Main State Gyro Roll Summary ---")
                print(main_data["gyro_roll"].describe())
                mean_roll = main_data["gyro_roll"].mean()
                print(f"\nAverage Gyro Roll during MAIN: {mean_roll:.3f}")
            else:
                print("\nNo 'main' state found in data.")
        plt.show()

if __name__ == "__main__":
    main()
