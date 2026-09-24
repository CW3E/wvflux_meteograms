#!/bin/bash

for product in watervaporflux_3day_meteogram watervaporflux_7day_meteogram rh_3day_meteogram rh_7day_meteogram
do

 for model in GFS_25 ECMWF_HRes
 do
  cd "/data/projects/website/mirror/htdocs/images/${product}/v1/${model}/"

  for lat in {26..69}; do
   echo $lat

   for domain in "${lat}N"*
   do
    echo "${product} ${model} ${domain}"
    rm -rf "/data/projects/website/mirror/htdocs/images/${product}/v1/${model}/${domain}/202604"* &
   done
   wait
  done
 done
done



exit