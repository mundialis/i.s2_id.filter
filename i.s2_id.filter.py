#!/usr/bin/env python3
# ruff: noqa: D100, DTZ011, PLR0914, PTH123
#
############################################################################
# MODULE:      i.s2_id.filter
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Filter Sentinel-2 scenes by time range, AOI, UTM tile ID
# and cloud cover.
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
#
# %module
# % description: Filter S2 scenes by time range, AOI, tile ID and cloud cover.
# % keyword: raster
# % keyword: Sentinel-2
# % keyword: eodag
# %end

# %option
# % key: start_time
# % description: Start time for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: end_time
# % description: End time for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: tile_id
# % description: S2 tile ID for filtering S2 scenes e.g. 33UXP
# % required: no
# % type: string
# %end

# %option
# % key: cloud_cover
# % description: Maximum cloud cover for filtering S2 scenes
# % required: no
# % answer: 100
# % type: string
# %end

# %option
# % key: lonmin
# % description: Minimum longitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: lonmax
# % description: Maximum longitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: latmin
# % description: Minimum latitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: latmax
# % description: Maximum latitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: stac_collection
# % description: URL to STAC collection for retrieving start time
# % required: no
# % type: string
# %end

# %option
# % key: output
# % description: Path to output JSON file
# % required: no
# % type: string
# %end

# %flag
# % key: s
# % description: Retrieve start time from last entry in STAC collection
# %end

# %flag
# % key: p
# % description: Only print query results as text output
# %end

# %rules
# % collective: lonmin,lonmax,latmin,latmax
# % requires: -s,stac_collection
# %end

import datetime
import json
import sys

import grass.script as grass
import pystac
from eodag import EODataAccessGateway


def main() -> None:
    """Filter S2 scenes."""
    # Get options
    start = options["start_time"]
    end = options["end_time"]
    tile_id = options["tile_id"]
    cloud_cover = options["cloud_cover"]
    lonmin = options["lonmin"]
    lonmax = options["lonmax"]
    latmin = options["latmin"]
    latmax = options["latmax"]
    stac_collection = options["stac_collection"]
    output = options["output"]
    s = flags["s"]
    p = flags["p"]

    # get bbox from region (must have been set before)
    if not lonmin:
        bbox_ll = grass.parse_command(
            "g.region",
            format="json",
            flags="b",
            quiet=True,
        )
        lonmin = bbox_ll["ll_w"]
        lonmax = bbox_ll["ll_e"]
        latmin = bbox_ll["ll_s"]
        latmax = bbox_ll["ll_n"]

    # get start time last entry of a STAC collection
    if s:
        # get end date of temporal extent of STAC collection
        collection = pystac.Collection.from_file(stac_collection)
        temp_extent = collection.extent.temporal.intervals
        end_stac_extent = temp_extent[0][1]
        # check if end time is None
        if end_stac_extent is None:
            # stop processing
            grass.fatal("No end time found in STAC collection")

        # overwrite start and end date for filtering range
        start_tmp = end_stac_extent + datetime.timedelta(days=1)
        start = start_tmp.strftime("%Y-%m-%d")
        end = datetime.date.today().strftime("%Y-%m-%d")

    # define search criteria
    search_criteria = {
        "provider": "cop_dataspace",
        "collection": "S2_MSI_L2A",
        "start": start,
        "end": end,
        "geom": {
            "lonmin": float(lonmin),
            "latmin": float(latmin),
            "lonmax": float(lonmax),
            "latmax": float(latmax),
        },
        "eo:cloud_cover": cloud_cover,
    }

    # add tile ID to search criteria
    if tile_id:
        search_criteria["grid:code"] = f"MGRS-{tile_id}"

    # initialize EODataAccessGateway
    dag = EODataAccessGateway()

    # search for S2 scenes matching the criteria
    all_products = dag.search_all(**search_criteria)

    # extract S2 IDs from search results
    result = {
        all_products[i].properties["id"]: {
            "acquisition_date": all_products[i].properties["datetime"],
            "cloud_cover": all_products[i].properties["eo:cloud_cover"],
            "tile_id": all_products[i].properties["grid:code"].split("-")[1],
        }
        for i in range(len(all_products))
    }

    if len(result) == 0:
        grass.message(
            "No Sentinel-2 scenes found matching the search criteria.",
        )
        return

    if p:
        grass.message("-----------------------------")
        grass.message("Search results:")
        grass.message("-----------------------------")
        for key, value in result.items():
            grass.message(
                f"S2 ID: {key}\n Acquisition Date: {value['acquisition_date']}"
                f"\n Cloud Cover: {value['cloud_cover']}%\n Tile ID:"
                f"{value['tile_id']}",
            )
            grass.message("-----------------------------")
    # if output path is provided, write result to file
    elif output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
    else:
        # write result to stdout
        sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
