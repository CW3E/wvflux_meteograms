#!/bin/bash
SITE=$1
FDATE=$2
sbatch <<EOF
#!/bin/bash
#SBATCH --account=cwp186
#SBATCH --partition=shared-128
#SBATCH --job-name=site_preprocess_${SITE}
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=logs/site_preprocess_${SITE}_%j.out

echo "Creating site-specific NetCDF for ${SITE}"
module load singularitypro
singularity exec --bind /cw3e:/cw3e /cw3e/mead/projects/cwp186/repos/wvflux_meteograms/envs/wvflux_meteograms.sif \
/cw3e/mead/projects/cwp186/repos/wvflux_meteograms/cylc-src/WWRF_workflow/bin/extract_site.py \
    --site ${SITE} \
    --init_date ${FDATE} \
EOF

# /home/dnash/miniconda3/envs/SEAK-impacts/bin/python -u extract_site.py --site 0 --init_date "2025100100"
