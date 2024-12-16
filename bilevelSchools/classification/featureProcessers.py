from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder
import pandas as pd

def label_encode_categorical_features(config, df_reference, df_follow):

    for s_feat_name in config.d_feature_collection['categorical']:

        encoder = LabelEncoder()

        ### use .loc to prevent the SettingWithCopyWarning in Pandas
        df_reference.loc[:, s_feat_name] = encoder.fit_transform(
            df_reference[s_feat_name]
        )

        df_follow.loc[:, s_feat_name] = encoder.transform(
            df_follow[s_feat_name]
        )

    df_reference = df_reference.astype(
        {
            s_feat_name: 'category'
            for s_feat_name in config.d_feature_collection['categorical']
        }
    )

    df_follow = df_follow.astype(
        {
            s_feat_name: 'category'
            for s_feat_name in config.d_feature_collection['categorical']
        }
    )

    return df_reference, df_follow

def one_hot_encode_categorical_features(config, df_reference, df_follow):

    # sparse = False to return a dense array

    for s_feat_name in config.d_feature_collection['categorical']:

        encoder = OneHotEncoder(
            sparse_output = False
        )

        ### Transform
        feat_encoded_reference = encoder.fit_transform(
            df_reference[[s_feat_name]]
        )
        feat_encoded_follow = encoder.transform(
            df_follow[[s_feat_name]]
        )

        ### Create DataFrames from the encoded arrays
        df_reference_feat_encoded = pd.DataFrame(
            feat_encoded_reference,
            columns = encoder.get_feature_names_out([s_feat_name])
        )
        df_follow_feat_encoded = pd.DataFrame(
            feat_encoded_follow,
            columns = encoder.get_feature_names_out([s_feat_name])
        )

        ### Reset index to ensure proper concatenation
        df_reference_feat_encoded.index = df_reference.index
        df_follow_feat_encoded.index = df_follow.index

        ### Concatenate the one-hot encoded columns back to the original DataFrames
        df_reference = pd.concat(
            [
                df_reference.drop(s_feat_name, axis = 1),
                df_reference_feat_encoded
            ],
            axis = 1
        )
        df_follow = pd.concat(
            [
                df_follow.drop(s_feat_name, axis=1),
                df_follow_feat_encoded
            ],
            axis = 1
        )

    return df_reference, df_follow

def normalize_numerical_features(config, df_reference, df_follow):

    ### this will handle some pandas warning for int64
    df_reference = df_reference.astype(
        {
            s_feat_name: 'float64'
            for s_feat_name in config.d_feature_collection['discrete']
        }
    )

    df_follow = df_follow.astype(
        {
            s_feat_name: 'float64'
            for s_feat_name in config.d_feature_collection['discrete']
        }
    )

    l_feat_names = (
        config.d_feature_collection['discrete']
        +
        config.d_feature_collection['continuous']
    )

    scaler = MinMaxScaler()

    df_reference.loc[:, l_feat_names] = scaler.fit_transform(
        df_reference[l_feat_names]
    )

    df_follow.loc[:, l_feat_names] = scaler.transform(
        df_follow[l_feat_names]
    )

    return df_reference, df_follow