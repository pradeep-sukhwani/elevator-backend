# Elevator Backend Logic
## To setup project in local environment
1. Take a clone of this repo
2. Setup Postgres
3. Setup Python 3.11.1
4. (Optional) Setup [Pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv):
5. (Optional) Make sure that you are using virtual-env before installing dependencies
### Setup `.env` file
- Create `.env` in the root directory and add the following
  ```.env
  DEBUG=True
  ALLOWED_HOSTS=['*']
  db_name='<db_name>'
  user_name='<db_user_name>'
  db_password='<db_password>'
  db_host='localhost'
  db_port='5432'
  SECRET_KEY=<django_secret_key> # This can be generated using this command:
  ```
  
  ```python
  # importing the function from utils
  from django.core.management.utils import get_random_secret_key

  # generating and printing the SECRET_KEY
  print(get_random_secret_key())
  ```

### Install the requirements to run the local server
  ```bash
  pip install -r requirements.txt
  ./manage.py migrate
  ```

### Fire up the server by running the following command
  ```bash
  ./manage.py runserver
  ```

## API
1. Create Elevator
   - API URL: `/api/elevator/`
   - Method: `POST`
   - payload:
     ```json
     {
     "name": "Elevator 3",  // str
     "total_number_of_floors": 20  // int
     "floors_not_in_use": [17,18,19]  // list
     "capacity_in_person": 10  // list
     "state": "idle"  // str - state can be idle/user_stop/door_close/door_open/moving/under_maintenance
     "current_floor": 1  // int
     }     
     ```
   - Response:
     ```json
     {
        "id": 3,
        "name": "Elevator 3",
        "state": "IDLE",
        "total_number_of_floors": 20,
        "floors_not_in_use": [
            17,
            18,
            19
        ],
        "capacity_in_person": 10,
        "current_floor": 1,
        "elevator_requests": [],
        "next_floor_details": null,
        "elevator_direction": null
      }
     ```
   - Sample Request & Response
     ![1 create_elevator](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/0f6f4525-6add-4d7d-98a8-5ab693447e64)
2. Edit Elevator
   - API URL: `/api/elevator/<elevator_id>/`
   - Method: `PATCH`
   - payload:
     ```json
     {
     "name": "Elevator 2",
     "total_number_of_floors": 30
     "floors_not_in_use": [17,18,19]
     "capacity_in_person": 15
     "state": "idle"
     "current_floor": 0
     }     
     ```
   - Response
     ```json
     {
        "id": 1,
        "name": "Elevator 2",
        "state": "IDLE",
        "total_number_of_floors": 30,
        "floors_not_in_use": [
            17,
            18,
            19
        ],
        "capacity_in_person": 15,
        "current_floor": 0,
        "elevator_requests": [],
        "next_floor_details": null,
        "elevator_direction": null
      }
     ```
   - Sample Request & Response
     ![2 edit_existing_elevator](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/f6308ceb-5b1b-4b53-9adb-687f3213cf1a)
3. Create Elevator Request
   - API URL: `/api/elevator-request/`
   - Method: `POST`
   - payload:
     ```json
     {
       "pick_from_floor_number": 1  // int
       "drop_at_floor_number": 15  // int
       "number_of_passengers": 4  // int
       "stop_elevator": true  // boolean - Optional
     }
     ```
   - Resonse:
     ```json
     {
        "id": 10,
        "pick_from_floor_number": 1,
        "drop_at_floor_number": 15,
        "number_of_passengers": 4,
        "elevator": 2
      }
     ```
   - Sample Request & Response
     ![3 create_elevator_request](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/a418ea3e-e7cc-4866-b220-16a4fdbfafc1)

4. Get all Elevator details
   - API URL: `/api/elevator/`
   - Method: `GET`
   - Response:
     ```json
     [
       {
        "id": 1,
        "name": "Elevator 2",
        "state": "DOOR_CLOSE",
        "total_number_of_floors": 30,
        "floors_not_in_use": [
            17,
            18,
            19
        ],
        "capacity_in_person": 15,
        "current_floor": 0,
        "elevator_requests": [
            {
                "id": 3,
                "pick_from_floor_number": 1,
                "drop_at_floor_number": 15,
                "number_of_passengers": 4,
                "is_completed": false,
                "created_date": "2023-10-04T19:24:25.385539Z",
                "elevator": 1
            }
        ],
        "next_floor_details": {
            "next_floor": 1,
            "number_of_passengers": 4,
            "drop_at_floor_number": 15
        },
        "elevator_direction": "Going Down"
       }
     ]
     ```
   - Sample Request & Response
     ![4 get_all_elevators](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/383991a8-95a3-4f69-86a4-60d9c97ed372)

5. Filter Elevator with params
   - API URL: `/api/elevator/`
   - Method: `GET`
   - params:
     ```json
     "name": "sample"  // Filter with name
     "state": "idle"  // filter with state - idle/user_stop/door_close/door_open/moving/under_maintenance
     "requests": "completed"  // filter with complete requests or not - param's value can be completed or not_completed
     ```
   - Response:
     ```json
     [
        {
            "id": 2,
            "name": "Elevator 1",
            "state": "DOOR_CLOSE",
            "total_number_of_floors": 20,
            "floors_not_in_use": [
                17,
                18,
                19
            ],
            "capacity_in_person": 10,
            "current_floor": 15,
            "elevator_requests": [
                {
                    "id": 1,
                    "pick_from_floor_number": 1,
                    "drop_at_floor_number": 15,
                    "number_of_passengers": 4,
                    "is_completed": true,
                    "created_date": "2023-10-04T18:05:37.766027Z",
                    "elevator": 2
                }
            ],
            "next_floor_details": null,
            "elevator_direction": null
        }
      ]
     ```
   - Sample Request & Response
     ![5 filter_with_elevators](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/20a7731f-a996-4963-9d97-437829b2ac76)
6. Process Elevator Requests
   - API URL: `/api/elevator-request/<elevator_request_id>/process_elevator_requests/`
   - Method: `POST`
   - Response:
     ```json
     {
        "id": 2,
        "pick_from_floor_number": 1,
        "drop_at_floor_number": 15,
        "number_of_passengers": 4,
        "is_completed": true,
        "created_date": "2023-10-04T19:13:55.060483Z",
        "elevator": 3
      }
     ```
   - Sample Request & Response
     ![6 process_elevator_requests](https://github.com/pradeep-sukhwani/elevator-backend/assets/18051510/639a6ab6-4dc9-4ac9-94ab-95af738aea53)


