# Friends API

This is a small API built on Django REST framework for managing friendships. It supports listing, creating, updating, and deleting friendships.

## Endpoints

- **List and Create Friendships**
  - **Endpoint:** `/api/friends/`
  - **HTTP Methods:** `GET` | `POST` | `PUT` | `DELETE`
 

## Query Parameters

- **`id` (Required)**
  - Specifies the user ID or friendship ID depending on the operation type.
  - `type 1` => `id` is the uid of the user.
  - `type 2` => `id` is friend record id.

- **`type` (Required for all request types except POST)**
  - Specifies the type of operation:
    - `1`: List friendships for the given user ID (pending and confirmed).
      - **User UID must be equal to `first_id` or `second_id` for `GET`**
    - `2`: Retrieve a specific friendship by ID.
      - **User UID must be equal to `second_id` for `PUT`**
      - **User UID must be equal to `first_id` or `second_id` for `DELETE`**
    - `3`: Check friendship between two users (requires `second_id` parameter).

- **`second_id` (Required for Operation Type 3)**
  - used to check if `second_id` is a `friend` `pending` or `no relationship`

## Usage

1. Ensure the Friends API is set up and running.

2. Use the provided endpoint.

   Example:
   ```bash
    # Create a new friendship
   curl -X POST -H "Content-Type: application/json" -d '{"first_id": 1, "second_id": 2}' http://localhost:8002/api/friends/

   # List friendships for self
   curl -X GET -H "Content-Type: application/json" -d '{"id": 123, "type": 1}' http://localhost:8002/api/friends/

   # Update friendship with ID 1
   curl -X PUT -H "Content-Type: application/json" -d '{"type": 2, "id":1 ,"first_id":88507,"second_id":88507,"relationship":0}' http://localhost:8002/api/friends/

   # Delete friendship record with ID 1
   curl -X DELETE -H "Content-Type: application/json" -d '{"type": 2 , "id": 1}' http://localhost:8002/api/friends/
