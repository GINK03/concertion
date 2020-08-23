export GUNICORN_PATH=`which gunicorn` 
echo $GUNICORN_PATH
sudo /sbin/setcap 'cap_net_bind_service=+ep' $GUNICORN_PATH
export PYTHON_PATH=`which python3` 
echo $PYTHON_PATH
sudo /sbin/setcap 'cap_net_bind_service=+ep' $PYTHON_PATH

# for pyenv.
sudo setcap 'cap_net_bind_service=+ep' $PYTHON_PATH
sudo setcap 'cap_net_bind_service=+ep' $GUNICORN_PATH
