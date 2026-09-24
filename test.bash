#!/bin/bash

yyyy="2026"
mm="04"
dd="01"
hh="06"

cd /data/projects/operations/wvflux_meteograms/figs/GFS

rename GFS_3DayWVFlux_ waterwaporflux_3day_meteogram__v1__GFS_25__ GFS_3DayWVFlux_*
rename .png "__${yyyy}${mm}${dd}${hh}__1__.png" waterwaporflux_3day_meteogram__v1__GFS_25__*

rename GFS_3DayRH_ rh_3day_meteogram__v1__GFS_25__ GFS_3DayRH_*
rename .png "__${yyyy}${mm}${dd}${hh}__1__.png" rh_3day_meteogram__v1__GFS_25__*

rename GFS_7DayWVFlux_ waterwaporflux_7day_meteogram__v1__GFS_25__ GFS_7DayWVFlux_*
rename .png "__${yyyy}${mm}${dd}${hh}__1__.png" waterwaporflux_7day_meteogram__v1__GFS_25__*

rename GFS_7DayRH_ rh_7day_meteogram__v1__GFS_25__ GFS_7DayRH_*
rename .png "__${yyyy}${mm}${dd}${hh}__1__.png" rh_7day_meteogram__v1__GFS_25__*


for filename in waterwaporflux_3day_meteogram__v1__GFS_25__*
do
 domain=`echo $filename | awk -F'__' '{print $4}'`
 echo $domain
 mkdir -p "/data/projects/website/mirror/htdocs/images/waterwaporflux_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p "/data/projects/website/mirror/htdocs/images/waterwaporflux_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mkdir -p "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1"
 mv "waterwaporflux_3day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/waterwaporflux_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "waterwaporflux_7day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/waterwaporflux_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_3day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_3day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 mv "rh_7day_meteogram__v1__GFS_25__${domain}"* "/data/projects/website/mirror/htdocs/images/rh_7day_meteogram/v1/GFS_25/${domain}/${yyyy}${mm}${dd}${hh}/1/" &
 wait
done


exit