#!/bin/bash

date=`date`
echo "STARTING AT "$date

lag=8  #3
yyyy=`date -d '-'$lag' hours' -u +%Y`
mm=`date -d '-'$lag' hours' -u +%m`
dd=`date -d '-'$lag' hours' -u +%d`
hh=`date -d '-'$lag' hours' -u +%H`

rm -f /data/projects/operations/wvflux_meteograms/figs/GFS/*.png

filename="/data/projects/external_datasets/GFS/processed/"$yyyy$mm$dd$hh"/"$yyyy$mm$dd$hh"_F168.grb2"
while true; do
  if [[ -e "$filename" ]]; then         # Check if the file exists
    filesize1=$(stat --format="%s" "$filename")   # Get the file size
    sleep 10                             # Wait a few seconds
    filesize2=$(stat --format="%s" "$filename")   # Get the file size again

    if [[ "$filesize1" == "$filesize2" ]]; then   # Compare file sizes
      break                    # Exit the loop if file size is not changing
    else
      echo $filename" is still being written (file size is changing)."
    fi
  else
    echo $filename" does not exist."
    sleep 30
  fi
done

echo $filename" ready for processing"

cd /data/projects/operations/wvflux_meteograms

date=`date`
echo "STARTING PLOTS AT "$date

singularity exec --bind /data:/data,/home:/home,/work:/work,/common:/common -e /data/projects/operations/wvflux_meteograms/envs/wvflux_meteograms.sif /opt/conda/envs/container/bin/python /data/projects/operations/wvflux_meteograms/run_tool_parallel.py "GFS" "$yyyy$mm$dd$hh"

date=`date`
echo "FINISHED PLOTS AT "$date

cd /data/projects/operations/wvflux_meteograms/figs/GFS/
try=1
while [ $try -le 5 ]; do
 timeout 240 rsync --ignore-missing-args -avih GFS_* /data/projects/website/mirror/htdocs/images/gfs/Meteograms/
 if [ $? -eq 0 ]; then
  break
 fi
 try=$((try + 1))
 sleep 5
done

date=`date`
echo "FINISHED AT "$date

exit

