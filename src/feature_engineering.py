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
