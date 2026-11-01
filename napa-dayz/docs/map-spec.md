# Map spec

## Size and scale

| Setting | Value |
|---|---|
| In-game size | 20,480 m × 20,480 m |
| Height grid | 4096 × 4096 points, 5 m cells |
| Satellite and surface mask images | 20,480 × 20,480 px (1 m per pixel) |
| Real-world area | 23,040 m × 23,040 m |
| Scale | 8/9 (0.8889): 1 in-game meter = 1.125 real meters |
| Height scaling | Heights × 0.8889 too, so slopes keep their real shape (can be revisited) |
| Projection | NAD83 / UTM Zone 10N, **EPSG:26910** (the system the USGS data already uses) |
| Terrain Builder origin | Easting 200000, Northing 0 |

## Real-world area (EPSG:26910)

| Edge | UTM | Roughly |
|---|---|---|
| West | X 547000 | Carneros, lower slopes of Mt. Veeder |
| East | X 570040 | Hills behind Skyline Park and Coombsville |
| South | Y 4228000 | Marsh below the Napa County Airport runways |
| North | Y 4251040 | North of Yountville town center |

Scale went from ~90% to 8/9 so that the airport runways and Yountville both fit. Yountville town center is ~420 m from the north edge, and the airport is ~1.5 km from the south edge.

### Converting real-world to in-game coordinates

```
gameX = (UTM_X - 547000) * 0.8889
gameY = (UTM_Y - 4228000) * 0.8889
```

In-game coordinates start at (0, 0) in the southwest corner. These are the X / Z values that DayZ XML files (spawn points, events, loot positions) use.

## Test patch (Phase 1)

| Setting | Value |
|---|---|
| Real-world area | X 555430 → 558310, Y 4232870 → 4235750 (2,880 m) |
| In-game size | 2,560 m (512 grid × 5 m) |
| Satellite image | 2,560 × 2,560 px |
| Location | Carneros around Hwy 121 / Duhig Rd |

The test patch uses the same 8/9 scale as the full map, so every step carries straight over.

## Landmarks

Coordinates are approximate; check them in QGIS against the aerial photos before placing anything.

| Place | Lat, Lon | UTM X, Y | In-game X, Y |
|---|---|---|---|
| Napa County Airport | 38.2133, -122.2807 | 562970, 4229726 | 14195, 1534 |
| Napa State Hospital | 38.2780, -122.2660 | 564200, 4236915 | 15289, 7925 |
| Skyline Wilderness Park | 38.2750, -122.2480 | 565777, 4236595 | 16690, 7640 |
| Downtown Napa (1st & Main) | 38.2975, -122.2869 | 562355, 4239065 | 13649, 9835 |
| Oxbow district | 38.3015, -122.2830 | 562692, 4239511 | 13949, 10232 |
| Carneros (Hwy 121 / Duhig Rd) | 38.2550, -122.3500 | 556870, 4234308 | 8774, 5607 |
| Yountville (town center) | 38.4016, -122.3608 | 555813, 4250568 | 7834, 20061 |
| Veterans Home, Yountville | 38.3935, -122.3720 | 554841, 4249663 | 6970, 19256 |
