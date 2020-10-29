import pandas as pd
import numpy as np

def weighted_median(data, weights, interpolate = False):
    """
    A function that calculates the weighted median of a given series of values 
    by using a series of weights.
    
    Parameters
    ----------
    data : Iterable
        The data which the function calculates the median for.
    weights : Iterable
        The weights the function uses to calculate an weighted median.

    Returns
    -------
    numpy.float64
        The function return the weighted median.

    """
    #Forcing the data to a numpy array.
    data = np.array(data)
    weights = np.array(weights)
    
    #Sorting the data and the weights.
    ind_sorted = np.argsort(data)
    sorted_data = data[ind_sorted]
    sorted_weights = weights[ind_sorted]
    
    #Calculating the cumulative sum of the weights.
    sn = np.cumsum(sorted_weights)
    
    #Calculating the threshold.
    threshold = sorted_weights.sum()/2
    
    #Interpolating the median and returning it.
    if interpolate == True:
        return np.interp(0.5, (sn - 0.5 * sorted_weights) / np.sum(sorted_weights), sorted_data)
    
    #Returning the first value that equals or larger than the threshold.
    else:
        return sorted_data[sn >= threshold][0]
    
def compute_tax(salary, levels, pcts, zichuy = 2.25, schum_zichuy = 216, max_salary = 0, max_tax = 0):
    """
    A function that calculates the amount of Income Tax, National Security Tax or Health tax
    a person needs to pay according to the Israeli tax laws.

    Parameters
    ----------
    salary : Float
        The salary from which the tax will be deducted.
    levels : Iterable
        A list of the tax brackets.
    pcts : Iterable
        A list of the tax brackets percents.
    zichuy : Float, optional
        The amount of zichuy points the salary earner has. The default is 2.25.
    schum_zichuy : Int, optional
        The Value of a single zichuy point. The default is 216.
    max_salary : Float, optional
        An optional maximum salary. The default is 0.
    max_tax : Float, optional
        An optional maximum tax. The default is 0.

    Returns
    -------
    Float
        The amount of tax which will be deducted from the salary.

    """ 
    #Returning the max tax if the conditions are met.
    tax = 0 
    if max_tax > 0 and max_salary > 0 and salary >= max_salary:
        return max_tax
    
    #The loop which calculates the tax. 
    for pct, bottom, top in zip(pcts, levels, levels[1:] + [salary]): 
        if salary - bottom <= 0 : 
            break 
        if salary > top:
            tax += pct*(top - bottom)  
        else: 
            tax += pct*(salary - bottom)
       
    #If the tax is less than the tax credit then return zero.    
    if tax <= (zichuy * schum_zichuy):
        return 0
    
    #If not, return the tax minus the tax credit.
    else:
        return tax - (zichuy * schum_zichuy)
    
#Creating lists for the employer's share of National Security Tax and Health Tax calculation.
levels_maasik = [0, 5944]
pct_maasik = [0.0345, 0.075]

"""
Source:
-------
https://www.btl.gov.il/Insurance/HozrimBituah/Hozrim/%D7%A9%D7%99%D7%A0%D7%95%D7%99%20%D7%91%D7%AA%D7%A9%D7%9C%D7%95%D7%9D%20%D7%93%D7%9E%D7%99%20%D7%91%D7%99%D7%98%D7%95%D7%97%20%D7%9C%D7%90%D7%95%D7%9E%D7%99%20%D7%95%D7%93%D7%9E%D7%99%20%D7%91%D7%99%D7%98%D7%95%D7%97%20%D7%91%D7%A8%D7%99%D7%90%D7%95%D7%AA%20%D7%9C%D7%A9%D7%A0%D7%AA%202018.pdf
"""

#Importing the household data. Enter the file address here. 
df = pd.read_csv(r'H20181021datamb.csv')
df.set_index('misparmb', inplace = True)

#Enter the file address here. 
df_prat = pd.read_csv(r'H20181021dataprat.csv')

#Importing the persons data and calculating the employer's share of National Security Tax and Health Tax. 
df_prat['maasik'] = df_prat['i111prat'].apply(compute_tax, args = (levels_maasik, pct_maasik), zichuy = 0, max_salary = 43370, max_tax = 3012)

#Calculating the tax for each household.
grouped = df_prat.groupby('misparMb').agg(np.sum)

#Creating a column with the employer's tax for each household.
df['maasik'] = grouped['maasik']

#Setting the value of Corporate Tax, Tariffs, Sales Tax, Gas Tax and employer's National Security Tax and Health Tax.
havarot_tariffs_knia_delek_maasik = 42900000000 + 2900000000 + 19100000000 + 36700000000 + np.sum(df['maasik'] * df['weight']) * 12
"""
Sources:
--------
https://www.gov.il/BlobFolder/guide/state-revenues-report/he/state-revenues-report_2017-2018_Report2017-2018_08.pdf
https://www.gov.il/BlobFolder/guide/state-revenues-report/he/state-revenues-report_2017-2018_Report2017-2018_15.pdf
https://www.gov.il/BlobFolder/guide/state-revenues-report/he/state-revenues-report_2017-2018_Report2017-2018_12.pdf
https://www.gov.il/BlobFolder/guide/state-revenues-report/he/state-revenues-report_2017-2018_Report2017-2018_13.pdf
"""

#Calculating VAT for each household.
df['VAT'] = df[['c30','c33','c34','c35','c36','c37','c38','c39']].sum(axis = 'columns') * 0.1453

#Calculating the tax share of each household according to the household consumption.
df['tax part'] = df['c3'] / np.sum(df['c3'] * df['weight'])

#Calculating the monthly tax other than direct taxes and VAT each household pays.
df['havarot_tariffs_knia_delek_maasik'] = df['tax part'] * ((havarot_tariffs_knia_delek_maasik) / 12)

#Calculating the total amount of yearly tax each houshold pays.
df['Total tax'] = (df['t21'] + df['VAT'] + df['havarot_tariffs_knia_delek_maasik']) * 12

#Calculating the median of the total tax payed.
median = weighted_median(df['Total tax'], df['weight'])

#Calculating the ratio between the median total tax payed and the total taxed payed by the households in Israel.
tax_exp_pct = median/np.sum(df['Total tax']*df['weight'])

#Printing what we are looking for.
print(tax_exp_pct)

