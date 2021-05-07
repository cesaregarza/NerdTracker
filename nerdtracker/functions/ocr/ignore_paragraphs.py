import pandas as pd

#Create a dictionary to reference for this function
class Ignore_Paragraphs_Class:
    block_number =      "block_num"
    paragraph_number =  "par_num"
    line_number =       "line_num"
    text =              "text"
    idx =               "idx"
    newline =           "\n"
    double_newline =    "\n\n"

function_dict = Ignore_Paragraphs_Class

def convert_raw_data_to_column(output_df):
    """Convert the output from image_to_data into a text dataframe with properly skipped values

    Args:
        output_df (pd.DataFrame): DataFrame output of pytesseract.image_to_data(output_type="data.frame")

    Returns:
        pd.DataFrame: Resulting DataFrame with a single column, ["text"], which skips the appropriate lines
    """

    #Convert the NaN values to empty strings
    na_mask = output_df[function_dict.text].isna()
    output_df.loc[na_mask, function_dict.text] = ""


    #Groupby block, paragraph, and line to split the values appropriately, then join the lines together with a space between them
    output_df = output_df.groupby([
        function_dict.block_number,
        function_dict.paragraph_number,
        function_dict.line_number,
    ])[function_dict.text].apply(" ".join)

    #Remove empty lines
    output_df = output_df.loc[output_df != ""]

    #Groupby again, this time by block number and concatenate with newlines
    output_df = output_df.groupby(function_dict.block_number).apply(function_dict.newline.join)

    #Reset index to turn it into a dataframe
    output_df = output_df.reset_index()

    #Add a constant that will be used as a basis for a new groupby
    output_df[function_dict.idx] = 0

    #Groupby on the new index column, then apply a double newline to indicate the split, and retrieve the top (only) value
    string_df = output_df.groupby(function_dict.idx)[function_dict.text].apply(function_dict.double_newline.join).loc[0]

    #Turn into a new dataframe
    final_df = pd.DataFrame(string_df.split(function_dict.newline), columns=[function_dict.text])

    #Strip extra spaces before and after the text in question
    final_df[function_dict.text] = final_df[function_dict.text].str.strip()

    return final_df