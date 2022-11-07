import numpy as np
import pandas as pd
import datetime

from .data_definition import DataDefinition

class DataGenerationSupporter():
    def __init__(self, 
                 data_defs:list=[],
                 data_num:int=None,
                 random_state:int=0,
                 verbose:int=0,
                 drop_rate:float=None,
                ):
        
        self.data_defs = data_defs
        self.data_num = data_num
        self.random_state = random_state
        self.verbose = verbose
        self.drop_rate = drop_rate
        self.df = pd.DataFrame()
        
        if len(data_defs) > 0:
            self.generate(self.random_state)
            self.drop_data_random(self.drop_rate)
        
    ##----------
    ## set new data definitions
    #3----------
    def set_data(self, data_defs):
        self.data_defs = data_defs
        self.generate(self.random_state)
        self.drop_data_random(self.drop_rate)
        
    ##----------
    ## auto generate function
    ##----------
    def auto_generate(self, data_num:int=100, col_num:int=10, random_state:int=0, key_date:bool=False, contain_nan:float=-1, verbose:int=0):
        
        np.random.seed(random_state)
        
        if col_num < 1:
            raise Exception(f'invalid col_num = {col_num}')

        # whether use date column or not
        key_col_date = (np.random.rand() >= 0.5) or key_date
            
        dtype_ths = {'num':0.8, 'cat':1}
        num_dtypes = ['uniform', 'gauss', 'sin', 'cos', 'order', 'noise']
        
        data_defs = []
        
        for col_idx in range(col_num):
            col_name = f'col_{col_idx}'
            data_cfg = {}
            
            ##---------
            ## if key column is date
            ##---------
            if col_idx == 0 and key_col_date:
                col_dtype = 'date'
                
                _date_candidates = pd.date_range(pd.to_datetime('2000-1-1'), pd.to_datetime('2021-12-31')).tolist()
                start_date = np.random.choice(_date_candidates)
        
                freq = np.random.choice(['D', 'h'])
            
                if freq == 'D':
                    end_date = start_date + datetime.timedelta(days=data_num-1)
                elif freq == 'h':
                    end_date = start_date + datetime.timedelta(hours=data_num-1)

                data_cfg['start'] = start_date.strftime('%Y-%m-%d %H:%m') #f'{year1}-{month1:0}-{day1:0}'
                data_cfg['end'] = end_date.strftime('%Y-%m-%d %H:%m') #f'{year2}-{month2:0}-{day2:0}'
                data_cfg['freq'] = freq
                
                if verbose:
                    print('auto generate >>', '  col_name =', col_name, '  col_dtype =', col_dtype, '  data_cfg =', data_cfg)
                
                
                data_defs.append([col_name, col_dtype, data_cfg])
                
                # data_num is deleted forcely
                data_num = self.get_data_num_from_datadef([col_name, col_dtype, data_cfg])
                
                continue
            
            _rand = np.random.rand()
            
            ##---------
            ## num column
            ##---------
            if _rand <= dtype_ths['num']:
                col_dtype = 'num'
                num_dtype = np.random.choice(num_dtypes, 1)
                
                if num_dtype == 'uniform':
                    data_cfg['type'] = 'uniform'
                    data_cfg['val'] = np.random.randint(-100,100)
                    
                if num_dtype == 'gauss':
                    data_cfg['type'] = 'gauss'
                    data_cfg['mean'] = np.random.randint(-100,100)
                    data_cfg['std'] = np.random.rand() * np.random.randint(1, 10)
                        
                if num_dtype == 'sin':
                    data_cfg['type'] = 'sin'
                    data_cfg['freq'] = np.random.randint(1,10)
                    data_cfg['scale'] = np.random.randint(1,10)
                    
                if num_dtype == 'cos':
                    data_cfg['type'] = 'cos'
                    data_cfg['freq'] = np.random.randint(1,10)
                    data_cfg['scale'] = np.random.randint(1,10)
                
                if num_dtype == 'order':
                    data_cfg['type'] = 'order'
                    data_cfg['freq'] = np.random.randint(-100,100)
                    data_cfg['start'] = np.random.randint(-100,100)
                    
                if num_dtype == 'noise':
                    data_cfg['type'] = 'noise'
                    data_cfg['noise_type'] = 'gauss'
                    data_cfg['prob'] = np.random.rand()
                    data_cfg['scale'] = np.random.randint(-100,100)
        
            ##----------
            ## category column
            ##----------
            elif _rand <= dtype_ths['cat']:
                col_dtype = 'cat'
                data_cfg['val'] = {f'category_{cat_idx+1}':np.random.rand() for cat_idx in range(np.random.randint(1, 50))}
                
            ##----------
            ## random drop
            ##----------
            if np.random.rand() <= contain_nan:
                data_cfg['drop_rate'] = np.random.rand() * 0.7
                
            
            if verbose:
                print('auto generate >>', '  col_name =', col_name, '  col_dtype =', col_dtype, '  data_cfg =', data_cfg)
                
            data_defs.append([col_name, col_dtype, data_cfg])

            
        self.data_defs = data_defs
        self.data_num = data_num
        self.random_state = random_state
        self.verbose = verbose
        
        self.generate(random_state, verbose=verbose)
        self.drop_data_random(self.drop_rate)
        
        # self.__init__(data_defs, data_num=data_num, random_state=random_state)
        
    ##----------
    ## generate function from data_defs
    ##----------
    def generate(self, random_state:int=None, verbose:int=0):
        random_state = random_state if random_state else self.random_state
        np.random.seed(random_state)
        
        # if data_num is None, auto compute from first column
        self.set_data_num_auto()
        
        # parse all data_defs
        data_defs, df = self.parse_data_defs(self.data_defs, self.data_num, verbose=0)
        self.data_defs = data_defs
        self.df = df
        return df
        
    ##----------
    ## get data row number from data column
    ##----------
    def get_data_num_from_datadef(self, data_def):
        key_dd = DataDefinition(data_def, verbose=self.verbose)
        return key_dd.data_num
        
    ##----------
    ## auto set data row number
    ##----------
    def set_data_num_auto(self):
        if self.data_num:
            return
        
        key_data_def = self.data_defs[0]
            
        self.data_num = self.get_data_num_from_datadef(key_data_def)

        if self.verbose:
            print(f'[INFO]data_num is None, so auto compute from column "{key_data_def[0]}" >> {self.data_num:,}')
        
        
    ##----------
    ## return generated data
    ##----------
    def get_data(self, return_dtype:str='pd'):
        if return_dtype == 'np':
            return self.df.copy().values
        return self.df.copy()
    
    
    ##----------
    ## drop randomly along row axis
    ##----------
    def drop_data_random(self, drop_rate:float=None, random_state:int=None, verbose:int=0):
        if drop_rate is None:
            if verbose:
                print(f'drop_rate_random is {drop_rate}')
            return
        
        _random_state = self.random_state if random_state is None else 0
        
        _df = self.df.sample(frac=1-drop_rate, random_state=_random_state)
        
        _df.sort_index(inplace=True)
        _df.reset_index(drop=True, inplace=True)
        self.df = _df
        
    ##----------
    ## random generate function
    ##----------
    def random_generate(self, auto:bool=False, data_num:int=100, col_num:int=10, key_date:bool=False, contain_nan:float=-1, verbose:int=0):
        random_state = np.random.randint(10000)
        if auto:
            self.auto_generate(data_num=data_num, col_num=col_num, random_state=random_state, key_date=key_date, contain_nan=contain_nan, verbose=verbose)
        else:
            self.generate(random_state=random_state)
            self.drop_data_random(self.drop_rate, random_state)
        return self.get_data()
    
        
    ##----------
    ## parse data_defs
    ##----------
    def parse_data_defs(self, data_defs:dict, data_num:int=None, verbose:int=0):
        dds = []
        df = pd.DataFrame()
        
        for i, data_def in enumerate(data_defs):
            # parse temporarily
            _col_name, _dtype, _cfg = data_def
            
            # corr data process
            if ('type' in _cfg) and (_cfg['type'] == 'corr'):
                anchor_data = df[_cfg['anchor']].copy()
                dd = DataDefinition(data_def, data_num, verbose=verbose, anchor_data=anchor_data)
            else:
                dd = DataDefinition(data_def, data_num, verbose=verbose)
                
            dds.append(dd)
            df[dd.col_name] = dd.values
            
        return dds, df

  