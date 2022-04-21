import pandas as pd
from pathlib import Path
import itertools

data_path = Path("excel/crop_impact_estimator.xlsx")

oblast_names = {
    'Vinnytska' :	0,
    'Volynska' :	0,
    'Dnipropetrovska' :	0.008987276,
    'Donetska' :	0.542371699,
    'Zhytomyrska' :	0.035060606,
    'Zakarpatska' :	0,
    'Zaporizka' :	0.720129649,
    'Ivano-Frankivska' :	0,
    'Kyivska' :	0.127230095,
    'Kirovohradska' :	0,
    'Luhanska' :	0.966453722,
    'Lvivska' :	0,
    'Mikolayivska' :	0,
    'Odeska' :	0,
    'Poltavska' :	0,
    'Rivnenska' :	0,
    'Sumska' :	0.331117551,
    'Ternopilska' :	0,
    'Kharkivska' :	0.367148026,
    'Khersonska' :	0.995345169,
    'Khmelnytska' :	0,
    'Cherkaska' :	0,
    'Chernivetska' :	0,
    'Chernihivska' :	0.306939387
}

enterprises = [
    'Wheat Enterprise',	
    'Wheat HH Farm',	
    'Winter Wheat Enterprise',	
    'Winter Wheat HH Farm',	
    'Corn Enterprise',	
    'Corn HH Farm',	
    'Barley Enterprise',	
    'Barley HH Farm',	
    'Sunflower Enterprise',	
    'Sunflower HH Farm'
]

crops = [
    'Wheat',
    'Winter Wheat',
    'Corn/Maize',
    'Barley',
    'Sunflower'
]

years = [2021, 2020]



# base_value_record = [
#     {'year' : y, 'crop' : c, 'base' : b}
#     for ((y,c), b) in zip(itertools.product(years, crops), [32719670,	31928410,	39819370,	9646230,	16439840,	25277714,	24644342,	28059337,	7832925,	13144369]) 
# ]

base_value_record = [
    {'year': 2021, 'crop': 'Wheat', 'base': 32719670}, 
    {'year': 2021, 'crop': 'Winter Wheat', 'base': 31928410}, 
    {'year': 2021, 'crop': 'Corn/Maize', 'base': 39819370}, 
    {'year': 2021, 'crop': 'Barley', 'base': 9646230}, 
    {'year': 2021, 'crop': 'Sunflower', 'base': 16439840}, 
    {'year': 2020, 'crop': 'Wheat', 'base': 25277714}, 
    {'year': 2020, 'crop': 'Winter Wheat', 'base': 24644342}, 
    {'year': 2020, 'crop': 'Corn/Maize', 'base': 28059337}, 
    {'year': 2020, 'crop': 'Barley', 'base': 7832925}, 
    {'year': 2020, 'crop': 'Sunflower', 'base': 13144369}
    ]

class CropSpecificAffected:

    def __init__(self, data_path: Path = None):
        
        self.data_path = data_path

    def data(self, data_path: Path = None):

        if data_path is None:
            data_path = self.data_path

        column_multiindex = pd.MultiIndex.from_product([years, crops, ['Output', 'Enterprise Share']], names=['year', 'crop', 'value'])

        df = (
            pd.read_excel(data_path, sheet_name='Data', header=0, usecols = 'A,C:W', skiprows=2, nrows=24, index_col=0)
            .drop(['Unnamed: 12'], axis=1)
            )

        df.columns = column_multiindex

        return df

    @property
    def oblast_conflict_dict(self):
        return oblast_names

    @property
    def oblast_conflict_df(self):
        return pd.DataFrame(self.oblast_conflict_dict.values(), index = self.oblast_conflict_dict.keys(), columns = ['Under Conflict'])

    @property
    def enterprise_df(self):
        multiindex = pd.MultiIndex.from_product([crops, ['Enterprise', 'HH Farm']], names=['crop', 'sector'])
        return pd.DataFrame([1]*len(multiindex),index = multiindex, columns = ['Share of Sector Impacted'])

    @property
    def base_df(self):
        return pd.DataFrame.from_records(base_value_record, index=['year', 'crop'])

    def set_oblast_conflict_value(self, name, value):
        df = self.oblast_conflict_df

        df.loc[name, 'Under Conflict'] = value

        return df

    def set_enterprise_dict_value(self, name, value):
        self.enterprise_dict[name] = value

    def get_impact(self, year, crop):

        group = self.data(data_path).groupby(['year', 'crop'],axis=1).get_group((year, crop))

        c = group.columns.get_level_values('crop')[0]

        hh_share, enterprise_share = self.enterprise_df.loc[(c, slice(None)), :].values.flatten()

        group.columns = ['Output', 'Enterprise Share']

        return group.apply(lambda x: ((x['Output']*x['Enterprise Share']*enterprise_share) + (x['Output']*(1-x['Enterprise Share'])*hh_share)), axis=1)*self.oblast_conflict_df['Under Conflict']

    def perc_impacted(self, year, crop, data_path: Path = None):

        gi = self.get_impact(year, crop)

        agg = gi.sum()

        base = self.base_df.loc[(year, crop), :].values[0]

        return agg/base


if __name__ == '__main__':

    csa = CropSpecificAffected(data_path=data_path)

    test_impact = [

    ]

    print(csa.perc_impacted(2020, 'Barley'))

