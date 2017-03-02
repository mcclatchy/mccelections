# conditional to see if already activated?
# if [pwd != ~/mccelections/electionsproject] ; then
# 	workon mccelections && cd ~/mccelections/electionsproject

# BACKUP MIGRATIONS
cp ~/mccelections/electionsproject/results/migrations/0* ~/migrationsbackup/

# PULL REPO and UPDATE SETTINGS
git pull origin master && cp ~/mccelections/electionsproject/electionsproject/settings_prod.py ~/mccelections/electionsproject/electionsproject/settings.py # && cd ~/mccelections/electionsproject 

# RELOAD MIGRATIONS
rm ~/mccelections/electionsproject/results/migrations/0* && cp ~/migrationsbackup/00* results/migrations/

# MAKE MIGRATIONS + MIGRATE
python ~/mccelections/electionsproject/manage.py makemigrations && python ~/mccelections/electionsproject/manage.py migrate

# REBOOT SERVER
# sudo reboot

