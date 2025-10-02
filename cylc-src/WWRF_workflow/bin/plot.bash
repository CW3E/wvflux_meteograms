#!/bin/bash
SITE=$1
sbatch <<EOF
#!/bin/bash
#SBATCH --account=cwp186
#SBATCH --partition=shared-128
#SBATCH --job-name=plot_${SITE}
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=logs/plot_${SITE}_%j.out

echo "Starting plot for site ${SITE}"
module load singularitypro
singularity exec --bind /cw3e:/cw3e /cw3e/mead/projects/cwp186/repos/wvflux_meteograms/envs/wvflux_meteograms.sif /cw3e/mead/projects/cwp186/repos/wvflux_meteograms/cylc-src/WWRF_workflow/bin/plot.py --site ${SITE}
EOF

# /home/dnash/miniconda3/envs/SEAK-impacts/bin/python -u plot.py --site 0