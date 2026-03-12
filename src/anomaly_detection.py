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
