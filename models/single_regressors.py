import os
#import statsmodels.api as sm
#from statsmodels.regression.linear_model import RegressionResults

from model_utils import get_pred_and_response_dfs

def create_single_regressors(input_data_dir, output_data_dir, output_model_summaries_dir):

    interim_modeling_df = pd.read_csv("{}/step3_interim_modeling_data.csv".format(input_data_dir))

    pred_df, response_df, invalid_preds = get_pred_and_response_dfs()
    print(pred_df.head())
    #pred_train, pred_test, response_train, response_test = train_test_split(pred_df, response_df, test_size=0.2, random_state=223)

if __name__ == "__main__":
    
    cwd = os.getcwd()
    input_data_dir =  cwd.replace('/src', '') + '/data/interim'
    output_data_dir = cwd.replace('/src', '') + '/data/processed'
    output_model_summaries_dir =  cwd.replace('/src', '') + '/models'