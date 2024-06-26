# Survivor Draft

A web application written in Django for visualizing & interacting with survivor drafts.

Organized by season, each season has a set of teams with a team owner & name. Each team has a set of survivors as drafted by that team owner. Each survivor has data associated with them pertaining to their performance on that season of survivor.

Survivor data includes overall placement, number of immunities won, idols found, confessionals featured in, fan favorite winner.

Currently being hosted at https://outdraft.me, but you can also host your own.
## Installation
The project comes with a Docker compose.yaml file for running a multi-container application. Alternatively you may set it up manually. By nature, the Docker instructions should be consistent across operating systems (other than installing Docker itself), but the manual instructions may vary slightly depending on the operating system.

### Installation (Docker)
1. Install Docker
2. Add an encryption key & cert file. Lots of ways to acquire one, for example, see https://letsencrypt.org/
3. Configure .env file (see step 4 of the Non-Docker steps for an explanation of the variables)
4. Run 'docker compose up'
5. Subsequent runs after code changes should run 'docker compose up --build' to ensure a new image is built with the updated code
6. The database migration step was removed from the Dockerfile, as it wasn't running on the DB living in the volume, & it apparently isn't best practice to automatically run database migrations anyway. So, if necessary, run the database migration (you'll know you need to if your server spits out ugly 500 response codes when trying to get to it):
  * open a shell within the Docker container. `docker container list` should show you the running containers, then `docker exec -it containername bash` will open a shell within it
  * run `python manage.py migrate`

### Installation (Legacy, Non-Docker)

1. Install Python 3.11 or higher.
2. Add an encryption key & cert file. Lots of ways to acquire one, for example, see https://letsencrypt.org/
3. Create a virtual environment
  > python -m venv .venv
  
  Then activate it
  
  > .venv\Scripts\activate
  
  The rest of the steps assume running within this environment.
3. Use Pip to install the requirements
  > python -m pip install -r 'requirements.txt'
4. Configure environment variables
  
  This project uses python-dotenv to pull environment variables from a '.env' file first before system environment variables. This allows you to utilize a file to configure your environment. You can do this by copying the `web_project/.env.sample` file into a `web_project/.env` file, & then modifying the contents of the environment variables within as appropriate. Descriptions of existing environment variables are as follows:
  * DJANGO_SURVIVOR_PROD: If present & 'true', the instance will run in production mode. This means a different secret key will be used, the allowed hosts will be different, the channel layers backend will be different, & the application will be HTTPS-only. If not present or not 'true', the server will run in debug/developer mode.
  * SECRET_KEY_DEV: The secret key that developer mode runs with
  * SECRET_KEY: The secret key that prod mode runs with
  * DJANGO_SURVIVOR_CERTFILE: The path to the certfile to use for encryption
  * DJANGO_SURVIVOR_KEYFILE: The path to the keyfile to use for encryption
  * Email things:
    * DJANGO_SURVIVOR_EMAIL_ENABLED: if 'true', will use emails to send password resets. Otherwise password reset requests just go right to console. Implemented as a stop-gap while getting email working.
      * If not configured or not 'true', all of the below email settings can be ignored.
    * DJANGO_SURVIVOR_EMAIL_HOST: the host to use for sending emails, likely an SMTP server
    * DJANGO_SURVIVOR_EMAIL_PORT: the port to use for sending emails
    * DJANGO_SURVIVOR_EMAIL_USER: the user (email address) to use for sending emails
    * DJANGO_SURVIVOR_EMAIL_PASSWORD: the password for the user used for sending emails
    * DJANGO_SURVIVOR_EMAIL_KEYFILE: path to an SSL keyfile used for encrypting emails (only necessary if EMAIL_USE_TLS or EMAIL_USE_SSL is True)
    * DJANGO_SURVIVOR_EMAIL_CERTFILE: path to an SSL certfile used for encrypting emails (only necessary if EMAIL_USE_TLS or EMAIL_USE_TLS is True)
5. If running in prod, the Django Channels backend is Redis (https://redis.io/docs/install/). The default settings just point to a Redis install on the default port on the same machine, but you can configure that if preferred.
6. If running in prod, the application is configured to always be HTTPS. You will need to get a cert & a key & point the server to those files when running it.
7. If running in prod, you will need to adjust the ALLOWED_HOSTS field in the top-level settings.py file to match the IP or domain you are hosting from.
8. Run the migration
  > python manage.py migrate

This will create the database file & then migrate it to its intended state.
9. Collect the static files
  > python manage.py collectstatic
10. Create a superuser
  > python manage.py createsuperuser -- username=yourUsername --email=yourEmail
  
  This will be useful in managing the database - creating seasons, survivors, etc. You can later access the administrative interface through the `/admin` path, logging in with these credentials. 
11. Run the server
  > python manage.py runserver
  
  This will be useful in running the server for development purposes, but if you're running it in prod, you should use a proper server.
12. Run the server in prod
  > daphne -e ssl:443:privateKey=<pathToPrivateKey.pem>:certKey=<pathToCert.pem> web_project.asgi:application
  
  This will cause the Daphne (https://github.com/django/daphne) server to run the web_project.asgi application using the private key & cert provided. Daphne is necessary to make use of the secure websockets that the live draft depends upon - before that functionality, I used to host using Gunicorn (as of writing the Gunicorn config file is still in the repo).

## Use
Once the server is running, it may not actually work - I haven't tested the homepage with an empty DB yet, but I imagine it may complain about some empty tables. First steps:
1. Go to the /admin endpoint & login.
2. Create a Survive Rubric. The default values are probably fine for now, but this is where you'd configure how a season is scored.
3. Create a Survive Season. This is the place that draft teams will live.
  * Use the rubric you just created
  * The opening date would usually be the day the first episode is aired, & the closing date would be the day the last episode airs.
  * The 'Survivor drafting' checkbox determines whether the draft is currently live. When checked, participating teams will have the option to draft survivors. Leave unchecked when a draft is not actively happening.
  * The 'Team Creation' checkbox determines whether a user can make a team for this season if they don't currently have one. Usually, only one of this or 'Managed Season' should be checked.
  * The 'Managed Season' checkbox dictates whether a season is 'managed' by a Team within the season with the 'Draft Owner' checkbox selected. Usually, only one of this or 'Team Creation' should be checked. Season managers have access to the Manage Season page, where they can invite users & delete teams from a season - useful for allowing users to manage their seasons completely free of admin assistance.
  * Other seasons can be associated with a season - for instance, if two groups of people are running separate drafts for the same season. Associated seasons can be viewed together on the homepage.
  * The final field is the current place in the draft, if draft ordering is being enforced. Set this to '-1' for a free for all draft. Default of '1' indicates that the draft is on the first pick.
4. Create Tribes & put 'em in the season
  * Each tribe is basically just a name & a color, & survivors can be associated with it to give them a border around their profile pics
5. Create Survivors to put in the season
  * Give 'em a name
  * Each survivor should know the season they belong to
  * If tribes have been created, you can assign this survivor to their tribe
  * The 'Pic' & 'Pic Full' fields don't quite work at this point in time, because media uploads don't quite work. Instead these are just used as string paths to the file locations on the static file server. No way to properly configure this through the admin console - I use the DB Browser for SQLite to do database manipulation when I need to.

With all this done, now the server should have at least one proper season, complete with a bunch of undrafted survivors. Now you'll need users to come sign up & make teams to participate in the draft.

## Steps before Deploy
I haven't properly built up a build pipeline yet, so the deployment steps that I run manually are starting to add up. For now, here's a list of things that can/should be run before making a pull request/running it:
1. Run unittests with `python manage.py test survive`
2. Run the server, then run Cypress tests using `npx cypress run`
3. Run MyPy with `mypy .` & check for typing errors
4. Run Black with `black .` to format new code
