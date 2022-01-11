wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -zxvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
sudo make
sudo make install
cd ../
sudo rm -rf ta-lib-0.4.0-src.tar.gz
sudo rm -rf ta-lib
pip install TA-Lib