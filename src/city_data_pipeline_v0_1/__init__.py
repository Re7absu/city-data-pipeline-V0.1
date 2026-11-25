"""City data pipeline: weather and air-quality data for Saudi cities."""


def main() -> None:
    """Entry point for the `city-data-pipeline-v0-1` command: run extraction."""
    from city_data_pipeline_v0_1.pipeline.extract import main as run_extract

    run_extract()
