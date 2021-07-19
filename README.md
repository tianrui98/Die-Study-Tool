# Die Study Tool

This application is designed for numismatists who engage in die analysis.

## What is Die Analysis
One of the most important problems ancient numismatics (the study of currency) tries to solve is the quantity of a money issue. Counting the number of surviving coins will not help simply because most ancient coins do not survive till today. A better approach is to estimate, with the help of statistics, the number of stamps used to make these coins, which tend to be of a limited amount and easier to be captured by today's samples. While coins from the same issue tend to have very similar designs, trained numismatist can identify whether two coins are struck from the same stamp. In numismatics, these stamps are called "dies". Dies were hand-carved by skilled artisans and came in sets of obverse and reverse. They were used in Roman workshops for pressing patterns on to molten metal, and thus have a typical lifespan of a few thousands of strikes. With the two information, the predicted number of dies and the life span of each die, numismatists can estimate the quantity of a coin issue. This is important for understanding aspects of the ancient economy such as the monetary and fiscal policies.

Die analysis can also shed light on the organization of Roman mints. This is achieved by plotting a network diagram of die types, which are connected by obverse-reverse relationship. 

## What is this program for

Traditionally, die analysis involves pair-wise comparisons of coin images. This process, done manually, takes a extremely long time and requires meticulous organization and documentation. To speed up the pair-wise comparison, our team has designed a statistical model that uses computer vision and machine learning to group coin images into die types. However, the model does not have a 100% success rate, therefore it is still necessary that a numismatist look over the model's output and correct where necessary.

This program simplifies the checking process by automatically opening pairs of images in the right order and recording the user's actions (eg. confirming the match). __Freed from the burden of Excel spreadsheets, the user can now concentrate on visual analysis, and all they have to do is clicking buttons__. After each session, the program will generate a spreadsheet with the identified die grouping, as well as a "die combination diagram" for visualizing the network of die types in Cytoscape or Gephi. s
