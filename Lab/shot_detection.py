from google.cloud import videointelligence

client = videointelligence.VideoIntelligenceServiceClient()

operation = client.annotate_video(
    request={
        "input_uri": "gs://YOUR_BUCKET/YOUR_VIDEO.mp4",
        "features": [videointelligence.Feature.SHOT_CHANGE_DETECTION],
    }
)

result = operation.result(timeout=300)
shots = result.annotation_results[0].shot_annotations

for number, shot in enumerate(shots, start=1):
    start = shot.start_time_offset.total_seconds()
    end = shot.end_time_offset.total_seconds()
    print(f"Shot {number}: {start:.2f}s to {end:.2f}s")