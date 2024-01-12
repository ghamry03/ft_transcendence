# User Management API Documentation

## Overview

The User Management API is designed to facilitate the creation, retrieval, update, and deletion of user information. The API leverages Django REST Framework to handle HTTP requests and responses.

## Authentication

Authentication for the API is implemented using a custom authentication class called `api_auth`. Users are required to include the following headers in their requests:

- `HTTP_X_UID`: User ID.
- `HTTP_X_TOKEN`: Access token.

The `api_auth` class validates the provided user ID and token by making a request to the `https://api.intra.42.fr/oauth/token/info` endpoint. If the authentication fails, the API returns an `AuthenticationFailed` error.

## Endpoints

### 1. List Users

- **Endpoint:** `/users/`
- **Methods:** 
  - `GET`: Retrieve a list of all users.
  - `POST`: Create a new user.
- **Authentication:**
  - None required.
- **Request Headers:** None (for GET); `HTTP_X_UID` and `HTTP_X_TOKEN` required (for POST).
- **Request Body:** Serialized user object (for POST).
- **Response:**
  - `GET`: List of serialized user objects (Status Code: 200 OK).
  - `POST`: Serialized newly created user object (Status Code: 201 Created).
- **Errors:**
  - `POST`: 400 Bad Request if the request data is invalid.

### 2. User Details

- **Endpoint:** `/users/{user_id}/`
- **Methods:** 
  - `GET`: Retrieve user details by ID.
  - `PUT`: Update user details by ID.
  - `DELETE`: Delete a user by ID.
- **Authentication:**
  - `HTTP_X_UID` and `HTTP_X_TOKEN` required.
- **Request Headers:** `HTTP_X_UID` and `HTTP_X_TOKEN`.
- **Parameters:** `user_id` (for GET, PUT, DELETE).
- **Request Body:** Serialized user object (for PUT).
- **Response:**
  - `GET`: Serialized user object (Status Code: 200 OK).
  - `PUT`: Serialized updated user object (Status Code: 200 OK).
  - `DELETE`: No content (Status Code: 204 No Content).
- **Errors:**
  - 404 Not Found if the user with the specified ID doesn't exist.

## Example Usage

### Retrieve List of Users

**Request:**
```http
GET /users/api/
```

**Response**
```json
[
  {
    "uid": 1,
    "username": "john_doe",
    "image": "/media/john_doe.jpg",
    "status": 0
  },
  {
    "uid": 2,
    "username": "jane_doe",
    "image": "/media/jane_doe.jpg",
    "status": 1
  }
]
```

Create a New User
Request:
