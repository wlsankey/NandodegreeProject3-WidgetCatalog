BRIEF DESCRIPTION OF APPLICATION:
This web application is called Widget Catalog. It allows users to input categories and assign items to those categories. 

The homeplage (localhost://9080) displays a images of popular items in the databse ranked ranked by the number of visits. The sidebar displays the most popular categories by the number of visits.

The page localhost://9080/category/all displays a list of all categories in the database in alphabetical order.



#INITIAL STEPS: ADJUSTING THE DEVELOPMENT ENVIRONMENT

This step demonstates how to update your vagrant configuration for the appropriate forward ports 

1. From your command line interface (git bash recommmeneded), go to the appropriate folder where you would like to setup and run the application and files.

2. Once there, run vagrant environment (or setup a new vagrant environment using "vagrant init" and the virtualbox preferred--in this case "ubuntu/trusty32"). Type "vagrant init ubuntu/trusty32". If you are just setting up a vagrant environment be sure to adjust the Vagrantfile and add the following provisioning and configuration information:
  
  config.vm.provision "shell", path: "pg_config.sh"
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 9080, host: 9080

  (Note that if you already using these forward ports, please select another unused port number and adjust the app accordingly to run on that port: Adjust the runserver.py file)

The second configuration line adjustment modifies the setup forward ports to include forward port 9080--which is the forward port the application is written to run on from the localhost.


1. "vagrant ssh" -- enter your secure linux shell.
2. Move within the directory to the top of the downloaded respoitory directory.


#STEP 1: CREATE DATABASE

1. In command line go to the top folder in the downloaded repository in the directory.
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
