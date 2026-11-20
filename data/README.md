# The synthetic NOKTA dataset

All files of this folder are produced by `tools/make_synthetic_data.py` with the seed 2026. The values are invented. They are plausible for a sunny November morning at mid-latitudes but describe no real campus, and they must not be quoted as findings. A Turkish version of this page is in [README.tr.md](README.tr.md).

## Design

Three campuses, A (inland highland), B (continental city) and C (coastal), have six fixed point types each. One portable station per campus (S1, S2, S3) visits the points at about 1.5 m in two rounds. Round 1 starts at 10:00 and visits P1 to P6. Round 2 visits P6 to P1 at the same clock times. Each visit lasts 15 minutes with a reading every 10 seconds, followed by 10 minutes of walking to the next point.

| Point | Type | Field form note |
|---|---|---|
| P1 | `shaded` | narrow passage between two buildings, no direct sun |
| P2 | `traffic` | two meters from the campus road, buses stop nearby |
| P3 | `reference` | open lawn edge away from roads and entrances |
| P4 | `sunny_hard` | concrete square in full sun, station housing in direct sun |
| P5 | `crowded` | faculty entrance, a group smoking near the door |
| P6 | `green` | under a row of trees, grass irrigated in the morning |

## `nokta_synthetic.csv`, 3,240 rows

| Column | Unit | Meaning |
|---|---|---|
| `sample_id` | | running number of the reading |
| `timestamp` | local time | date and time of the reading |
| `campus` | | A, B or C |
| `round` | | 1 or 2 |
| `point_id`, `point_type` | | P1 to P6 and the type above |
| `visit_order` | | position of the visit in its round (1 to 6) |
| `station` | | S1, S2 or S3 |
| `seconds_since_arrival` | s | 0 to 890 |
| `temperature_c` | °C | air temperature |
| `rel_humidity_pct` | % | relative humidity |
| `pressure_hpa` | hPa | station air pressure (set mostly by altitude) |
| `pm1_ugm3`, `pm25_ugm3`, `pm10_ugm3` | µg/m³ | particle mass from an optical sensor |
| `co2_ppm` | ppm | carbon dioxide |
| `light_lux` | lx | illuminance (a 16-bit sensor stops at 65,535) |
| `uva_wm2`, `uvb_wm2` | W/m² | ultraviolet A and B irradiance |

## The other files

- `nokta_field_forms_synthetic.csv`: One row per visit with `date`, `start`, `end`, `vehicles_15min`, `people_15min`, `sun_condition` (shade, partial, sun), `sky`, `green_cover_pct`, `station` and `notes`.
- `nokta_colocation_synthetic.csv`: The three stations side by side on 31 October from 14:00 to 16:00, one reading per minute of temperature, humidity, PM2.5 and CO₂.
- `nokta_synthetic_qc_truth.csv`: `sample_id` and `qc_truth`, the problem planted in each reading (`ok`, `warmup`, `spike_pm25`, `spike_pm10`, `spike_co2`, `flatline_co2`, `gap`, `saturated`, `high_rh`). Real data have no such file.
- `nokta_template.csv`: The header of the readings file, to be used for real NOKTA data.

## How the values were made

The script draws a background for each campus and round that warms through the morning and slowly dilutes particles and CO₂. Each point type adds its own effect: Shade cools, the sunny square warms and heats the sensor housing, traffic adds short plumes of particles and CO₂, smokers add strong short spikes at the entrance, and trees cool, dim the light and lower particles slightly. The sensor layer then adds what low-cost devices do: A two-minute settling after every move, station offsets, particle readings inflated by humidity (κ-Köhler growth with κ = 0.3), a frozen CO₂ sensor, single-channel glitches, logger dropouts and a light sensor at its limit.
