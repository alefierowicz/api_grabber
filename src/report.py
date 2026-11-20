"""console output of the weather comparison as rich tables"""

from typing import Any

from rich.console import Console
from rich.table import Table

from data_processor import NUMERIC_FIELDS, WeatherReading

COLUMNS = {
    "temp_c": "Temp °C",
    "humidity_pct": "Hum %",
    "pressure_hpa": "hPa",
    "wind_ms": "Wind m/s",
}

DIGITS = {"temp_c": 2, "humidity_pct": 1, "pressure_hpa": 1, "wind_ms": 2}


def fmt(value: float | None, digits: int = 2) -> str:
    """format a number with the given decimals, or a dash when it is missing"""
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def build_table(
    location: str, readings: list[WeatherReading], stats: dict[str, Any]
) -> Table:
    """build a table for one location with a row per source plus mean and spread"""
    table = Table(title=location, title_style="bold")
    table.add_column("Source")
    for field in NUMERIC_FIELDS:
        table.add_column(COLUMNS[field], justify="right")
    table.add_column("Description")
    table.add_column("Time", justify="right")

    for r in readings:
        table.add_row(
            r.source,
            *(fmt(getattr(r, field), DIGITS[field]) for field in NUMERIC_FIELDS),
            r.description or "—",
            f"{r.elapsed_s:.3f}s" if r.elapsed_s is not None else "—",
        )

    table.add_section()
    for stat in ("mean", "spread"):
        table.add_row(
            f"[bold]{stat}[/bold]",
            *(
                fmt(stats[field][stat], DIGITS[field]) if field in stats else "—"
                for field in NUMERIC_FIELDS
            ),
            "",
            "",
        )
    return table


def print_report(
    readings: list[WeatherReading],
    summary: dict[str, dict[str, Any]],
    results: list[dict[str, Any]],
    total_s: float,
) -> None:
    """print one table per location, then failed requests and timing totals"""
    console = Console()

    for location, stats in summary.items():
        location_readings = [r for r in readings if r.location == location]
        console.print(build_table(location, location_readings, stats))
        console.print()

    failed = [r for r in results if r["error"] is not None]
    if failed:
        console.print("[bold red]Failed:[/bold red]")
        for r in failed:
            console.print(
                f"  {r['source']} / {r['location']}: {r['error']} after {r['elapsed_s']:.2f}s"
            )
    else:
        console.print("Failed: none")

    request_sum_s = sum(r["elapsed_s"] for r in results)
    console.print(
        f"Total: [bold]{total_s:.2f}s[/bold] for {len(results)} requests "
        f"(sum of individual requests: {request_sum_s:.2f}s)"
    )
