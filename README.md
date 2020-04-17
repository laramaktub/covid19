# Getting Started
## Dependencies
What you need to run this app:

* `Python` and `Flask`.

* Ensure you're running the latest versions of Python `3.x` and Flask `1.x`.
* Also to not encounter any issues when compiling from libraries such as `Flask-Babel`, be sure that you run Jinja v. `2.5.2` or later.

> **Note:** For Mac users, it is recommended to first install **Homebrew**, as it will smooth the process of installing first dependencies. You can check it out [here](https://brew.sh/).

## Installing dependencies
1. First we need to have Python installed. For that, just run the command below:
```bash
$ brew install python
```
2. Now we will need to create a `virtual environment` inside our project. For that, we need to go to our project folder and install a `venv` folder inside:
```bash
$ cd covid19
$ python3 -m venv venv
```
3. Once the environment has been created, simply run it with the following command:
```bash
$ . venv/bin/activate
```
4. Now we will install `Flask`. Within the environment activated (you will notice a `(venv)` prefix on command line now), use the following command:
```bash
$ pip install Flask
```
> **Note:** For more information about Flask's installation, check the original [installation guide](https://flask.palletsprojects.com/en/1.1.x/installation/).

### Library dependencies
By now, all the dependencies needed to being able to run our project are installed. However, if you try to run the app now with `flask run`, you will be surprised by some unexpected errors such as `ModuleNotFoundError: No module named 'flask_wtf'`. This is because certain libraries used by the project are not installed automatically.
In order to install them, simply run the command:
```bash
$ pip install flask-assets flask-oidc flask-wtf pandas pyscss
```
> **Note:** Here are included only the dependencies required at the time this file was written. If more dependencies would be required, just refer to the [app.py](https://github.com/laramaktub/covid19/blob/master/app.py) file and check the modules imported.

### File dependencies
Same as happened with the [Library dependencies](#library-dependencies), certain additional files are required for the project to be able to run correctly:
* `client_secret.json` which contains `OAuth` credentials. Should be placed in the `root` folder
* `covid19.db` is a database file which contains test examples to work locally. Should be placed in the `./db` folder.
* An `img` folder which shall contain a set of X-Ray images to test the cases stored in the  _covid19.db_ file. This folder should be placed in the `./static` folder.
> **Note:** In order to get those files, please request them through the email shared in the [contact us](#contact-us) section.

## Running the app
Now that we have installed all dependencies and we have our virtual environment activated, we can finally runthe project. Just keep in mind that, before the first time you run run it, you must choose under which `environment` you want the project to run. The options are:
* `development`: environment to be used while making changes on the code. This modes enables auto-detention of any saved change, so you just need to refresh the browser to see your changes applied.
* `production`: It simulates the behaviour of the project being live. It also needs to be set before creating the build release.
So then for development purposes, we will run the command to set the environment, followed by the comman to run the project:
```bash
$ export FLASK_ENV=development
$ flask run
```
> **Note:** You only need to set the environment once. It will remain unless is set to another one by the developer. The project will most probably be running in http://localhost:5000/


### Detecting changes
When running on `production` environment, if you save any changes on the code, the app does not refresh automatically, specially if changes relate to `template` or `static` files (`.js`, `.css`, etc).
* In case of `.css` files, simply full refresh `localhost` by pressing `SHIFT+Cmd+R` or by clicking refresh button while pressing `SHIFT`.
* For `.html` files, sames steps described above, but right after entering `flask run` again.
This is why we recommend making use of the development environment. If any changes may not be detected, simply apply full refresh the same way described avobe.

# Useful Information
## Use a Flask-aware editor
These are some well known editors which can be used to edit the project:

* [Visual Studio Code](https://code.visualstudio.com/)
* [Atom](https://atom.io/) with [Flask plugin](https://atom.io/packages/flask-snippets)


## Further Information
* For more about Flask and Jinja, you can refer to the [user's guide](https://flask.palletsprojects.com/en/1.1.x/).
* For more information about `Flask-Babel` and how to proceed with translation keys, please check [the official documentation](https://pythonhosted.org/Flask-Babel/).


### Contact us

* Generic mail: covid19training@ifca.unican.es
* Comments regarding Frontend: solisgpedro@gmail.com
