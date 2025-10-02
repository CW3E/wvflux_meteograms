#!/bin/bash
#SBATCH --account=cwp140
#SBATCH --partition=shared-128
#SBATCH --job-name=preprocess_F
#SBATCH --output=logs/preprocess_F_%A_%a.out
#SBATCH --error=logs/preprocess_F_%A_%a.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --mail-type=ALL # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user=dnash@ucsd.edu # Email to which notifications will be sent
#SBATCH --array=0-56   # 57 tasks (0..56) -> F=0..168 every 3

# Compute lead time
F=$(( SLURM_ARRAY_TASK_ID * 3 ))

# Run Python script
/home/dnash/miniconda3/envs/SEAK-impacts/bin/python -u preprocess.py --leadtime ${F} --init_date "2025093000"
