# Integrated Water Vapor Transport (IVT) and Relative Humidity Time-Height Meteograms

---

This repository runs calculations and plots for the CW3E IVT and Relative Humidity time-height meteograms for GFS and ECMWF. 

Current capabilities includes point-based 3- or 7-day deterministic forecasts for GFS or ECMWF every degree from 20-60°N and 111-127°W and from 51-69°N and 130-174°W.

## To run:

---

To run all points for each model:

```bash
## runs plots for GFS
singularity exec --bind /data:/data,/home:/home,/work:/work,/common:/common -e /data/projects/operations/wvflux_meteograms/envs/wvflux_meteograms.sif /opt/conda/envs/container/bin/python /data/projects/operations/wvflux_meteograms/run_tool_parallel.py "GFS"

## runs plots for ECWMF
singularity exec --bind /data:/data,/home:/home,/work:/work,/common:/common -e /data/projects/operations/wvflux_meteograms/envs/wvflux_meteograms.sif /opt/conda/envs/container/bin/python /data/projects/operations/wvflux_meteograms/run_tool_parallel.py "ECMWF"
```