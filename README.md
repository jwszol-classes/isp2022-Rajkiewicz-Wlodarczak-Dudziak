[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-c66648af7eb3fe8bc4f294546bfd86ef473780cde1dea487d3c4ff354943c9ae.svg)](https://classroom.github.com/online_ide?assignment_repo_id=10088939&assignment_repo_type=AssignmentRepo)

# Application visualizing airplanes in Poland
The project involved the use of AWS to visualize aircraft located in Poland


### Used technologies and data flow
![diagram](https://github.com/jwszol-classes/isp2022-Rajkiewicz-Wlodarczak-Dudziak/blob/main/technologies.png)

### OpenSky
Airplanes data are downloaded from OpenSky.

### AWS EC2 Instance
Inside the EC2 instance, there are programs responsible for downloading data about airplanes,
sending them via kinesis, and placing them in the database. The EC2 also runs a Flask server,
which allows visualization the airplanes through a browser.

### Kinesis data stream
Kinesis data stream gets data about airplanes and distribute them to different shards. Shards then send data to RDS database.

### Amazon RDS
Amazon RDS provides a database where aircraft data is stored, which is then loaded into the visualization.

### Flask Server
It allows you to launch a website responsible for visualization.

### Leaflet
Open-source JavaScript library for mobile-friendly interactive maps.

### OpenStreetMap
An online community project to create a free, freely available map of the entire globe.

### Airplanes visualization
![diagram](https://github.com/jwszol-classes/isp2022-Rajkiewicz-Wlodarczak-Dudziak/blob/main/airplanesVisualization.png)

# Setup AWS services

### Create EC2 Instance
* Go to EC2 service
* Click **Launch instance**
* Choose Instance name
* Choose **Ubuntu** system
* Create new key pair -> Select .ppk format -> Create key pair
* Click **Launch**

### Allocate Elastic IP
* Go to EC2 service
* In **Network & Security** -> Elastic IPs
* Click Allocate Elastic IP address -> Allocate
* Select created Elastic IP adress
* Click **Actions**
* Click **Associate Elastic IP address** -> Instance -> Select created EC2 Instance -> Associate


### Create RDS Database
* Go to RDS service
* Click **Create database**
* Choose **PostgreSQL** engine
* Choose **Free Tier** template
* Choose DB cluster identifier
* Choose Master username
* Choose Master password
* Select **Connect to an EC2 compute resource** -> Select created EC2 Instance
* Select **Create new VPC security Group** -> Enter new VPC security group name
* Click **Create Database** 


### Adjust EC2 Instance Inbound Rules
* Go to EC2 service
* Click **Security**
* Click Security group (for example "sg-0d6217ad993ec8181 (ec2-rds-2)")
* Click **Edit inbound rules**
* Click **Add rule**
* Select **Custom TCP** Type 
* Choose **8080** Port range
* Choose **Custom** Source type
* Select **0.0.0.0** Source
* Click **Save rules**

### Connect with EC2 instance through PuTTY
* open **PuTTY**
* In **Category** window go to Connection/Data/ and fill Auto-login with "ubuntu"
* In **Category** window go to Connection/SSH/Auth and browse for earlier downloaded .ppk key file
* in **Category** window go to Session and fill Host Name (or IP address) inputbox (for example "ec2-18-209-77-177.compute-1.amazonaws.com")
* click **Open**
* on PuTTY Security Alert popup window choose **tak**

### EC2 Instance setup - configure git
* Generate ssh keys:
```
ssh-keygen -o
```
* Push **enter** button for each communicate (3 times)
* Show public key
```
cat ~/.ssh/id_rsa.pub
```
* Log in to **github** service
* Go to **Settings**
* Click SSH and GPG keys
* Click **New SSH key**
* Provide **Key** (generated public key)
* Click **Add SSH key**

### EC2 Instance setup - clone repository
Download repository
```
git clone git@github.com:jwszol-classes/isp2022-Rajkiewicz-Wlodarczak-Dudziak.git
cd isp2022-Rajkiewicz-Wlodarczak-Dudziak/
```

### Instance setup - software instalations

#### AWS instalation:
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
	
* create folder .aws in following path:
```
\home\ubuntu\
```

* Open labs.vocareum page
* Click **Account Details**
* Click **show** under **AWS CLI**
* Copy displayed text
* Paste it into
```
\home\ubuntu\.aws\credentials
```

* paste following text 
```
[default]
region = us-east-1
output = json
```
into
```
\home\ubuntu\.aws\config:
```

#### Opensky instalation:
https://github.com/openskynetwork/opensky-api


#### Packages instalation:
To install all required packages, copy and paste every single command below into EC2 Instance terminal in order:
```
sudo apt update
sudo apt install python3-pip
pip install boto3
pip install boto
pip install SQLAlchemy
pip install --force-reinstall 'sqlalchemy<2.0.0'
sudo apt install libpq-dev python3-dev
pip install psycopg2
sudo apt install postgresql-client-common
sudo apt-get install postgresql-client
pip install flask
```

### Project launch:
* Go to repository folder ("isp2022-Rajkiewicz-Wlodarczak-Dudziak/")

#### Opensky credentials
Required OpenSky account: https://opensky-network.org/
* Open opensky_credentials.json file
* Set your username and password values in proper keys

#### Database credentials

* Open database_credentials.json file
* Set proper values in proper keys
* as user, provide **Database Master User** username
* as password, provide **Database Master User** password
* as host, provide **Endpoint** (for example "test-database.co37l7odeo9c.us-east-1.rds.amazonaws.com")
* as database, provide "postgres"
* as port, provide **database port** (for example "5432")

#### Create Kinesis Stream
* Use below command:
```
aws kinesis create-stream --stream-name stream_0 --shard-count 1 --region us-east-1
```

#### Launch Producer program
* Use below command:
```
python3 producer.py
```
#### Launch Consumer programs
It requires launching several EC2 Instance Sessions. In each session:
* Go to repository folder ("isp2022-Rajkiewicz-Wlodarczak-Dudziak/")
* Use below command:
```
python3 consumer.py INDEX
```
Where "INDEX" is number 0..2. For every Session use different "INDEX".

#### Launch Visualization program
It requires launching another EC2 Instance Session.
* Go to repository folder ("isp2022-Rajkiewicz-Wlodarczak-Dudziak/")
* Use below command:
```
python3 visualization.py
```
* Open web browser
* In web browser, type EC2 Instance Public IPv4 address with port 8080 (for example 18.209.77.177:8080)

There should be displayed airplanes visualization like in image in **Airplanes visualization** section.

