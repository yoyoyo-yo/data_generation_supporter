# Data Generation Supporter

Generate random data.

# Install

```bash
$ pip install git+https://github.com/yoyoyo-yo/data_generation_supporter.git
```

# Requirments

```bash
numpy, pandas
```

# Easy Usage

## Generate random data

```python
import data_generation_supporter

dgs = data_generation_supporter.DataGenerationSupporter(drop_rate=None)
dgs.random_generate(auto=True, col_num=10, data_num=10)
df = dgs.get_data()
```

df is like below

| col_0               |   col_1 |   col_2 |   col_3 | col_4      | col_5      |    col_6 |   col_7 |   col_8 |     col_9 |
|---------------------|---------|---------|---------|------------|------------|----------|---------|---------|-----------|
| 2008-09-01 00:09:00 |      17 |      -8 |       1 | category_8 | category_4 |  4.06959 |       1 | 24.6271 |   0       |
| 2008-09-02 00:09:00 |      89 |      66 |       1 | category_1 | category_3 | 17.5235  |       1 | 25.198  |   0       |
| 2008-09-03 00:09:00 |     161 |     140 |       1 | category_7 | category_3 | 18.1787  |       1 | 23.4561 |  53.6464  |
| 2008-09-04 00:09:00 |     233 |     214 |       1 | category_8 | category_2 | 13.2303  |       1 | 27.8414 |  17.1787  |
| 2008-09-05 00:09:00 |     305 |     288 |       1 | category_2 | category_4 |  9.9566  |       1 | 28.5841 | -17.3606  |
| 2008-09-06 00:09:00 |     377 |     362 |       1 | category_8 | category_1 | 14.5099  |       1 | 29.1131 |   6.54613 |
| 2008-09-07 00:09:00 |     449 |     436 |       1 | category_3 | category_1 | 15.2615  |       1 | 21.7097 | -27.202   |
| 2008-09-08 00:09:00 |     521 |     510 |       1 | category_8 | category_4 | 23.8298  |       1 | 30.0376 |  43.2443  |
| 2008-09-09 00:09:00 |     593 |     584 |       1 | category_1 | category_3 | 12.6841  |       1 | 30.6187 | -47.3898  |
| 2008-09-10 00:09:00 |     665 |     658 |       1 | category_6 | category_2 | 10.3038  |       1 | 27.3513 | -45.3113  |


## Generate from your pre-setting

You can set column config list.

Each list contains [***column name***, ***data type***, ***config***].


```python
import data_generation_supporter

dgs = data_generation_supporter.DataGenerationSupporter(
    [
        ['date', 'date', dict(start='2022-04-01', end='2022-04-14', freq='D')],
        ['id', 'raw', dict(val=np.arange(14))],
        ['id2', 'num', dict(type='order')],
        ['temperature', 'num', dict(type='gauss', mean=25, std=5)],
        ['sin', 'num', dict(type='sin', freq=5, scale=2)],
        ['const_val', 'num', dict(type='uniform', val=2)],
        ['Friend', 'cat', dict(val=['Cat', 'Dog', 'Salamander'])],
        ['Fruits', 'cat', dict(val={'Orange':3, 'Apple':1, 'Banana':2})],
        ['sin_corr', 'num', dict(type='corr', anchor='sin', corr=0.4)],
        ['sin_noised', 'expr', dict(expr=[dict(type='gauss'), '*', dict(type='sin', freq=3, scale=10, shift=10)])],
        ['exp_sin', 'expr', dict(expr=[dict(type='exp-', scale=2), '*', dict(type='sin', freq=1), 'f', 'log1p'])],
        ['Strength', 'expr', dict(expr=[dict(type='uniform', val=2), '+', dict(type='noise', noise_type='gauss', prob=0.2, scale=10)])],
    ],
)

df = dgs.get_data()
```


| date                |   id |   id2 |   temperature |          sin |   const_val | Friend     | Fruits   |   sin_corr |   sin_noised |      exp_sin |   Strength |
|---------------------|------|-------|---------------|--------------|-------------|------------|----------|------------|--------------|--------------|------------|
| 2022-04-01 00:00:00 |    0 |     0 |       33.8203 |  0           |           1 | Salamander | Orange   |  -2.38066  |            0 |  0           |    1       |
| 2022-04-02 00:00:00 |    1 |     1 |       27.0008 |  1.56366     |           1 | Cat        | Orange   |  -1.23466  |            0 |  0.464174    |    1       |
| 2022-04-03 00:00:00 |    2 |     2 |       29.8937 | -1.94986     |           1 | Dog        | Orange   |  -3.46184  |            0 |  0.544968    |    1       |
| 2022-04-04 00:00:00 |    3 |     3 |       36.2045 |  0.867767    |           1 | Salamander | Apple    |  -6.07699  |            0 |  0.479351    |    1       |
| 2022-04-05 00:00:00 |    4 |     4 |       34.3378 |  0.867767    |           1 | Cat        | Orange   |  -1.22663  |            0 |  0.34971     |    1       |
| 2022-04-06 00:00:00 |    5 |     5 |       20.1136 | -1.94986     |           1 | Salamander | Banana   |  -5.72915  |            0 |  0.205826    |   -5.75938 |
| 2022-04-07 00:00:00 |    6 |     6 |       29.7504 |  1.56366     |           1 | Cat        | Orange   |   2.37184  |            0 |  0.0828094   |    1.84861 |
| 2022-04-08 00:00:00 |    7 |     7 |       24.2432 |  1.22465e-15 |           1 | Dog        | Banana   |   5.73987  |            0 |  1.65877e-17 |    1       |
| 2022-04-09 00:00:00 |    8 |     8 |       24.4839 | -1.56366     |           1 | Salamander | Apple    |  -3.20957  |            0 | -0.040827    |  -15.3592  |
| 2022-04-10 00:00:00 |    9 |     9 |       27.053  |  1.94986     |           1 | Salamander | Banana   |   1.85907  |            0 | -0.0503148   |    1       |
| 2022-04-11 00:00:00 |   10 |    10 |       25.7202 | -0.867767    |           1 | Cat        | Orange   |  -0.320109 |            0 | -0.0425446   |    1       |
| 2022-04-12 00:00:00 |   11 |    11 |       32.2714 | -0.867767    |           1 | Dog        | Banana   |  -0.400157 |            0 | -0.028763    |    1       |
| 2022-04-13 00:00:00 |   12 |    12 |       28.8052 |  1.94986     |           1 | Dog        | Orange   |   0.425005 |            0 | -0.0155988   |    1       |
| 2022-04-14 00:00:00 |   13 |    13 |       25.6084 | -1.56366     |           1 | Salamander | Banana   |  -0.392099 |            0 | -0.00586413  |   23.1815  |

# Parameters

## raw

```python
['id', 'raw', dict(val=np.arange(30))],
```

- val : array ... raw data

## date

```python
['date', 'date', dict(start='2022-04-01', end='2022-04-30', freq='D')],
```

- start : str ... Start date.
- end : str ... End date.
- freq : str ... Frequency.

## numerical

```python
['temperature', 'num', dict(type='gauss', mean=25, std=5)],
```

- type : str ... Data name.
- scale : float (default=1) ... Scaling value.
- shift : float (defualt=0) ... Shifting value.
- abs : bool (default=False) ... Return absolute value.

### gauss

Gaussian noise.

```python
['gauss_test', 'num', dict(type='gauss', mean=25, std=5)],
```

- mean : float ... Mean value of gaussian distribution.
- std : float ... Standard deviation of gaussian distribution.

### order

Order value.

```python
['order_test', 'num', dict(type='order', freq=1, start=1)],
```

- freq : int ... Frequency.
- start : int ... Start value.

### sin, cos

f = sin(2 * pi * frequency * ind / data_length)

```python
['sin_test', 'num', dict(type='sin', freq=3)],
```

- freq : float ... Frequency.

### uniform

```python
['uniform_test', 'num', dict(type='uniform', val=2)],
```

- value : float ... Constant value.

### exp, exp-

f = exp(x), f = exp(-x)

```python
['exp_test', 'num', dict(type='exp')],
```

### noise

```python
['noise_test', 'expr', dict(expr=[dict(type='uniform', val=2), '+', dict(type='noise', noise_type='gauss', prob=0.2, scale=10)])],
```

- noise_type : str (default='gauss') ... Noise type. ['gauss', 'const']
- prob : float (defualt=0.5) ... Noise frequency.

### corr

```python
['corr_test', 'num', dict(type='corr', anchor='exp_test', corr=0.8)],
```

- anchor : str ... Anchor column name.
- corr : float (default=0.5) ... Target correlation value.
- epsilon : float (default=1e-4) ... Difference between target correlation and generated correlation.
- iter_max : int (default=10_000) ... Max iteration number.

## cat

```python
['Friend', 'cat', dict(val=['Cat', 'Dog', 'Salamander'])],
['Fruits', 'cat', dict(val={'Orange':3, 'Apple':1, 'Banana':2})],
```

- val : list, dict ... Category list. If list, each category appears at the same frequency. If dict, key is cateogyr and value is frequency weight.

## expr

```python
['sin_noised', 'expr', dict(expr=[dict(type='gauss'), '*', dict(type='sin', freq=3, scale=10, shift=10)])]
```

- expr : list ... Mathematical expression. List number is surely odd. You can use '+', '-', '*' and '/' .

# Function Usage

## DataGenerationSupporter(**args)

### Args

- data_defs : list (default=[]) ... Data config list.
- data_num : int (default=None) ... Data row number.
- random_state : int (default=0) ... Random seed.
- verbose : int (default=0) ... Print verbose information.
- drop_rate : float (default=None) ... Drop rate along row axis.


## random_generate(**args)

Generate random data using random determined seed.

### Usage

```python
dgs = data_generation_supporter.DataGenerationSupporter()
dgs.random_generate(auto=True, col_num=10)
df = dgs.get_data()
```

### Args

- auto : bool (default=False) ... Whether generate random data automatically.
- data_num : int (default=100) ... Data row number.
- col_num : int (default=10) ... Data column number.
- key_date : bool (default=False) ... Whether key column is data or not.
- contain_nan : float (default=-1) ... Frequency rate for each column contain nan.
- verbose : int (default=0) ... Print verbose information.




## auto_generate(**args)

Generate random data using fixed random_state.

### Usage

```python
dgs = data_generation_supporter.DataGenerationSupporter()
dgs.auto_generate(col_num=10)
df = dgs.get_data()
```

### Args

- data_num : int (default=100) ... Data row number.
- col_num : int (default=10) ... Data column number.
- random_state : int (default=0) ... Random seed.
- key_date : bool (default=False) ... Whether key column is data or not.
- contain_nan : float (default=-1) ... Frequency rate for each column contain nan.
- verbose : int (default=0) ... Print verbose information.

## get_data(**args)

### Args

- return_dtype : str (default='pd') ... Data type.


# License

MIT License