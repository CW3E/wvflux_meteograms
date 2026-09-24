#!/bin/bash

yyyy="2026"
mm="09"
dd="24"
hh="00"

cd /data/projects/operations/wvflux_meteograms

date=`date`
echo "STARTING PLOTS AT "$date

singularity exec --bind /data:/data -e /data/projects/operations/wvflux_meteograms/envs/wvflux_meteograms.sif /opt/conda/envs/container/bin/python /data/projects/operations/wvflux_meteograms/run_tool_parallel.py "GFS" "$yyyy$mm$dd$hh"

date=`date`
echo "FINISHED PLOTS AT "$date


cd /data/projects/operations/wvflux_meteograms/figs/GFS

chmod 664 *.png
for filename in watervaporflux_3day_meteogram__v1__GFS_25__*
do
 domain=`echo $filename | awk -F'__' '{print $4}'`
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mv "watervaporflux_3day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "watervaporflux_7day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_3day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_7day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 wait
done

lag=30
yyyyP=`date -d '-'$lag' days' -u +%Y`
mm=P`date -d '-'$lag' days' -u +%m`
ddP=`date -d '-'$lag' days' -u +%d`

cd "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/GFS_25/"
for domain in *
do
 rm -rf "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/GFS_25/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/GFS_25/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/GFS_25/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/GFS_25/${domain}/${yyyyP}${mmP}${ddP}"* &
 wait
done

date=`date`
echo "FINISHED AT "$date

exit