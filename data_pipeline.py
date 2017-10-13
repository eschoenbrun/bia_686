import pandas as pd
import numpy as np
import gc 

import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


from sklearn.preprocessing import Imputer

def load_data(path_to_data='data', sample_size = None):
	logging.info('Reading Properties 2016...')
	prop_2016 = pd.read_csv('{}/properties_2016.csv'.format(path_to_data))
	
	logging.info('Reading Properties 2017...')
	prop_2017 = pd.read_csv('{}/properties_2017.csv'.format(path_to_data))
	
	logging.info('Reading Train 2016...')
	target_2016 = pd.read_csv('{}/train_2016_v2.csv'.format(path_to_data))
	
	logging.info('Reading Train 2017..')
	target_2017 = pd.read_csv('{}/train_2017.csv'.format(path_to_data))
	
	logging.info('Performing merge')
	joined_data_2016 = pd.merge(target_2016,prop_2016,on="parcelid",how="left")
	joined_data_2017 = pd.merge(target_2017, prop_2017,on='parcelid',how='left')

	joined_data = pd.concat([joined_data_2016,joined_data_2017])

	# convert dates:
	joined_data.transactiondate = pd.to_datetime(joined_data.transactiondate,format="%Y-%m-%d")

	joined_data['transaction_mth'] = joined_data.transactiondate.apply(lambda x:x.month)
	joined_data['transaction_yr'] = joined_data.transactiondate.apply(lambda x: x.year)
	joined_data['transaction_day_of_wk'] = joined_data.transactiondate.apply(lambda x: x.dayofweek)
	joined_data=joined_data.drop('transactiondate',axis=1)


	# save memory
	for c, dtype in zip(joined_data.columns, joined_data.dtypes):
		if dtype == np.float64:
			joined_data[c] = joined_data[c].astype(np.float32)
    
	del target_2016
	del target_2017
	del prop_2016
	del prop_2017

	gc.collect()
	

	if sample_size is not None:
		logging.info('Sampling: {} of data'.format(sample_size))
		joined_data = joined_data.sample(frac=sample_size)

	return joined_data, joined_data['logerror'].values


def drop_columns(data, drop_cols):
	# mostly null
	data = data.drop(drop_cols, axis=1)
	data.drop_duplicates(inplace = True)

	return data


def columns_after_drop(numeric, categorical, drop_columns):
	numeric = list(set(numeric) - (set(numeric) & set(drop_columns)))
	categorical = list(set(categorical) - (set(categorical) & set(drop_columns)))

	return numeric, categorical


def impute_numerical_var(joined_data, numerical_cols, imputation= None):
    logging.info('Filling numeric NAs')
    if imputation:
        for col, val in imputations_numeric.items():
            if col in properties.columns:
                properties[col].fillna(val, inplace=True)
                return properties
    else:
    # numerical vars
        numerical_data = joined_data.copy().reset_index()
        numerical_data = numericaΩl_data[numerical_cols]
        numerical_data_cols = numerical_data.columns

        numeric_imp  = Imputer(strategy='median', axis=0)     
        numerical_data = pd.DataFrame(numeric_imp.fit_transform(numerical_data.values), columns=numerical_data_cols)

        return numerical_data,  {key:val for key,val in  zip(numerical_data_cols, numeric_imp.statistics_)}


def impute_categorical_var(joined_data, categorical_cols):
	# categorical vars
	categorical_data = joined_data.copy().reset_index()
	categorical_data  = categorical_data[categorical_cols]

	if 'hashottuborspa' in categorical_cols:
		categorical_data['hashottuborspa']=categorical_data['hashottuborspa'].apply(lambda x: 1 if x == 'True' else 0)

	if 'taxdelinquencyflag' in categorical_cols:
		categorical_data['taxdelinquencyflag']=categorical_data['hashottuborspa'].apply(lambda x: 1 if str(x).strip().lower() == 'y' else 0)

	for c, dtype in zip(categorical_data.columns, categorical_data.dtypes):
		categorical_data[c] = categorical_data[c].apply(lambda x: x if pd.isnull(x) else str(x))

	categorical_data_cols = categorical_data.columns

	most_frequent_lst = []
    
	logging.info('Using most frequent...')
    
	for col in categorical_data_cols:
		logging.info("Filling NA: {}".format(col))
		# logging.info("Filling NA: {}".format(col))
		mk=categorical_data[col].notnull()
		value_counts = categorical_data[mk][col].value_counts()
		most_frequent_lst.append(value_counts.index[0])
		categorical_data[col].fillna(most_frequent_lst[-1], inplace=True)

	return categorical_data, {key:val for key,val in zip(categorical_data_cols, most_frequent_lst)}

numeric_cols = ['assessmentyear','basementsqft',	'bathroomcnt',	'bedroomcnt',	'calculatedbathnbr', 
                'calculatedfinishedsquarefeet',	'finishedfloor1squarefeet',	'finishedsquarefeet12',
                'finishedsquarefeet13',	'finishedsquarefeet15',	'finishedsquarefeet50',	'finishedsquarefeet6',
                'fireplacecnt',	'fullbathcnt',	'garagecarcnt',	'garagetotalsqft',	'landtaxvaluedollarcnt',
                'lotsizesquarefeet',	'numberofstories',	'poolcnt',	'poolsizesum',	'roomcnt',
                'structuretaxvaluedollarcnt',	'taxamount',	'taxvaluedollarcnt',	'threequarterbathnbr',
                'unitcnt',	'yardbuildingsqft17',	'yardbuildingsqft26','transaction_day_of_wk','transaction_mth','transaction_yr',
               'taxdelinquencyyear','yearbuilt','latitude','longitude']

categorical_cols = ['airconditioningtypeid','architecturalstyletypeid','buildingclasstypeid','buildingqualitytypeid',
'censustractandblock','decktypeid','fips','fireplaceflag','hashottuborspa',
 'heatingorsystemtypeid','parcelid','pooltypeid10','pooltypeid2','pooltypeid7','propertycountylandusecode',
 'propertylandusetypeid','propertyzoningdesc', 'rawcensustractandblock','regionidcity','regionidcounty','regionidneighborhood','regionidzip',
 'storytypeid','taxdelinquencyflag','typeconstructiontypeid']

drop_cols = ['buildingclasstypeid','propertyzoningdesc','garagetotalsqft',	'garagecarcnt',	'numberofstories',	'poolcnt',	'threequarterbathnbr',	
	'fireplacecnt',	'finishedfloor1squarefeet','finishedsquarefeet50','finishedsquarefeet15',
	'finishedsquarefeet12', 'yardbuildingsqft17',	'poolsizesum',	'finishedsquarefeet6',	'yardbuildingsqft26',	
	'basementsqft',	'finishedsquarefeet13','assessmentyear','calculatedbathnbr',
	'rawcensustractandblock', 'censustractandblock','regionidzip','regionidcounty','regionidcity','regionidneighborhood',
	'regionidneighborhood','taxvaluedollarcnt','buildingclasstypeid','fireplaceflag','storytypeid']	

# use pipeline

joined_data, logerror_var = load_data(path_to_data='data')
joined_data = drop_columns(joined_data, drop_cols)

# if you need to drop a column, add it to drop_cols
numeric_cols, categorical_cols = columns_after_drop(numeric_cols, categorical_cols, drop_cols)

numeric_data, imputations_numeric = impute_numerical_var(joined_data, numeric_cols)

categorical_data, imputations_categorical = impute_categorical_var(joined_data, categorical_cols)










