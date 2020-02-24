export GUNICORN_PATH=`which gunicorn` 
echo $GUNICORN_PATH
sudo /sbin/setcap 'cap_net_bind_service=+ep' $GUNICORN_PATH
export PYTHON_PATH=`which python3` 
echo $PYTHON_PATH
sudo /sbin/setcap 'cap_net_bind_service=+ep' $PYTHON_PATH

# for pyenv.
sudo setcap 'cap_net_bind_service=+ep' $HOME/.pyenv/versions/3.8.1/bin/python3.8
sudo setcap 'cap_net_bind_service=+ep' $HOME/.pyenv/versions/3.8.1/bin/gunicorn 
