# i.s2_id.filter

## DESCRIPTION

*i.s2_id.filter* searches Sentinel-2 Level-2A scenes using
[EODAG](https://eodag.readthedocs.io/) and returns matching scene IDs.
The module filters by time range, area of interest (AOI), tile ID, and cloud cover.

The search is currently configured for:

- Provider: `cop_dataspace` (CDSE)
- Collection: `S2_MSI_L2A`

If no manual bounding-box options are provided, the current GRASS region is used
as AOI by default.

If any one of `lonmin`, `lonmax`, `latmin`, or `latmax` is set,
all four values must be provided.

When flag `-s` is used, `stac_collection` is required. The module reads
the end of the temporal extent from the given STAC collection and sets:

- `start_time` to one day after that end date
- `end_time` to today

## OUTPUT

By default, the module writes a JSON object. The keys are Sentinel-2 scene IDs and
the values contain selected metadata:

- `acquisition_date`: Scene acquisition datetime
- `cloud_cover`: Cloud cover percentage
- `tile_id`: Sentinel-2 MGRS tile ID

```json
{
	"S2A_MSIL2A_20250401T092031_N0510_R093_T34SFH_20250401T125901": {
		"acquisition_date": "2025-04-01T09:20:31Z",
		"cloud_cover": 12.4,
		"tile_id": "34SFH"
	}
}
```

When `-p` is used, results are printed as formatted text messages.

## EXAMPLES

### 1. Filter by time range, tile ID, and current region (default AOI)

```sh
# Region is used as AOI by default
i.s2_id.filter start_time=2025-01-01 end_time=2025-01-31 cloud_cover=20 tile_id=34SFH
```

### 2. Filter by explicit bounding box

```sh
i.s2_id.filter start_time=2025-01-01 end_time=2025-01-31 cloud_cover=30 \
		lonmin=23.60 lonmax=23.90 latmin=37.85 latmax=38.10
```

### 3. Continue search from STAC collection temporal extent

```sh
i.s2_id.filter -s stac_collection=https://example.org/stac/collections/s2_indices.json \
		lonmin=23.60 lonmax=23.90 latmin=37.85 latmax=38.10 cloud_cover=40
```

### 4. Write JSON output to file

```sh
i.s2_id.filter start_time=2025-01-01 end_time=2025-01-31 \
		cloud_cover=20 output=s2_results.json
```

## NOTES

- Requires working EODAG installation. For only searching metadata, no provider credentials are needed.

## SEE ALSO

- [EODAG installation](https://eodag.readthedocs.io/en/stable/getting_started_guide/install.html)
- [STAC specification](https://stacspec.org/en)

## AUTHOR

Jonas Pischke, [mundialis GmbH & Co. KG](https://www.mundialis.de/), Germany
