#!/bin/bash
SITE=$1
FDATE=$2
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=site_preprocess_${SITE}
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=logs/site_preprocess_${SITE}_%j.out

echo "Creating site-specific NetCDF for ${SITE}"
python extract_site.py \
    --site ${SITE} \
    --init_date ${FDATE} \
EOF

# /home/dnash/miniconda3/envs/SEAK-impacts/bin/python -u extract_site.py --site 0 --init_date "2025100100"
