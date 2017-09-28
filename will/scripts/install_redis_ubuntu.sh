sudo apt install tcl
wget http://download.redis.io/releases/redis-latest.tar.gz
wget http://download.redis.io/releases/redis-stable.tar.gz
tar -xvzf redis-stable.tar.gz
cd redis-stable/
make
make install
sudo make install
cd ..
./start_dev_will.py
ping localhost
telnet localhost:6379
telnet localhost -p 6379
telnet localhost 6379
ps aux | grep -i redis
cd redis-stable/
cd utils
sudo ./install_server.sh
