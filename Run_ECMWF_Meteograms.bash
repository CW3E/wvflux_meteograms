#!/bin/bash

date=`date`
echo "STARTING AT "$date

lag=6
yyyy=`date -d '-'$lag' hours' -u +%Y`
mm=`date -d '-'$lag' hours' -u +%m`
dd=`date -d '-'$lag' hours' -u +%d`
hh=`date -d '-'$lag' hours' -u +%H`

rm -f /data/projects/operations/wvflux_meteograms/figs/ECMWF/*.png

ftimes=(000 003 006 009 012 015 018 021 024 027 030 033 036 039 042 045 048 051 054 057 060 063 066 069 072 075 078 081 084 087 090 093 096 099 102 105 108 111 114 117 120 123 126 129 132 135 138 141 144 150 156 162 168)

for FT in "${ftimes[@]}"; do
 echo "Running "$yyyy$mm$dd$hh "F-"$FT
 IVTfile="/data/projects/derived_products/ECMWF_IVT/Deterministic/"$yyyy$mm$dd$hh"/ECMWF_IVT_"$yyyy$mm$dd$hh"_F${FT}.nc"
 while true; do
   if [[ -e "$IVTfile" ]]; then         # Check if the file exists
     filesize1=$(stat --format="%s" "$IVTfile")   # Get the file size
     sleep 1  #10                             # Wait a few seconds
     filesize2=$(stat --format="%s" "$IVTfile")   # Get the file size again

     if [[ "$filesize1" == "$filesize2" ]]; then   # Compare file sizes
       break                    # Exit the loop if file size is not changing
     else
       echo $IVTfile" is still being written (file size is changing)."
     fi
   else
     echo $IVTfile" does not exist."
     sleep 30
   fi
 done
 echo $IVTfile" ready for processing"
done


cd /data/projects/operations/wvflux_meteograms

date=`date`
echo "STARTING PLOTS AT "$date

singularity exec --bind /data:/data -e /data/projects/operations/wvflux_meteograms/envs/wvflux_meteograms.sif /opt/conda/envs/container/bin/python /data/projects/operations/wvflux_meteograms/run_tool_parallel.py "ECMWF" "$yyyy$mm$dd$hh"

date=`date`
echo "FINISHED PLOTS AT "$date

cd /data/projects/operations/wvflux_meteograms/figs/ECMWF

chmod 664 *.png
for filename in watervaporflux_3day_meteogram__v1__ECMWF_HRes__*
do
 domain=`echo $filename | awk -F'__' '{print $4}'`
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p -m 2775 "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mv "watervaporflux_3day_meteogram__v1__ECMWF_HRes__${domain}"* "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "watervaporflux_7day_meteogram__v1__ECMWF_HRes__${domain}"* "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_3day_meteogram__v1__ECMWF_HRes__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_7day_meteogram__v1__ECMWF_HRes__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 wait
done

lag=30
yyyyP=`date -d '-'$lag' days' -u +%Y`
mm=P`date -d '-'$lag' days' -u +%m`
ddP=`date -d '-'$lag' days' -u +%d`
cd "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/ECMWF_HRes/"
for domain in *
do
 rm -rf "/data/projects/website/mirror/htdocs/images/watervaporflux_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/watervaporflux_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/ECMWF_HRes/${domain}/${yyyyP}${mmP}${ddP}"* &
 rm -rf "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/ECMWF_HRes/${domain}/${yyyyP}${mmP}${ddP}"* &
 wait
done

date=`date`
echo "FINISHED AT "$date

exit