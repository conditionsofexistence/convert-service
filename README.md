# TEI4BPS Web Converter
A Flask wrapper around the TEI4BPS conversion script. 
## Endpoints cheatsheet
* `/` - Home page, lets you upload a file. Select one from your machine, click upload and boom.
* `/show/<id>` - Task page, provides you links to the various task files.
* `/download/<id>/<file>` - File page, it serves you either of three files in text/plain mimetype.

## Usage
Every time a file is uploaded and processed (**task**), a unique  **id** is created. You can use this ID to later retrieve the results of a task and for support purposes. Each task contains three files:

```sh
input.csv 
output.xml 
conversion.log
```
Which are the input provided by the user, the output computed by the converter (if there was an error, this file may not be present) and a transcript of the conversion. 

For example, the result of task #`13fd312661284231a1868f6cbf7c967a` would look like:
```sh
/download/13fd312661284231a1868f6cbf7c967a/conversion.log
```
To access the task page:
```sh
/show/13fd312661284231a1868f6cbf7c967a
```
