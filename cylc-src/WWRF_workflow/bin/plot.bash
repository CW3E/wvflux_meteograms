#!/bin/bash
SITE=$1
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=plot_${SITE}
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --output=logs/plot_${SITE}_%j.out

echo "Starting plot for site ${SITE}"
python plot.py --site ${SITE} --indir ./tempdata --outdir ./plots
EOF

# /home/dnash/miniconda3/envs/SEAK-impacts/bin/python -u plot.py --site 0