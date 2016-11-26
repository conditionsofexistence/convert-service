# Task Manager
A trivial Flask tasks manager. 

## Endpoints cheatsheet
* `/` - Home page, lets you upload a file. Select one from your machine, click upload and boom.
* `/list` - List page, shows you a list of all the tasks that have run.
* `/show/<id>` - Task page, provides you links to the various task files.
* `/download/<id>/<file>` - File page, it serves you either of three files (in `text/plain` mimetype).

## Usage
Every time a file is uploaded and processed (**task**), a unique  **id** is created. You can use this ID to later retrieve the results of a task and for support purposes. 

For example, the result of task #`13fd312661284231a1868f6cbf7c967a` would look like:
```sh
/download/13fd312661284231a1868f6cbf7c967a/conversion.log
```
To access the task page:
```sh
/show/13fd312661284231a1868f6cbf7c967a
```
or simply find it in the tasks list
```sh
/list
```

## Running
Install requirements (in virtualenv if preferred) and run with:

`python server.py`

