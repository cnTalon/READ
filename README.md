The aim of this project is to develop an open-source prototype for a reading tutor application. A set of AI
-generated stories at various difficulty levels will be provided, although optionally a Large Language Model 
could be used to generate additional stories. An existing open-source speech recognition model will be used 
to recognise words as the learner reads a text passage: the main algorithmic problem will be to align the 
output of the speech recogniser to the words in the passage. The application should highlight the next word 
to read; if the reader takes too long, or says the wrong word, assistance should be provided by giving the 
correct pronunciation (broken down into sounds) and asking them to try again. Statistics of reading speed 
and accuracy should also be provided, and reading content recommended based on the current level of 
reading proficiency. The application will only support reading in English, so that existing resources can be 
used, but the aim will be to develop a modular system that could be extended to other languages later

gitlab link: [https://gitlab.cs.uct.ac.za/capstone_reading-tutor-app/read]

Instructions to run:
1. clone the repository
3. open command line
4. change directory to the repository
5. enter <python .\installPackages.py>
2. install Espeak NG on github at [https://github.com/espeak-ng/espeak-ng]
6. run the application with <python .\READ.py>