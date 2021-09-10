# Mimamsa Exam Portal

<img src="https://user-images.githubusercontent.com/63692326/132917588-577f19c6-3cf4-4959-a097-367d3bb67680.jpg" width="700">

This is the exam portal first used by Mimamsa to conduct its online rounds in 2021. It's a Django app that allows for teams of participants to attempt a proctored exam.
Participants of a team can talk to each other and chat amongst themselves and the proctor assigned to the team can hear and see all the converstaion. The proctor will also be receiving video streams of all the participants of the team and can communicate with the team through chat. Proctors are also notified whenever anyone in their team tries to right click, escape fullscreen mode, or open inspect element. Proctors also see errors are logged onto participants' browser consoles so that they'll be better equipped to deal with technical difficulties.

**Participants' view:**

<img src="https://user-images.githubusercontent.com/63692326/132922735-b87603ff-9d72-4094-9432-93b37bf308f9.JPG" width="500">
<img src="https://user-images.githubusercontent.com/63692326/132922762-d932c77d-edab-47ec-a0e5-e4b2916a5575.JPG" width="500">
<img src="https://user-images.githubusercontent.com/63692326/132922522-c8fb7c7d-b3aa-4002-b21e-576aa783fce5.JPG" width="500">
<img src="https://user-images.githubusercontent.com/63692326/132922305-829a047e-1431-4a64-885a-2ed96a6b032f.JPG" width="500">

**Proctor's view:**

<img src="https://user-images.githubusercontent.com/63692326/132921865-dd4a5dae-0988-473f-a642-1abc5b1a6822.jpg" width="500">


Participants can upload answers in different formats depending on the type of question asked. In case two participants are viewing the same question, one can view their teammate's latest answers by using a sync button. Participants can also mark questions as answered or mark them for review, and these changes show for all members of the team in real time.



## Setup

Make sure to install all dependencies in requirements.txt using pip, apply migrations, and create a superuser named 'admin'.
You'll need to have a redis server running on docker to make django-channels work. Relevant cmd command:
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
