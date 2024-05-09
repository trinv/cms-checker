## CMS Checker (CMS is Content Management Software)
This tool allows you to check a list of websites if they have CMS installed with various useful information
also it provide a url contain a list of possible vulnerabilities related to that version.
## Usage
`python2 cms-checker.py -l [List of Urls] -t [# of Threads]`

### 1. Install python virtualenv dependencies packages
```
apt-get install python-virtualenv
apt-get install python3-virtualenv
apt get install virtualenv
```

### 2. Create a Virtual Environment
```
cd /home/ubuntu
virtualenv -p /usr/bin/python2 cms-env
```

### 3. Activate The Virtual Environment
```
cd /home/ubuntu/cms-env/bin
source activate
```

### 4. Downloading or Clone the packages

`git clone https://github.com/trinv/cms-checker.git`

### 5. Dependencies
Installation on Linux:

`sudo pip2 install -r requirements.txt`

### 6. Run
```
cd /home/ubuntu/cms-env/bin/cms-checker
python2 cms-checker.py -l [List of Urls] -t [# of Threads]
```
### 7. Images

![Output](https://i.imgur.com/70U7XUB.png)

