# ModelMigrate

ModelMigrate is a way where you can migrate your TabularEditor model to Fabric Semantic Model. Here I choose Fabric Semantic Model because there we can save the storage by creating the shortcuts in Semantic Model and store the data in Azure Lakehouse. Here the data is actually redirecting through shortccuts than being directly queried during the connection with models.

Create a semantic model in Fabric. Ensure that there will be no need for re-wiring tabular connected reports after the model is built. 
Approach 
Pre-requisites: 
Before starting the encryption process, access the Original Tabular model.bim file from local storage and make a backup copy of it. Consider this file as OriginalTabular.bim. 
Prior to developing the Semantic model in Fabric, delta tables must be created for the intended tables with the same names as that of Tabular (But without spaces in column and table names). 
Note: Shortcut names cannot contain the following character(s) : \" \\ / : | < > * ? . % +"} 

Once we have a list of tables created, we use copilot for generating the required Array structure with details for shortcut creation. 

We run through the array containing the shortcutdetails and create shortcuts in Fabric for those delta tables using the script: 

Approach: 
1)Encrypt: We utilize a script that processes the Original Tabular .bim file, streamlining table names, source names, and relationships to produce an Encryptedmodel.bim file.  This generated .bim file doesn’t have spaces in the table and column names. 

2)During Encryption,
a log is created automatically using the script, to record all modifications
applied to the original .bim file. The encryption logic works by removing spaces from the “sourceColumn” key of the json data of columns. This result will get stored in “After” column of the tracker. The original untouched display name will be stored in the “Before” column. The datatype and table name of the columns are also stored.
This log is crucial for subsequently restoring the original naming configurations for Tables and Columns. 

3)Exception Handling: In the tracker document, any logs not to be considered for decryption, such as the changes to dataSources.name and Model.name, can be removed. 
Even without the removal code runs fine because data sources will be different for Fabric and Tabular.  

4)Exceptional Case 1: In instances where there are 2 duplicate columns being created from the same source columnof the table, it’s essential to omit or rename one of the conflicting columns from the source table query.
  Exceptional Case 2: Tabular allows the Relationships present in the existing Model to have columns with different datatypes, but Fabric doesn’t allow this. It's essential to find all these faulty relations and correct them. But other relationships also can get affected by this correction when same columns are being used, so it's better to correct the datatypes of all the relationships.  

5)Store the resultant excel in ADB for further analysis.
  We use a script that processes the export.csv excel by using graphs in Python. This script fixes all the datatypes of relationships and saves the updated relationships to a new csv file.  

6)The final step is to update the original changesLog file that we got from Encryption with the new datatypes for column names that we got from export_Corrected.csv. We are storing this corrected relationship file also in ADB as corrected_datatypes and utilize it for updation of log file using below logic. 

7)Now from the fabric side, after shortcuts creation, construct a new semantic model on these tables.  
Connect to this newly created Semantic Model through Tabular Editor and save it locally as a .bim file for subsequent steps.  This model won’t have any relationships or measures created. And the table and column names won’t have spaces in them. 
Decrypt: Run the decryption script on this locally saved .bim file, giving the updatedLogFile as a parameter. This script will revert the table and column names to their original state based on the updated log file. Additionally, it will integrate the hierarchies from the Original .bim file into the locally saved .bim file. Once this step is done, you will have a model .bim file that is very much like the Original Model .bim file but without relationships and measures. 

8)ALM Toolkit: To bring the relationships and measrues we use this ALM Toolkit. Uploadt he local Semantic model alongside the Encryptedmodel.bim, using the ALM Toolkit to transfer relationships and measures between the source and destination files.  

9)In ALM toolkit make sure we skip the entities other than Measures and Relationships. At this juncture, incorporate measures and relationships into the SemanticEncryptedmodel.bim.  without executing command scripts.  

10) Input the new Semantic model with the updated metrics and relationships into Tabular Editor to diagnose any potential issues or warnings. 

11)Deploy the newly Decrypted .bim file as a fresh Semantic Model (note: avoid overwriting existing models). Post-deployment, refresh the Semantic Model to update its contents

12)Ultimately, establish a link between the refreshed Semantic Model and Power BI to test functionality. Confirming backend data retrieval by sampling a few columns within Power BI verifies the operation’s success. 