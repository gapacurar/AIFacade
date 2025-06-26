-- to run migrate you first have to set env variable FLASK_APP:
    PowerShell(windows):
        $env:FLASK_APP = "project:create_app"
-- After that we can use commands like
flask db init
flask db migrate
flask db upgrade
flask init-db
--- if it gets bugged you can delete the new migration folder entirely and redo these steps
--- And we start fresh after setting the env var again with:
flask db init
flask db migrate -m "initial"
flask db upgrade
flask init-db


# Registration
Added __@app.route('/register')__ logic and __register.html__ UI.
# ASYNC
Changed async deepseek query as all the aiohttp async logic. 
## Reasoning
1. Flask is based on WSGI so doesn't have a good support for it so it creates bugs. Replaced all with normal requests with Timeout incorporated. We don't get the full benefits of async. -- flask waits for each request to finish before serving another (unless we use async WGSI servers like uvicorn --- which, we're not completely using but we can in the future.)
2. The way this application work isn't suited for async. Why? First of all we have few requests happening, especially because we have limited requets per minute. 
3. The big problem of normal requests (concurrency) isn't a problem in this scenario.

# User db and app.py related
I updated a bit the User model and added directly into the model the methods to hash password and to check for hashed password. Its easier to use and it supports DRY concepts.

# Session cookie.
A big problem i've noticed is that even if you logout - register a new account and log back in with a new account you still have access to the old conversations. This problem occurs because we use sessions to store the conversations which, of course, remain even after we log out.
## Changes
Added a new __table__ for chats. We will use this table to store each chat individually. Added the logic to support this change as well. With this we solve the session cookies problem.

# Clear chat history.
I added a button to be able to clear the chat history.

# Logout button
I added a logout button to log-out from the current user.

# Restructured the folder architecture and the files. Current dir:
AIFacade/
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── instance/
│   └── users.db
├── project/           <--- new folder
│   ├── static/
│   │   └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   ├── __init__.py         <----new file
│   ├── auth.py             <---new file / broke from ex main.py
│   ├── chat.py             <---new file / broke from ex main.py
│   ├── config.py
│   ├── db.py
│   ├── extensions.py       <----new file
│   ├── models.py
│   └── utils.py            <--- new file
├── .env
├── .gitignore
├── changes.md          <---- new file
├── README.md
└── requirements.txt    <--- new file

## Reasoning
1. A more clear project structure.
2. Introduction of __init.py__ so future tests will be easier to make.
3. An organized structure means it will be easier in the future to scale and add new functionalities without having to worry about how you will have to reorganize in order to proper implement or where are located certaing methods, functions etc.

## New Content of files

### Database - db.py, models.py
Now its located in __db.py__ and the models for it are in __models.py__. As well as the logic for the CLI commands.

### Authentication - auth.py
Now all the routes __/logout__, __/login__, __/register__ aswell as the __login_manager__ object are located in __auth.py__.

### Chats - chat.py, utils.py
All the chats related routes __/chat__, the *new* __**/clear**__ route logic and __/home__ are located in __chat.py__ while the function __query_deepseek__ has been moved to __utils.py__

### extensions.py
In here we only have the __limiter__ object.

### App creation and all the linking logic behind - __init__.py
All the logic regarding creating the app, connecting the blueprints to the app, connecting the database, limiter, login manager is happening in **__init__.py**. Erros are also there because we need to add them as global in app directly. 

### .env file
Moved it to root dir and updated .gitignore to properly hide it.

### templates/register
Added the whole register page.

### index.html
Added a __clear chat history__ button.

### requirements.txt **new file*
Using 
```shell 
pip freeze > requirements.txt 
``` 
I added all the libraries which this project uses.

## Stayed the same

### templates/base, templates/login, templates/errors, static, config.py
All of them remained the same (changed only the url_for() routes so it will match the new routes.), __moved__ in __/project dir__. 