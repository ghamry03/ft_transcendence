# Front End Documentation

This documentation provides an overview of the front-end structure, templates, and views for the project. It covers the system used to create front-end elements, explaining how everything connects and comes together.

## Table of Contents

- [File Structure](#file-structure)
- [File Structure Explained](#file-structure-explained)

## File Structure

```python
 main_app
│   ├── frontEnd # This app is where the magic happens
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py # This file is in charge of catching our URLs
│   │   └── views.py # Where the logic for the rendered page goes
│   ├── main_app
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py # We must add our sub-apps to the "Installed apps" section
│   │   └── urls.py # Any app URLs must be included in the main
│   ├── static
│   │   ├── css
│   │   │   └── main.css
│   │   └── fonts
│   │       └── ps2p.ttf
│   └── templates
│       ├── gameButton.html
│       ├── home.html
│       └── main.html
```

## File Structure Explained
**main_app *(Project Directory)***
- The purpose of the Django project is to communicate with other Django projects and Apps to control the flow of the front end & the rendering of templates.
- Minimal logic should be applied, as the apps the separate django projects will implement the majority of the logic.

**frontEnd *(sub-app Directory)***
- This sub-app is responsible for manipulating the base page for the SPA.
- most URL patters should be placed here
- most Views should be placed here

**main_app (sub-directory of project directory)**
- This is where the configuration and manager of the project are
- *This directory should be handled with care*

**static**
- Static files such as js, css, images, etc ... will be placed here

**templates**
- HTML templates that are used in the project should be placed here
- These templates are modular, and can be injected within other templates (we rely on this for the SPA)
- Using javascript, we will fetch certain URLs that will return an HTML template, then inject the returned file within the base HTML template without any page refreshes.

## Apps Breakdown
**main_app**
- settings.py
  - This file is used to configure our django project.
  - In this file we define our databse configuration, static files directory, templates engine & directories, and our middlewear.
  - We must define any additional sub-apps within this file.

- urls.py
  - in this file we must include all our sub-apps' url patterns
  - an example of this is the frontEnd app, we must include its URLs file to be able to handle the URL patterns related to it.

**frontEnd**
- urls.py
  - In this file, we must define our URL patterns that are required to handle, and define which view they are related to.

- views.py
  - In this file we must define the logic to execute once a URL patter has been recognized

- models.py
  - In this file, we will define the structure and behaviour of the database tables. 
  - This file might end up not being used, since the other apps/projects will implement their respective models and this app will mainly be used for rendering logic.

- apps.py
  - Can be used to customize the app specific configuration.

@ommohame
@mfirdous
@lde-alen
@kamin
