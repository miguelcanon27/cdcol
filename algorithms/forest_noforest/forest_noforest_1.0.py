import xarray as xr
import numpy as np
print "Excecuting forest_noforest v1 "
nbar = xarr0
nodata=-9999
medians={}
bands=["red","nir"]
cloud_mask=np.where(np.logical_and(nbar["cf_mask"].values!=2, nbar["cf_mask"].values<4), True, False)
for band in bands:
    datos=np.where(np.logical_and(nbar.data_vars[band]!=nodata,cloud_mask),nbar.data_vars[band], np.nan)
    allNan=~np.isnan(datos)
    if normalized:
        m=np.nanmean(datos.reshape((datos.shape[0],-1)), axis=1)
        st=np.nanstd(datos.reshape((datos.shape[0],-1)), axis=1)
        datos=np.true_divide((datos-m[:,np.newaxis,np.newaxis]), st[:,np.newaxis,np.newaxis])*np.nanmean(st)+np.nanmean(m)
    medians[band]=np.nanmedian(datos,0)
    medians[band][np.sum(allNan,0)<minValid]=np.nan
del datos
period_red = medians["red"]
period_nir = medians["nir"]
del medians
mask_nan=np.logical_or(np.isnan(period_red), np.isnan(period_nir))
period_nvdi = np.true_divide( np.subtract(period_nir,period_red) , np.add(period_nir,period_red) )
period_nvdi[mask_nan]=np.nan
height = period_nvdi.shape[0]
width = period_nvdi.shape[1]
bosque_nobosque=np.full(period_nvdi.shape, -1)
for y1 in xrange(0, height, slice_size):
    for x1 in xrange(0, width, slice_size):
        x2 = x1 + slice_size
        y2 = y1 + slice_size
        if(x2 > width):
            x2 = width
        if(y2 > height):
            y2 = height
        submatrix = period_nvdi[y1:y2,x1:x2]
        ok_pixels = np.count_nonzero(~np.isnan(submatrix))
        if ok_pixels==0:
            bosque_nobosque[y1:y2,x1:x2] = nodata    
        elif float(np.nansum(submatrix>ndvi_threshold))/float(ok_pixels) >= vegetation_rate :
            bosque_nobosque[y1:y2,x1:x2] = 1
        else:
            bosque_nobosque[y1:y2,x1:x2] = 0


ncoords=[]
xdims =[]
xcords={}
for x in nbar.coords:
    if(x!='time'):
        ncoords.append( ( x, nbar.coords[x]) )
        xdims.append(x)
        xcords[x]=nbar.coords[x]
variables ={"bosque_nobosque": xr.DataArray(bosque_nobosque, dims=xdims,coords=ncoords)}
output=xr.Dataset(variables, attrs={'crs':nbar.crs})
for x in output.coords:
    output.coords[x].attrs["units"]=nbar.coords[x].units
print output