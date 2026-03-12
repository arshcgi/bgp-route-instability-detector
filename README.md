# BGP Route Instability Detector

Machine‑learning based BGP Route Instability Detector using MRT parsing, feature engineering, and Isolation Forest anomaly detection.
A machine‑learning based system that detects unstable Internet prefixes by analysing BGP update messages from RIPE RIS MRT archives.
This project parses raw BGP update files, extracts routing behaviour, engineers instability features, applies anomaly detection, and visualises unstable prefixes

# Project Overview
Border Gateway Protocol (BGP) controls how traffic flows across the global Internet.
When a prefix becomes unstable (route flapping, path churn, origin changes), it can cause:
- packet loss
- latency spikes
- routing loops
- service outages
This project automatically detects such instability using:
- MRT parsing
- Feature engineering
- Isolation Forest anomaly detection
- Time‑series visualisation
  
# Repository Structure

```
src/
  parse_mrt.py
  feature_engineering.py
  anomaly_detection.py
  visualize.py
data/
results/
README.md
requirements.txt
```

# 1. Download MRT File

```

!pip install git+https://github.com/YoshiyukiYamauchi/mrtparse.git
import mrtparse
print("mrtparse is working!")

```

```
!wget https://data.ris.ripe.net/rrc00/2024.01/updates.20240101.0000.gz -O updates.mrt.gz

```

# 2. Parse MRT File

```

import mrtparse
import pandas as pd

mrt_file = "updates.mrt.gz"
reader = mrtparse.Reader(mrt_file)
records = []

for entry in reader:
    if entry.err or not entry.data:
        continue

    data = entry.data
    bgp = data.get('bgp_message')
    if not bgp:
        continue

    bgp_type = list(bgp['type'].keys())[0]
    if bgp_type != 2:  # UPDATE messages only
        continue

    as_path = []
    next_hop = None

    for attr in bgp.get('path_attributes', []):
        if 2 in attr['type']:
            as_path = attr['value'][0]['value'] if attr['value'] else []
        elif 3 in attr['type']:
            next_hop = attr['value']

    ts = list(data['timestamp'].keys())[0]
    timestamp = pd.to_datetime(ts, unit='s')

    for nlri in bgp.get('nlri', []):
        prefix = f"{nlri['prefix']}/{nlri['length']}"
        records.append({
            "timestamp": timestamp,
            "prefix": prefix,
            "type": "announce",
            "peer_as": data.get('peer_as'),
            "as_path": " ".join(as_path),
            "origin_as": as_path[-1] if as_path else None,
            "next_hop": next_hop
        })

    for nlri in bgp.get('withdrawn_routes', []):
        prefix = f"{nlri['prefix']}/{nlri['length']}"
        records.append({
            "timestamp": timestamp,
            "prefix": prefix,
            "type": "withdraw",
            "peer_as": data.get('peer_as'),
            "as_path": " ".join(as_path),
            "origin_as": as_path[-1] if as_path else None,
            "next_hop": next_hop
        })

df = pd.DataFrame(records)
df.head()

```

# 3. Feature Engineering

```

df['path_length'] = df['as_path'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

grouped = df.groupby("prefix").agg(
    update_count=("timestamp","count"),
    withdraw_count=("type", lambda x: (x == "withdraw").sum()),
    announce_count=("type", lambda x: (x == "announce").sum()),
    unique_as_paths=("as_path", "nunique"),
    origin_as_changes=("origin_as","nunique"),
    path_length_mean=("path_length","mean"),
).reset_index()

grouped.head()

```

# 4. Visualise Update Distribution

```

import seaborn as sns
import matplotlib.pyplot as plt

sns.histplot(grouped['update_count'], log_scale=True)
plt.title("Distribution of BGP Update Counts per Prefix")
plt.show()

```

# 5. Anomaly Detection (Isolation Forest)

```

from sklearn.ensemble import IsolationForest

features = grouped[[
    "update_count",
    "withdraw_count",
    "unique_as_paths",
    "origin_as_changes",
    "path_length_mean"
]]

model = IsolationForest(contamination=0.02, random_state=42)
grouped['anomaly'] = model.fit_predict(features)
grouped['score'] = model.decision_function(features)

unstable = grouped[grouped['anomaly'] == -1]
unstable.sort_values("score").head(20)

```

# 6. Visualise an Unstable Prefix

```

sample_prefix = unstable.sort_values("score").iloc[0]['prefix']
sample_df = df[df['prefix'] == sample_prefix]

ax = sample_df.set_index('timestamp').resample('1min').size().plot(figsize=(12,5))

plt.title(f"Update Timeline for {sample_prefix}")
plt.xlabel("Time")
plt.ylabel("Updates per minute")

plt.savefig("results/figures/update_timeline.png")
plt.show()

```

# Results
- Successfully parsed RIPE RIS MRT BGP updates
- Engineered routing instability features
- Detected anomalous prefixes using Isolation Forest
- Visualised real BGP instability (e.g., 67.211.53.0/24)
  
# Business Value
This system can be used by:
- ISPs
- Cloud providers
- NOC teams
- Monitoring platforms (e.g., ThousandEyes, Kentik)
To detect:
- route flapping
- path churn
- origin AS changes
- routing leaks
- early signs of outages
  
# Future Work
- Add AS‑path graph visualisation
- Add BGP hijack detection
- Add real‑time streaming support
- Deploy as a dashboard (Streamlit/FastAPI)








