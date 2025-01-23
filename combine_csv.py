import pandas as pd
import os

def combine_csv(files, output_file):
    try:
        dataframes = []
        
        for file in files:
            # Check if the file exists
            if not os.path.isfile(file):
                print(f"Error: The file '{file}' does not exist.")
                return
            
            # Read the CSV file
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding='latin1')
            
            dataframes.append(df)
        
        # Combine the DataFrames
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        # Save the combined DataFrame to a new CSV file
        combined_df.to_csv(output_file, index=False)
        print(f"Combined CSV saved as {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Get the number of files from the user
    num_files = int(input("Enter the number of CSV files to combine: "))
    
    # Get file names from the user
    files = []
    for i in range(num_files):
        file = input(f"Enter the name of CSV file {i+1} (with extension): ")
        files.append(file)
    
    output_file = input("Enter the name of the output CSV file (with extension): ")
    
    # Combine the CSV files
    combine_csv(files, output_file)

if __name__ == "__main__":
    main()