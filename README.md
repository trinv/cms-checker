## CMS Checker (CMS is Content Management Software)
This tool allows you to check a list of websites if they have CMS installed with various useful information
also it provide a url contain a list of possible vulnerabilities related to that version.
## Usage
`python2 cms-checker.py -l [List of Urls] -t [# of Threads]`

### 1. Install python virtualenv dependencies packages
```
apt-get install python3-virtualenv
apt-get install virtualenv
apt-get install python3-bs4
apt-get install python3-pyfiglet
apt-get install python3-termcolor
```
### 2. Checkout source code and create virtualenv

```
git clone https://github.com/trinv/cms-checker.git /opt/cms-checker
cd /opt/cms-checker
python3 -mvenv ./venv
```

### 3. Activate your python3 environment and install libraries:
```
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run
```
python3 cms-checker.py -l [List of Urls] -t [# of Threads]
```
### 5. Images

![Output](https://i.imgur.com/70U7XUB.png)

