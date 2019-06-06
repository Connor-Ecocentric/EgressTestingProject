serial="$(more /media/sdcard/config.ini | grep client_id | awk '{print $3}')"
secret="$(more /media/sdcard/config.ini | grep client_secret | awk '{print $3}')"

cp /home/root/config/config.ini /media/sdcard/config.ini
cp /home/root/config/config.ini.default /media/sdcard/config.ini.default

sed -i "s/^client_id.*/client_id                         = ${serial}/g" /media/sdcard/config.ini
sed -i "s/^client_secret.*/client_secret                     = ${secret}/g" /media/sdcard/config.ini

cp /media/sdcard/config.ini /home/root/config.bak
more /media/sdcard/config.ini