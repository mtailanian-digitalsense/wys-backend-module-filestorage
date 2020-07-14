# API Endpoints for Filestorage module

Port: 8087

## Save a file

**URL** : `/api/filestorage/save`

**Method** : `POST`

**Required form data** : 
```
content_type='multipart/form-data'
"file=@FILENAME;type=application/extension"
```
**Auth required** : YES

### Success Response

**Code**: 201

**Content Example**

````json
{
  "url": "http://127.0.0.1:5000/api/filestorage/Y3ZfMTMucGRmMTU5NDU3NjgzNS4zMzUzNTg=.pdf"
}
````

## Get file
**URL** : `/api/filestorage/{filename}`

**URL Parameters**: `{filename}=[string]` where `{filename}` is the name of the file with extension.

**Method**: `GET`

**Auth required**: No

### Success Response

**Code**: `200 OK`

**Content example**
The file that you want to download.

### Error Responses

**Condition**: If the file required isn't in the server

**Code**: `404 Not Found`

## Update a file

**URL** : `/api/filestorage/{filename}`

**URL Parameters**: `{filename}=[string]` where `{filename}` is the name of the file with extension.

**Method** : `PUT`

**Required form data** : 
```
content_type='multipart/form-data'
"file=@FILENAME;type=application/extension"
```
**Auth required** : YES

### Success Response

**Code**: 200

**Content Example**

````json
{
  "url": "http://127.0.0.1:5000/api/filestorage/Y3ZfMTMucGRmMTU5NDU3NjgzNS4zMzUzNTg=.pdf"
}
````

### Error Responses

**Condition**: If the file required isn't in the server

**Code**: `404 Not Found`

**Condition**: Internal Error

**Code**: `500 Internal Error Server`

## Delete file
**URL** : `/api/filestorage/{filename}`

**URL Parameters**: `{filename}=[string]` where `{filename}` is the name of the file with extension.

**Method**: `Delete`

**Auth required**: Yes

### Success Response

**Code**: `200 OK`

### Error Responses

**Condition**: If the file required isn't in the server

**Code**: `404 Not Found`

