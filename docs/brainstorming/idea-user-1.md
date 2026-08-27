# idea-user-1

In this file I will talk about why am I building this project.
Following description that will be under is the source of thruth for this
project.

This project is being created to make my usage of Fusion 360 easier and provide
additional helpful features that will be used in development later. Since I will
be working in Fusion 360 using Claude and Codex I feel like I could bring the
workflows that have proven its usefullnes and create new workflows suited for
this project individualy, something like METHOD.md file that bring how the AI's
should communicate with eachother and how the folder structure should look like
based on ICM research paper that is core of Omnissiahs work logic and since this
folder structre system can be fitted to do any work, I thought it would look
great here too. Since we touched Omnissiah I want you to know that this is core
project for my because it is essential part of creating something(component/detail,
frame, whole project) I want to be able to save some data after work is done and
use it in the next projects or maybe save some shortcut that will help me out
alot since we are using Fusion I am sure we will find out lots of hidden
mechanics and valuable lessons during the time of development, so I want to save
most crucial data to use it to make future projects easier to make and boost
their quality so we wont make the same mistakes again that we learned on during
the development of last project( for example: we made the 18x18 mm diameter
stock drone motor and store this 3d model + 2d planning so we can use it for
future projects that may need it), also Fusion 360 isn't only 3d modeling app it
could to lots of things, such as writing electrical circuits and many more
features that makes your idea become real. Since I am also working on creating
system of knowledge capture for software development(webs, apps , etc.) I think
catching knowledge in hardware development(I consider Fusion a crucial part of
creation of the hardware) is also very important and becoming more and more
advanced as times and projects go on.

How should this project work?

There is 2 use cases that I could think of right now, why would I use this
project(first lets rename this project to FusionControlCenter).

First use case is I want model and plan soemthing specific that I have in hand,
for example 17x17 diameter drone motor, which then I will use to create a
connection to the wood frame, so conclusion is that I have piece of hardware in
hand(could be 1 mottor and even every component the drone needs to fly) and I
want to create addition to it or you could say build aroun the existing piece or
pieces of hardware. From user stand point it means that he has the meassurements
that needs to be imported inside the Fusion 360 first as 2d plan and then scaled
up to 3d where work of perfecting the project for hardware begins, either user
himself start correcting 3d model by hand(without using AI and MCP server) or
user prompts AI the changes that he wants to make happen, after receiving the
prompt 2 AI;s start working together to determine couple of things, does the user
request classify's as minor change for sake of making hardware better(could be
lots of reasons, such as cutting on weight to make it more efficient, aerodynamic
purposes, etc.) or a big change that causes the re-evaluation of the project and
goes against the core reason why it was built. Then brainstorming happens, user
and AI's start exchaning ideas (this process is partly discussed inside
METHOD.md file) and after this process final decision is being made and put into
work. After all the parts are designed and created starts the process of building
the whole product, where the main work starts, we want user to provide well
written document about what this project is about, what parts does he have, what
material and cutting technique is he going to use and all the other specifics
such as why this project is being made ... etc. This documentation is very
important since its users input that could be viewed as single source of truth,
core logic that this project is being built around. This part of development
requires not only 3d moddeling but also knowledge of electronics, mechanical
engineering, mathematics and lot more, this part of development is very important
for knowledge capture since its heavily saturated with lots of high value data
that can be tested and than used as a refference for future projects.

So based on this case user already has some ready data that he can provide for
this system/project + well writen project description document. All of this
needs to wrapped by UI that provides user easier experience of working with
everything, for example I have motor in hand and project want me to give all the
needed measurements, right by the input field we can make UI that shows dummy
model of the mottor(there are lots of mottors and there needs to be couple of
dummy 3d models for most used types), then when requires to show the length of
the mottor, it makes slight tilt animation of the dummy 3d model and shows the
part that needs to be meassured(doesnt have to be total copy of the hardware
peice that user holds in hand but it will just give user better understanding of
what he has to measure to provide more correct info/data) and after inputting
all the needed data that user has, the project starts. This is the idea of the UI
that I want, and I only described 1 feature of user inputing data, there should
also be page where user can interract with AI's and brainstorm, see and provide
the files needed for conversation. For every change user should open the Fusion
360 app himself.

Second use case is user doesnt have any hardware on hand but has a strong idea
of what he want to do. He could provide well writen project description
document, planned circuit diagram and other stuff that is needed for project.
That means generating the hardware starts from 0, for example user want to create
a project, fixedwing drone that is used es retranlator and needs to have long
amount of flight time to do its mission better, user provides well writen
description document plus first version of what electric circuit should look
like, than start the brainstorming and search of compomenents that fit the
mission set, motors that could provide with longer flight time that consumes less
electicity and provides less thrust, flight controller, pcb, pdb ... etc. you get
the idea, you are building project from zero, searching internet for the
datasheets that provide the meassurements and specs that is best fit for the
projects mission requirements and so on.

I view this project as a development system + knowledge capture, for my hardware
part of development(I am already building Omnissiah that is doing the same but
for software). This project should grow around me and make development of
hardware easier. Since we are using MCP that is made by someone else maybe we
could even add something more to the server to suit this project mission
requirements better.

You can ask me questions that will specify certain things that I could have
missed.
