import pandas as pd

# Load the dataset with proper encoding
df = pd.read_csv('AP_dataset.csv', encoding='latin1', dtype=str)

# Drop completely empty rows
df.dropna(how='all', inplace=True)

# Replace NaN values in 'KccAns' with an empty string
df['KccAns'] = df['KccAns'].fillna('').str.strip().str.lower()  # Normalize case & trim spaces

# Define regex pattern for rows to REMOVE
pattern = r'recomond dosage has given|transferred to level ? 2|recommended information has given|recomended information has given|details already provided|no additional info required|information provided as per data|given infermation as per the data|recommanded information has given|infoermation given as per data|given information sa pet the data|info given|recommanded information has given|given information as per  the data|recommanded dosage has given|infoermation given|recommanded date has given|given information a sper the data|recommnaded information has given|recommanded information haws given|infoermation given as per data|infoermation given as per data'

# Remove rows that match the pattern
df_cleaned = df[~df['KccAns'].str.contains(pattern, regex=True, na=False)].copy()

# Save the cleaned dataset without unwanted rows
df_cleaned.to_csv('cleaned_AP_dataset.csv', index=False, encoding='utf-8')

# Print confirmation
print(f"Original dataset: {len(df)} rows")
print(f"Cleaned dataset: {len(df_cleaned)} rows (after removal)")
