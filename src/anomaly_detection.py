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
