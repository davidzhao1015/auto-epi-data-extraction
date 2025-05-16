#==============================================================================
# This script is used to parse subtype-specific patient ages for eco burden data 
#==============================================================================

import os
import re
import numpy as np
import pandas as pd
import pyxlsb

#----------------------------------------------------------------
# List files in the folder
#----------------------------------------------------------------

# Change the working directory to the folder containing the txt files 
os.chdir('/Users/xinzhao/ISMS_Work/Project_AIE/Working/chatgpt_outputs/chatgpt_output_epi/batch_3_eco') 

# List all files in the directory
file_list_epi = [] 
for file in os.listdir():
    if file.endswith("epi_v.txt"):
        file_list_epi.append(file)
    else:
        print(f"File {file} is not a txt file.") 

# Sort the file list
file_list_epi.sort() 
print(file_list_epi)

print(len(file_list_epi)) # Check the number of files in the list

# Convert the list to a dictionary 
file_dict_epi = {i:file_list_epi[i] for i in range(0, len(file_list_epi))}
print(file_dict_epi)

# file_dict_epi_df = pd.DataFrame(list(file_dict_epi.items()), columns = ['File', 'Ref']) 
# file_dict_epi_df['Ref'] = file_dict_epi_df['Ref'].str.split("_").str[1]
# file_dict_epi_df.to_csv("file_dict_epi.csv", index=False)


#---------------------------------------------------------------
# Read in each txt file, and write the contents to data frames 
#---------------------------------------------------------------

chat_dict_epi = {} # Create a dictionary to store the chat output
for key0, value0 in file_dict_epi.items():
    print(key0, value0)
    # Remove the line with "Quote(s)" in the txt file 
    with open(f"{value0}", "r") as f:
        lines = f.readlines()
        lines = [line for line in lines if 'Line(s)' not in line]
        lines = [line for line in lines if 'Section' not in line] 
        lines = [line for line in lines if "Quote(s)" not in line]
        # Skip empty lines
        lines = [line for line in lines if line != '\n']
        lines = [line for line in lines if line != ""]
        lines = [line.strip("\t") for line in lines] # Remove the leading and trailing tabs which is critical for the split function
      
        chat_key = key0 # key is the index of the file
        chat_dict_epi[chat_key] = {} # Create a nested dictionary for each txt file 

        for line in lines:
            # print(line)
            if ":" in line and re.match(r'^\d+', line): 
                key1, value1 = line.split(":", 1)
                # print(key1, f'the value is {value1}')

                if "Age of Patients by Subtype" in key1:
                    ind = lines.index(line) + 1 
                    while not re.match(r"^\d+", lines[ind]): 
                        key2, value2 = lines[ind].split(":", 1)
                        print(key2, f'the value is {value2}') # Check the key and value pairs

                        keywords = ['Mean', 'Median', 'SD', 'IQR', 'Subtype', 'Standard Deviation']
                        if all(keyword not in key2 for keyword in keywords): 
                            value3 = key2
                            key3 = key1 + " " + "Subtype" + " " + str(ind) # Add a unique identifier to the key
                            chat_dict_epi[chat_key][key3] = value3.strip()
                        else:
                            key3 = key1 + " " + key2.strip() + " " + str(ind) # Add a unique identifier to the key
                            chat_dict_epi[chat_key][key3] = value2.strip()
                            print(chat_dict_epi[chat_key])
                        ind += 1
                    else:
                        continue
                else:
                    continue
            else:
                continue    

print(len(chat_dict_epi)) # Check the number of files read in
print(chat_dict_epi[2]) 


#---------------------------------------------------------------
# Convert the dictionary to a data frame
#--------------------------------------------------------------- 
chat_df = pd.DataFrame(columns = ["File", "Parameter", "Value"])
rows = []

for key4, value4 in chat_dict_epi.items():
    for parameter, cell in value4.items():
        rows.append({'File': key4, 'Parameter': parameter, 'Value': cell})

chat_df = pd.concat([chat_df, pd.DataFrame(rows)], ignore_index=True)   

# Export the data frame to a csv file
chat_df.to_csv("parsed_patient_age.csv", index=False)


#---------------------------------------------------------------
# Unify Parameter column
#---------------------------------------------------------------

# Remove "22.    Age of Patients by Subtype" from the Parameter column
chat_df2 = chat_df.copy()
chat_df2['Parameter'] = chat_df['Parameter'].str.replace(r'22.\t*Age of Patients by Subtype', "", regex=True)

chat_df2.head(10)

# Remove •\t from the Parameter column
chat_df2['Parameter'] = chat_df2['Parameter'].str.replace(r'•\t', "", regex=True)
chat_df2.head(10)

# Remove digits from the Parameter column
chat_df3 = chat_df2.copy()
chat_df3['Parameter'] = chat_df2['Parameter'].str.replace(r'\d*', "", regex=True)

chat_df3.head(10)

# Unify the names in Parameter column
chat_df3['Parameter'].unique()

chat_df3['Parameter'] = chat_df3['Parameter'].str.strip()
chat_df3['Parameter'].unique()

# Replace Standard Deviation with SD
chat_df3['Parameter'] = chat_df3['Parameter'].str.replace("Standard Deviation", "SD")
chat_df3['Parameter'].unique()


#---------------------------------------------------------------
# Reshape the data frame
#---------------------------------------------------------------
chat_df4 = chat_df3.copy()

# Create a new column for Subtype
subtype_list = []

for i in range(0, len(chat_df4)):
    if chat_df4['Parameter'][i] == "Subtype":
        subtype_list.append(chat_df4['Value'][i])
        
        index = i+1
        while chat_df4['Parameter'][index] != "Subtype":
            subtype_list.append(chat_df4['Value'][i])
            index += 1
    else:
        continue

chat_df4['Subtype'] = subtype_list
chat_df4.head(30)

# Drop row with Parameter = Subtype
chat_df5 = chat_df4[chat_df4.Parameter != "Subtype"] 
chat_df5.head(30)

# Make long table wide 
chat_df6 = chat_df5.pivot(index=('File', 'Subtype'), columns='Parameter', values='Value').reset_index()
chat_df6.head(30)

# Export the data frame to a csv file
chat_df6.to_csv("parsed_patient_age_wide.csv", index=False)


#---------------------------------------------------------------
# Standardize the data
#---------------------------------------------------------------

# Remove •\t from Subtype column
chat_df6['Subtype'] = chat_df6['Subtype'].str.replace(r'•\t', "", regex=True)
chat_df6['Subtype'] = chat_df6['Subtype'].str.strip()
chat_df6['Subtype'].unique()


#---------------------------------------------------------------
# Standardize the Mean, Median, and SD columns
#---------------------------------------------------------------
def standardize_age(age):
    age = str(age)

    if age == "NR":
        return np.nan
    elif 'year' in age.lower() or 'month' in age.lower():
        print(age)
        # Find the number immediately before "month"
        match = re.findall(r'(\d+(?:\.\d+)?)\s+(?=years|months)', age)
        if len(match) == 2:
            years, months = map(float, match)
            return years + months/12
        elif len(match) == 1:
            years = float(match[0])
            return years
        else:
            return np.nan
    else:
        return age    

        
chat_df7 = chat_df6.copy()
chat_df7['Mean'] = chat_df6['Mean'].apply(standardize_age)

chat_df7['Median'] = chat_df6['Median'].apply(standardize_age)
chat_df7['SD'] = chat_df6['SD'].apply(standardize_age)

chat_df7.head(30)

# Export the data frame to a csv file
chat_df7.to_csv("parsed_patient_age_wide_2.csv", index=False)



#---------------------------------------------------------------
# Deal with IQR
#---------------------------------------------------------------
chat_df8 = chat_df7.copy()

def parse_irq(iqr):
    iqr = str(iqr)
    if iqr == "NR":
        return np.nan
    if "–" in iqr:
        print(iqr)
        iqr = iqr.split("–")
        iqr = [standardize_age(i) for i in iqr]
        return (iqr[0], iqr[1])
    
chat_df8['IQR'] = chat_df7['IQR'].apply(parse_irq)
chat_df8.head(30)

# Create two new columns for IQR - IQR_Lower and IQR_Upper
chat_df8['IQR_Lower'] = chat_df8['IQR'].apply(lambda x: x[0] if pd.notna(x) and isinstance(x, (list, tuple)) else np.nan)

chat_df8['IQR_Upper'] = chat_df8['IQR'].apply(lambda x: x[1] if pd.notna(x) and isinstance(x, (list, tuple)) else np.nan)

chat_df8.head(30)



#---------------------------------------------------------------
# Map Ref to File
#---------------------------------------------------------------

chat_df9 = chat_df8.copy()

chat_df9['Ref'] = chat_df8['File'].map(file_dict_epi)
chat_df9['Ref'] = chat_df9['Ref'].str.split("_").str[1]
chat_df9.head(30)


#---------------------------------------------------------------
# Reorder the columns
#---------------------------------------------------------------

chat_df10 = chat_df9[['Ref', 'Subtype', 'Mean', 'SD', 'Median', 'IQR_Lower', 'IQR_Upper']].reset_index(drop=True)
chat_df10.head(30)


# Export the data frame to a csv file
chat_df10.to_csv("parsed_patient_age_wide_3.csv", index=False)

#---------------------------------------------------------------
# Align Subtype with data hub manually
#---------------------------------------------------------------

chat_df11 = pd.read_csv("parsed_patient_age_wide_4.csv")


#---------------------------------------------------------------
# Read in the data hub
#---------------------------------------------------------------

data_hub_df = pd.read_excel("/Users/xinzhao/ISMS_Work/Project_AIE/Working/archived/ARG_Autoimmune_Encephalitis_Econ_Burden_Datahub_2025.01.17_CB_Mar14.xlsb", 
                            engine='pyxlsb',
                            sheet_name='Econ burden_copy_Mar13',
                            usecols="C:CS",
                            skiprows=4)

data_hub_df.head(10)

#---------------------------------------------------------------
# Merge the data frames
#---------------------------------------------------------------

# Rename columns in chat_df11
chat_df12 = chat_df11.copy()

renamed_list = {"Ref": "Ref #",
                "Subtype": "AIE subtype",
                "Mean": "Mean age (years)",
                "SD": "Age (SD)",
                "Median": "Median age (years)",
                "IQR_Lower": "Age (lower IQR)",
                "IQR_Upper": "Age (higher IQR)"}

chat_df12.rename(columns=renamed_list, inplace=True)

chat_df12.head(10)

# Merge the data frames
merged_df = pd.merge(data_hub_df, chat_df12, on=("Ref #", "AIE subtype"), how="left")
merged_df.head(10)

# Export the data frame to Excel
merged_df.to_excel("merged_patient_age.xlsx", index=False)
