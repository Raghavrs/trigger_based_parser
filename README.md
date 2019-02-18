# trigger_based_parser

python based News parser 
Specify the trigger to only get specified news from yahoo and google news.

Read the following steps to use.

1.Open the trigger.txt file.


2.Use following type of triggers:.
   
   
   TITLE​ : trigger execute if phrase you provide is present in Title of news.
   
   
   DESCRIPTION​ : trigger execute if phrase you provide is present in Description of news.
   
   
   NOT​ : trigger execute if phrase you provide is not present in news.
   
   
   AND​ : Used to combine two triggers or more . trigger execute if both triggers you provide are present in news.
   
   
   OR​ : Used to combine two triggers or more . trigger execute if one or more triggers you provide are present in news

3.Format of adding lines to triggers.txt.

      Name of text,Type of trigger(Case Sensitive use as shown above in capital letters),Phrase you want your news to          include(Not case Sensitive)

e.g: t1,TITTLE,YES BANK (will return all the news whose title contains yes bank)

      t2,DESCRIPTION,Reliance (will return all the news whose description contains Reliance)

      t3,AND,t1,t2 (in case of and,or provide the triggers you wish to combine)  

4.After creating the triggers you want add them in last line as shown

      ADD,t1,t2,t3

5.Save trigger.txt

6.Run parser.py file (Program refreshes after 2 minutes to find a new news if present)
