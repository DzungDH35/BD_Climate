import os
import pandas as pd

src='D:\\BD_Climate\\data\\csv'
obj_list=os.listdir(src)
print(obj_list)
s = {'Day': pd.Series([1], index=[1]),
     'T': pd.Series([1], index=[1]),
     'TM': pd.Series([1], index=[1]),
     'Tm': pd.Series([1], index=[1]),
     'SLP': pd.Series([1], index=[1]),
     'H': pd.Series([1], index=[1]),
     'PP': pd.Series([1], index=[1]),
     'VV': pd.Series([1], index=[1]),
     'V': pd.Series([1], index=[1]),
     'VM': pd.Series([1], index=[1]),
     'VG': pd.Series([1], index=[1]),
     'RA': pd.Series([1], index=[1]),
     'SN': pd.Series([1], index=[1]),
     'TS': pd.Series([1], index=[1]),
     'FG': pd.Series([1], index=[1]),
     'Month': pd.Series([1], index=[1]),
     'Year': pd.Series([1], index=[1]),
     'City': pd.Series([1], index=[1]),
     'Country': pd.Series([1], index=[1]),
     'Continent': pd.Series([1], index=[1])}

dfAll = pd.DataFrame(s)
# for (root,dirs,files) in os.walk('D:\\Ky20211\\Big_Data\\BD_Climate\\data\\csv', topdown=True):
#     print(root)
#     print(dirs)
#     print(files)
#     print('--------------------------------')
dem = 0
for dirs1 in os.listdir(src):

    src1 = os.path.join(src, dirs1)
    for dirs2 in os.listdir(src1):



        src2 = os.path.join(src1, dirs2)
        for dirs3 in os.listdir(src2):
            


            src3 = os.path.join(src2, dirs3)
            for dirs4 in os.listdir(src3):
                try:
                    int(dirs4)
                except:
                    break
                src4 = os.path.join(src3, dirs4)
                for dirs5 in os.listdir(src4):
                    dem = dem + 1
                    if(dem > 250*1000):

                        df = pd.read_csv(os.path.join(src4, dirs5))

                        df['Month'] = int(dirs5[:-4])

                        df['Year'] = int(dirs4)

                        df['City'] = dirs3

                        df['Country'] = dirs2

                        df['Continent'] = dirs1

                        dfAll = dfAll.append(df, ignore_index=True)

                        # dfAll.to_csv('dataAll.csv', index=False)

                        if(dem%100==0):

                            print(dem)

                    if(dem == 300*1000):

                        dfAll.to_csv('dataAll300.csv', index=False)

                        exit()
                




# dfAll.to_csv('dataAll1000.csv', index=False)