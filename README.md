
# Poodle
#### Description:
Poodle is a really simple scheduling app. It presents a really lightweight and simple-to-use alternative to doodle which organisations can host on their own servers.

It is created using Flask, SQLAlchemy and JQuery. It has a landing page, a form to create new polls and a page which is dynamically created for all polls and presents the data on which you can fill out the poll.

The form which enables you to create a new poll include a calendar with the ability to select multiple days. You can then also add as many timeslots as you wish to offer as options for the poll. The calendar and dynamic creation of the form is done using jquery and it is done in a way so you can select and unselect multiple days, which will presented in the correct order, without deleting any of the data that has been entered before.

For the poll, you will find the link to a URL which you can share with all of the people that should fill out the poll. The URL includes a random 24-letter Word so access to the poll is limited to the people who know the exact url. All poll include a row which shows the total numbers of available people at a given timeslot. The timeslots with the most people available as well as all timeslots with more than average availability are color-coded. In the last row you can simply add all your availability. You can also edit previously entered information and change it according to your changed availability. This is purposefully not restricted with some sort of user authentication to preserve simplicity and not needing to rely on the availability of cookies (users may come back days or weeks later). It is assumed users with access to the URL can be trusted not to meddle with the input of other users.

Poodle is fast, reliable and straightforward to use. It will also be published as open source so anyone can host it on their own servers.

To install the project environment, simply run

    pip install -r requirements.txt

You can simply start the flask server running

    python app.py

`app.py` Contains all of the routes that are available and relay all data between the database and the frontend

`pdatabase.py` Contains all the functions that are needed to retrieve and store information to and from the database

`/static/css/main.css` Contains all the styling used for the app

`/static/img/favicon.ico` Icon for the app

`/static/js` Contains all the javascript libraries utilised in the app

`/templates` Folder containing all the html files that are needed for the project, including the javascript/jquery code

`/templates/base.html` Base template 

`/templates/index.html` Page that shows the polls

`/templates/landing.html` Landing page template 

`/templates/newpoodle.html` Form to create new Polls
