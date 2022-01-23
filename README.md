# Flask Student Attendance Management System
I build this project during Lockdown(Pandamic) of 2020 when my institute started taking online classes, as my institute wasn't having any ERP/EMS system to track presence of students in online class or track the student.
<br>

They were using Excel before I build this then an Idea of making an ERP came into my mind.

I was having some experience of using Flask and using some online documentation I finally build this.

It was used by my institutions for long time and after that classes went offline and no one use it now.

## Why I made this Repository ?
This project was kept in a private repository for long time so I decided to bring this up as a public project so that anyone can work on it and contribute if they want.
<hr>

# Project is Live on Website
Click here to see this project in action : [Link to Project](http://attmngt.herokuapp.com/)

To know how to use this project click here : [How to use](howto.md)
<hr>

# How to Run this project on your machine?
I have used **Docker** so that any one can easily run this on their machine.

> To run you need docker installed on your computer, goto this link to know how its done : [How to install Docker Engine](https://docs.docker.com/engine/install/)

## Cloning and Runing the project
- To start working you have to get this repository on your machine for that run :
  ```shell
  git clone https://github.com/areeburrub/Flask-Student.git
  cd Flask-Student
  ```
- Build the docker container using following command :
  ```
  docker build -t attendance .
  ```
- Run the container, and port it to `localhost:8000` using :
  ```
  docker run -p 8000:8000 attendance
  ```
## Opening in browser
To view the project got `localhost:8000` from your browser