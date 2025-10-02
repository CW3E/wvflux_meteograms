#!/bin/bash
F=$1
fdate=$2
sbatch <<EOF
#!/bin/bash
#SBATCH --account=cwp186
#SBATCH --partition=shared-128
#SBATCH --job-name=preprocess_F${F}
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=logs/preprocess_F${F}_%j.out

echo "Starting preprocess for lead time ${F}"
python preprocess.py --leadtime ${F} --init_date ${fdate}
EOF
