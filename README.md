

#INITIAL STEPS: ADJUSTING THE DEVELOPMENT ENVIRONMENT

This step demonstates how to update your vagrant configuration for the appropriate forward ports 

1. From your command line interface (git bash recommmeneded), go to the appropriate folder where you would like to setup and run the application and files.
2. Once there, run vagrant environment (or setup a new vagrant environment using "vagrant init" and the virtualbox preferred--in this case "ubuntu/trusty32"). Type "vagrant init ubuntu/trusty32". If you are just setting up a vagrant environment be sure to adjust the Vagrantfile and add the following provisioning and configuration information:

  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 8090, host: 8090

The second configuration line adjustment modifies the setup forward ports to include forward port 8090--which is the forward port the application is written to run on from the localhost.

2. Run the following commands from the command line to install the appropriate programs that the application will utilize. Wait for the applications to download and install before proceeding with the next command. 

	a. apt-get -qqy install postgresql python-psycopg2
	b. apt-get -qqy install python-flask python-sqlalchemy
	c. apt-get -qqy install python-pip
	d. pip install bleach
	e. pip install oauth2client
	f. pip install requests
	g. pip install httplib2


#STEP 1: CREATE DATABASE

1. In command line go to folder "catalog" in directory.
2. Run "psql" to start postgres
3. Once open type "CREATE DATABASE model;" where "model" is the name of the database being created for the application.
4. Next exit psql and return the directory folder and command line interface.
5. In your text editor, open the "database_setup.py" file and make sure line that the line
		engine = create_engine('postgresql:///model')
	is set to 'postgresql:///model' which is the name of the database you just created in psql.

6. Setup of the database using the "database_setup.py" file by typing command "python database_setup.py" This will run the file that uses Sqlachemy as the ORM to setup the database tables and columns.


#STEP 2: POPULATE DATABASE WITH DATA

I have created some JSON data to populate the newly setup database with data initially. from the catalog log folder in the VM directory, run "python populate_database.py" from the command line.



#STEP 3: RUNNING THE APPLICATION

1. From the command line, run the file "python runserver.py".

This should allow the application to run in the web browser under localhost://9080

For reference, some of the other keys files include the views.py file which contains all the views for the web application.
