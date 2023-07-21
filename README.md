# Song-Recommender

This project begins with a proposal for the gathering (webscraping on the first case) of songs of two natures. One about the 100 BillBoard. Other about the 10MillionSubset. 
The first dataset will be marked as hot. The second dataset marked as not_hot.
After the merging of the two datasets there will be a constructed dataframe with data from both datasets and columns 'Artist', 'Title', and hot_or_not.
Then the creating of several functions to gather first the features of identification of each song on the dataset.
Then the 2nd function will retrieve their audio features. 
There will be merging of all this data in a unique dataframe, droping duplicates and making sure the hot_or_not is still there. 
Then there will be a Clustering of musics according to similarities between them and if they are hot or not. 
The clustering will serve for the main program. 
The main program will serve to ask the user for an input of a song and then it will look for the songs id and audio features in the Spotify API. 
It will ask the user to choose between several options, and the chosen option will be the base of the search for a cluster with the same features. 
The program will give the user 5 recommendations of songs based on clusters. 
If the user wants more recommendations or make a reset in the program he can ask for it. 
