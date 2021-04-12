# syto-app

DRF & Vue.js based timetable helper.

## Installation

Project uses [Poetry](https://python-poetry.org) dependency manager, although for production purposes `pip` should be enough.

### Get the app

    git clone https://github.com/przemekk1385/syto-app.git
    cd syto-app
    git checkout release/[version]
    pip install -r requirements.txt
    
### Set environment variables

Environment variables can be set using `.env` file, sample content may look like below:

    SECRET_KEY=w7-xojjpvjxi60io0_hpv!_!+68jd#92=m6&6o7da^j439p8zk
    DEBUG=False
    STATIC_ROOT=static
    ALLOWED_HOSTS=localhost,127.0.0.1

`SECRET_KEY` must be set, remaining variables have defaults defined inside `settings.py`. Last step is migrating:

    ./manage.py migrate
    
## Usage

App is meant to be helper-tool for timetable management. Backend is handled by Django REST Framework, frontend by Vue.js app. API schema in in `openapi-schema.yml` or at the `/api/v1/swagger/` url.

### Access control

Access control inside the app is group-based. Groups are described below.

#### cottage_worker, stationary_worker

Aboves store info about job type. User cannot have both stationary_wsorker and cottage worker_groups.

#### foreman

Group for supervisors; can define workdays, activate users and see timetable / overview. Can be mixed with another groups.

#### new_employee

For informational pusposes only, to highlight new employees.
