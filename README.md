# Mimamsa Exam Portal

<img src="https://user-images.githubusercontent.com/63692326/132917588-577f19c6-3cf4-4959-a097-367d3bb67680.jpg" width="700">

This is the exam portal first used by Mimamsa to conduct its online rounds in 2021. It's a Django app that allows for teams of participants to attempt a proctored exam.

## Setup

Make sure to install all dependencies in requirements.txt using pip, apply migrations, and create a superuser named 'admin'.
You'll need to run this command on docker to make django-channels work:
```
docker run -p 6379:6379 -d redis:5
```

Upon running server and logging in as admin, you should see the following screen:

<img src="https://user-images.githubusercontent.com/63692326/132915914-a3395b14-6608-46ec-840b-efb725006c35.JPG" width="700">

The **Update Registrations** page allows you to add teams of participant users by uploading a csv file. The update_accounts view can be tweaked depending on the format of the csv file.
Once the users are all registered, they'd need passwords. The **List of unset passwords** link returns a json file with randomly generated passwords for every user. The first time any user logs in, they'll be prompted to change their password.

The questions on the test can be set on the **Question Portal** page.

<img src="https://user-images.githubusercontent.com/63692326/132918820-32bccc75-fc4d-4633-9e97-e9b4e81fe193.JPG" width="700">

The start and end times of the test is set on the admin page manually. There's a single instance of the GlobalVariables model class that stores these as datetime fields.

Teams also need to be assigned proctors. This has to be done programmatically at this time. Proctor users' `user_type` fields take the value 'proctor' as opposed to the default 'participant'. Every team object has a foreign key called `proctor_user` that assigns thee proctor user to that team.

At multiple points in views.py, we used an AWS S3 bucket that no longer exists. To use this app, you'd have to create your own bucket and set the bucket name accordingly in views.py wherever necessary.
We also had a google form at the end of the exam for feedback. To use this app you could create your own form and set the iframe src accordingly in testended.html.
To allow for peer to peer connections we had a TURN server which now no longer exists. This is something that would also need to be set before deployment.
