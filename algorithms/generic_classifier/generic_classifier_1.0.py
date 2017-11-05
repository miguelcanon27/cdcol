#Parámetros: normalized, minValid, bands, modelos
import xarray as xr
import numpy as np
print "Excecuting generic_classifier v1"
#Calcular el compuesto de medianas para cada uno de las entradas
nbar = xarr0
nodata=-9999
medians1={}
cloud_mask=np.where(np.logical_and(nbar["cf_mask"].values!=2, nbar["cf_mask"].values<4), True, False)
for band in bands:
    datos=np.where(np.logical_and(nbar.data_vars[band]!=nodata,cloud_mask),nbar.data_vars[band], np.nan)
    allNan=~np.isnan(datos)
    if normalized:
        m=np.nanmean(datos.reshape((datos.shape[0],-1)), axis=1)
        st=np.nanstd(datos.reshape((datos.shape[0],-1)), axis=1)
        datos=np.true_divide((datos-m[:,np.newaxis,np.newaxis]), st[:,np.newaxis,np.newaxis])*np.nanmean(st)+np.nanmean(m)
    medians1[band]=np.nanmedian(datos,0)
    medians1[band][np.sum(allNan,0)<minValid]=np.nan
del datos


# In[7]:

from sklearn.externals import joblib


# In[21]:

#Preprocesar: 
nmed=None
nan_mask=None
for band in medians1:
    b=medians1[band].ravel()
    if nan_mask is None: 
        nan_mask=np.isnan(b)
    else:
        nan_mask=np.logical_or(nan_mask, np.isnan(medians1[band].ravel()))
    b[np.isnan(b)]=np.nanmedian(b)
    if nmed is None:
        sp=medians1[band].shape
        nmed=b
    else:
        nmed=np.vstack((nmed,b))


# In[12]:

import os
model=None
for file in os.listdir(modelos):
    print file
    if file.endswith(".pkl"):
        model=file
        break
print model
if model is None:
    raise "Debería haber un modelo en la carpeta "+modelos
    
classifier=joblib.load(os.path.join(modelos, model))
