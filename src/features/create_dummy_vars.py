import pandas as pd

def create_dummy_vars(df):

    categorical_cols = [
        "Community School?",
        "Rigorous Instruction Rating",
        "Collaborative Teachers Rating",
        "Supportive Environment Rating",
        "Effective School Leadership Rating",
        "Strong Family-Community Ties Rating",
        "Trust Rating",
        "Student Achievement Rating",
        "borough"
    ]

    ref_val_dict = {
        "Rigorous Instruction Rating" : "Meeting Target",
        "Collaborative Teachers Rating" : "Meeting Target",
        "Supportive Environment Rating" : "Meeting Target",
        "Effective School Leadership Rating" : "Meeting Target",
        "Strong Family-Community Ties Rating" : "Meeting Target",
        "Trust Rating" : "Meeting Target",
        "Student Achievement Rating" : "Meeting Target"
    }
    for cat_col in categorical_cols:

        dummy_df = pd.get_dummies(df[cat_col], prefix=cat_col, dummy_na=True)
        dummy_df = dummy_df.astype('float')
        df = pd.concat([df, dummy_df], axis=1)

        drop_val = ref_val_dict.get(cat_col, None)
        if drop_val is None:
            drop_val = df.groupby([cat_col]).size().idxmax()
        
        drop_col = "{}_{}".format(cat_col, drop_val)
        
        df = df.drop(drop_col, axis=1)

    return df