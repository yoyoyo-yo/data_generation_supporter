import numpy as np
import pandas as pd
import datetime

class DataDefinition():
    def __init__(self, data_def:list, data_num:int=None, anchor_data:np.array=None, random_state:int=0, verbose:int=0):
        self.data_def = data_def
        self.col_name = data_def[0]
        self.data_dtype = data_def[1]
        self.data_cfg = data_def[2]
        self.data_num = data_num
        self.anchor_data = anchor_data
        self.random_state = random_state
        self.verbose = verbose

        self.values = self.fit(self.col_name, self.data_dtype, self.data_cfg, self.data_num, self.anchor_data, self.verbose)
        
        if self.data_num is None:
            self.data_num = len(self.values)
            
        if self.verbose:
            print('-'*20)
            print(f'DataDefinition')
            print('-'*20)
            print(f'  column    : {self.col_name}')
            print(f'  data type : {self.data_dtype}')
            print(f'  info      : {self.data_cfg}')
            print(f'  values    : {self.values}')
        
        
    def fit(self, col_name:str, data_dtype:str, data_cfg:dict, data_num:int, anchor_data:np.array=None, verbose:int=0):
        values = self.parse_date_dtype(col_name, data_dtype, data_cfg, data_num, anchor_data, verbose)
        return values
        
    ##----------
    ## parse data definitions
    ##----------
    def parse_date_dtype(self, col_name:str, data_dtype:str, data_cfg:dict, data_num:int=None, anchor_data:np.array=None, verbose:int=0):

        if data_dtype == 'raw':
            values = self.generate_raw(col_name, data_cfg, verbose)
        if data_dtype == 'num':
            # correlation generate
            if data_cfg['type'] == 'corr':
                values = self.generate_num_corr(col_name, data_cfg, data_num, anchor_data, verbose)
            else:
                values = self.generate_num(col_name, data_cfg, data_num, verbose)
        if data_dtype == 'expr':
            values = self.generate_expr(col_name, data_cfg, data_num, verbose)
            
        if data_dtype == 'cat':
            values = self.generate_cat(col_name, data_cfg, data_num, verbose)
        if data_dtype == 'date':
            values = self.generate_date(col_name, data_cfg, data_num, verbose)
            
        values = np.array(values)
            
        # replace nan
        values = self.replace_nan(col_name, values, data_cfg, data_num, verbose)
            
        # skip when automatically getting data_num 
        if data_num:
            if len(values) > data_num:
                print(f'\n[WARNING] column "{col_name}" values={len(values)} > data_num={data_num}, so undersampled values')
                values = values[:data_num]
            if len(values) < data_num:
                pad = 0
                print(f'\n[WARNING] column "{col_name}" values={len(values)} < data_num={data_num}, so pad with {pad}')
                values = np.hstack([values, [pad] * (data_num-len(values))])
            
        return values
    
    ##----------
    ## get parameter from data config(data_cfg) or return default
    ##----------
    def get_param(self, data_cfg:dict, arg:str, default:None):
        return data_cfg[arg] if arg in data_cfg else default
    
    ##----------
    ## generator for raw data
    ##----------
    def generate_raw(self, col_name:str, data_cfg:dict, verbose:int=0):
        assert 'val' in data_cfg
        
        if verbose:
            print(f'column "{col_name}" >> raw')
        
        return data_cfg['val']

    
    ##----------
    ## get function applied value
    ##----------
    def wrap_func(self, xs:np.array, func:str):
        if func == 'log':
            values = np.log(xs)
        elif func == 'log1p':
            values = np.log1p(xs)
        elif func == 'exp':
            values = np.exp(xs)
        elif func == 'expm1':
            values = np.expm1(xs)
        return values
    
    ##----------
    ## generator for expression data
    ##----------
    def generate_expr(self, col_name:str, data_cfg:dict, data_num:int, verbose:int=0):
        exprs = data_cfg['expr']
        
        assert len(exprs) % 2 == 1
            
        xs = self.generate_num(col_name, exprs[0], data_num, verbose)

        for i in range(1, len(exprs), 2):
            operator = exprs[i]

            if operator in ['+', '-', '*', '/']:
                _xs = self.generate_num(col_name, exprs[i+1], data_num, verbose)
                if operator == '+':
                    xs += _xs
                elif operator == '-':
                    xs -= _xs
                elif operator == '*':
                    xs *= _xs
                elif operator == '/':
                    xs /= _xs

            elif operator == 'f':
                xs = self.wrap_func(xs, exprs[i+1])
        return xs
    
            
    ##----------
    ## generator for numeric data
    ##----------
    def generate_num(self, col_name:str, data_cfg:dict, data_num:int=None, verbose:int=0):
        assert 'type' in data_cfg
        
        dtype = data_cfg['type']
        
        if dtype == 'gauss':
            mean = self.get_param(data_cfg, 'mean', 0)
            std = self.get_param(data_cfg, 'std', 0)
            values = np.random.normal(mean, std, data_num)
            
        if dtype == 'sin':
            freq = self.get_param(data_cfg, 'freq', 1)
            values = np.sin(2 * np.pi * np.arange(data_num) / data_num * freq)
            
        if dtype == 'cos':
            freq = self.get_param(data_cfg, 'freq', 1)
            values = np.cos(2 * np.pi * np.arange(data_num) / data_num * freq)
            
        if dtype == 'order':
            start = self.data_cfg['start'] if 'start' in data_cfg else 0

            if 'freq' in data_cfg and 'end' in data_cfg:
                freq = data_cfg['freq']
                end = data_cfg['end']
                values = np.linspace(start, end, freq)

            elif 'freq' in data_cfg:
                freq = data_cfg['freq']
                end = start + freq * data_num
                values = np.arange(start, end, freq)
                
            elif 'end' in data_cfg:
                end = data_cfg['end']
                values = np.linspace(start, end, data_num)
                
            else:
                freq = 1
                end = start + freq * data_num
                values = np.arange(start, end, freq)
     
        if dtype == 'uniform':
            val = self.get_param(data_cfg, 'value', 1)
            values = np.ones(data_num) * val
            
        if dtype == 'exp':
            start = self.get_param(data_cfg, 'start', 0)
            end = self.get_param(data_cfg, 'end', 5)
            values = np.exp(np.linspace(start, end, data_num))
            
        if dtype == 'exp-':
            start = self.get_param(data_cfg, 'start', 0)
            end = self.get_param(data_cfg, 'end', 5)
            values = np.exp(-np.linspace(start, end, data_num))
            
        if dtype == 'noise':
            noise_type = self.get_param(data_cfg, 'noise_type', 'gauss')
            prob = self.get_param(data_cfg, 'prob', 0.5)
            
            if noise_type == 'gauss':
                noise = np.random.normal(0, 1, data_num)
            elif noise_type == 'const':
                noise = np.array([1] * data_num)
                
            probs = (np.random.rand(data_num) < prob).astype(int)
            values = noise * probs
            
        scale = self.get_param(data_cfg, 'scale', 1)
        shift = self.get_param(data_cfg, 'shift', 0)
        values = values * scale + shift
        
        set_abs = self.get_param(data_cfg, 'abs', False)
        
        if set_abs:
            values = np.abs(values)
    
        return values
    
    ##----------
    ## numeric data for correlation
    ##----------
    def generate_num_corr(self, col_name:str, data_cfg:dict, data_num:int=None, anchor_data:np.array=None, verbose:int=0):
        target_corr = self.get_param(data_cfg, 'corr', 0.5)
        target_corr_abs = np.abs(target_corr)
        assert 0 <= target_corr_abs <= 1
        epsilon = self.get_param(data_cfg, 'epsilon', 1e-4)
        add_type = self.get_param(data_cfg, 'add_type', 'gauss')
        iter_max = self.get_param(data_cfg, 'iter_max', 10_000)
        
        anchor_ptp = np.ptp(anchor_data)
        
        if add_type == 'gauss':
            
            if target_corr_abs == 1:
                scale = 0
            elif target_corr_abs >= 0.95:
                scale = 1
            elif target_corr_abs >= 0.9:
                scale = 0.15
            elif target_corr_abs >= 0.8:
                scale = 0.25
            elif target_corr_abs >= 0.7:
                scale = 0.35
            elif target_corr_abs >= 0.6:
                scale = 0.4
            elif target_corr_abs >= 0.5:
                scale = 0.75
            elif target_corr_abs >= 0.4:
                scale = 0.8
            elif target_corr_abs >= 0.3:
                scale = 1.2
            elif target_corr_abs >= 0.2:
                scale = 1.55
            else:
                scale = 2.2
                
            best_value = None
            best_corr = -100
            best_corr_diff = 1e5
            iter_count = 0
            corr_diff = 1e5
            

            while (best_corr_diff > epsilon) and (iter_count < iter_max):
                _z = np.random.normal(0, anchor_ptp * scale, data_num)
                value = anchor_data.copy() + _z
                corr = np.corrcoef(value, anchor_data)[0,1]
                corr_diff = np.abs(corr - target_corr_abs)

                if corr_diff < best_corr_diff:
                    best_value = value
                    best_corr = corr
                    best_corr_diff = corr_diff
                    
                iter_count += 1
                
            value = best_value
                
            if target_corr < 0:
                value *= -1
                
        else:
            raise Exception(f'invalid corr add_type >> {add_type}. ["gauss"] can be used ')
            
        if verbose:
            print('iter_count =', iter_count, '  best_corr =', best_corr, '  best_corr_diff =', best_corr_diff)
    
        return value
            
    
    ##----------
    ## category data
    ##----------
    def generate_cat(self, col_name:str, data_cfg:dict, data_num=None, verbose:int=0):
        assert 'val' in data_cfg

        cat_val = data_cfg['val']
        shuffle_num = self.get_param(data_cfg, 'shuffle_num', 5)
        cat_dic = {}
        
        # if category is list, all frequencies are equal
        if type(cat_val) is list:
            for cat_name in cat_val:
                cat_dic[cat_name] = data_num // len(cat_val)
                
            res = data_num - sum(cat_dic.values())
            cat_dic[cat_name] += res
            
        else:
            cat_n_sum = sum(cat_val.values())
            
            for cat_name, cat_num in cat_val.items():
                cat_dic[cat_name] = int(cat_num / cat_n_sum * data_num)
                
            res = data_num - sum(cat_dic.values())
            cat_dic[cat_name] += res
            
        values = []
        
        for cat_name, cat_num in cat_dic.items():
            values += [cat_name] * cat_num
            
        # random shuffle
        for _ in range(shuffle_num):
            np.random.shuffle(values)
        
        return values

    ##----------
    ## generator for date date
    ##----------
    def generate_date(self, col_name:str, data_cfg:dict, data_num=None, verbose:int=0):
        assert 'start' in data_cfg
        assert 'end' in data_cfg
        
        start_date = pd.to_datetime(data_cfg['start'])
        end_date = pd.to_datetime(data_cfg['end'])
        # freq = data_cfg['freq'] if 'freq' in data_cfg.keys() else 'D'
        freq = self.get_param(data_cfg, 'freq', 'D')
        
        dates = pd.date_range(start_date, end_date, freq=freq)
        return dates
    
    ##----------
    ## replace data to nan
    ##----------
    def replace_nan(self, col_name:str, values:np.array, data_cfg:dict, data_num:int, verbose:int=0):
        # get drop_rate parameter
        drop_rate = self.get_param(data_cfg, 'drop_rate', None)
        
        if drop_rate is None:
            return values
        
        nan_inds = np.random.rand(data_num) < drop_rate

        # if dtype is int, change to float
        if values.dtype in [np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64]:
            values = values.astype(np.float32)
 
        values[nan_inds] = None
        
        return values
        