import ee
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_aoi_areas(aoi, collection, start=2001, end=2022, tree_cover=20, mmu=0.5):
    """ Extract area for AOI, Forest and Deforestation from GFC data
    
    
    
    """
    
    if collection == 'CCI':

        lc = ee.ImageCollection("users/amitghosh/sdg_module/esa/cci_landcover")
        lc_start = lc.filter(ee.Filter.eq("system:index", f'{start}')).first()
        lc_end = lc.filter(ee.Filter.eq("system:index", f'{end}')).first()
        change = lc_start.neq(lc_end).clip(aoi)
        scale = 300

    elif collection == 'GFC':
        
        scale = 30
        hansen = ee.Image("UMD/hansen/global_forest_change_2021_v1_9")
        loss = hansen.select('lossyear').unmask(0)
        change = loss.gte(ee.Number(start).subtract(2000)).And(loss.lte(ee.Number(end).subtract(2000)))
        forest = hansen.select('treecover2000').updateMask(loss.gte(ee.Number(start).subtract(2000)).Or(loss.eq(0))).gt(tree_cover).unmask(0)
        
        
    # -----------------------------------------------------------------
    # getting total area of change
    total_image = forest.addBands(change).addBands(ee.Image(1)).multiply(ee.Image.pixelArea()).rename(['forest_area', 'change_area', 'total_area'])
    areas = total_image.reduceRegion(**{
            'reducer': ee.Reducer.sum(),
            'geometry': aoi,
            'scale': scale,
            'maxPixels': 1e14
        })
    
    
    d, areas = {}, areas.getInfo()
    for area in areas.keys():
        d[area] = np.round(areas[area]/1000000,2)
    
    span = end-start+1
    print(f"According to the GFC product, the Area of Interest covers an area of {d['total_area']} square kilometers,"
          f" of which {d['forest_area']} square kilometers have been forested in {start} ({np.round(d['forest_area']/d['total_area']*100, 2)} %)."
          f" Between {start} and {end}, {d['change_area']} square kilometers have been deforested."
          f" That corresponds to {d['change_area']/span} square kilometers of annual deforestation in average."    
    )
    
    return d


# we should invert that to do something similar as extrating from global data
def calculate_error_cochran(total_area, subarea, z_score=1.645, sample_size=250):
    """ Cochran sample size formula inverted to return error at specific sample size
    
    """
    
    proportional_change = subarea/total_area
    return np.sqrt((z_score*z_score * proportional_change * (1 - proportional_change))/sample_size)/proportional_change


def run_cochran(area_dict, max_error=10):

    d = {}
    for idx, sample_size in enumerate(range(10000, 500000, 10000)):
        change_error = calculate_error_cochran(total_area = area_dict['total_area'],
            subarea = area_dict['change_area'],
            z_score=1.645,
            sample_size=sample_size)*100

        forest_error = calculate_error_cochran(total_area = area_dict['total_area'],
            subarea = area_dict['forest_area'],
            z_score=1.645,
            sample_size=sample_size)*100

        grid_size = np.sqrt(area_dict['total_area']/sample_size)
        d[idx] = sample_size, forest_error, change_error, grid_size


    df = pd.DataFrame.from_dict(d, orient='index')

    df.columns = ['Sample Size', 'Theoretical Sampling Error (Forest)', 'Theoretical Sampling Error (Deforestation)', 'Grid Size']
    selected = df[df['Calculated Sampling Error (Deforestation)'] < max_error].head(1)
    
    return df, selected


def display_cochran(df, selected):


    
    
def get_sampling_errors(aoi, start, end, collection, proportional_change, nr_of_runs_per_grid, grid_sizes, random_seed):    
    print(proportional_change)
    # create random seeds
    np.random.seed(random_seed)
    seeds = np.random.random(nr_of_runs_per_grid)
    seeds = list(np.round(np.multiply(seeds, 100), 0))
    
    if collection == 'CCI':

        lc = ee.ImageCollection("users/amitghosh/sdg_module/esa/cci_landcover")
        lc_start = lc.filter(ee.Filter.eq("system:index", f'{start}')).first()
        lc_end = lc.filter(ee.Filter.eq("system:index", f'{end}')).first()
        change = lc_start.neq(lc_end).clip(aoi)
        scale = 300

    elif collection == 'GFC':

        hansen = ee.Image("UMD/hansen/global_forest_change_2021_v1_9").select('lossyear').unmask(0)
        change = hansen.gte(ee.Number(start).subtract(2000)).And(hansen.lte(ee.Number(end).subtract(2000)))
        scale = 30

    # -----------------------------------------------------------------
    # nested function for getting proportional change per grid size
    def get_grid_sample_error(grid):
        
        # set pixel size
        proj = ee.Projection("EPSG:3857").atScale(grid)
        
        # get total sample size
        sample_size = ee.Image(1).rename('sample_size').reproject(proj).reduceRegion(**{
            'reducer': ee.Reducer.sum(),
            'geometry': aoi,
            'scale': grid,
            'maxPixels': 1e14
        }).get('sample_size')
        
        
        # -----------------------------------------------------------------
        # nested function for getting proportional change per seed and grid
        def get_sampled_proportional_change(seed, proj):

            # create a subsample of our change image
            cells = ee.Image.random(seed).multiply(1000000).int().reproject(proj)
            random = ee.Image.random(seed).multiply(1000000).int()
            maximum = cells.addBands(random).reduceConnectedComponents(ee.Reducer.max())
            points = random.eq(maximum).selfMask().clip(aoi).reproject(proj.atScale(scale))

            # create a stack with change and total pixels as 1
            stack = (change.updateMask(points)          # masked sample change
                .addBands(points)                       # all samples
                .multiply(ee.Image.pixelArea())         # multiply both for pixel area
                .rename(['sampled_change', 'sampled_area'])
            )

            # sum them up
            areas = stack.reduceRegion(**{
                'reducer': ee.Reducer.sum(),
                'geometry': aoi,
                'scale': scale,
                'maxPixels': 1e14
            })

            # calculate proportional change to entire sampled area
            proportional_change_sampled = ee.Number(areas.get('sampled_change')).divide(ee.Number(areas.get('sampled_area'))).getInfo()
            print(proportional_change_sampled)
            error = (np.abs(proportional_change_sampled - proportional_change))/proportional_change*100
            return error
        # -----------------------------------------------------------------
        
        # get sample error mean and stddev
        sampling_iter = np.array([get_sampled_proportional_change(seed, proj) for seed in seeds])
        mean, stdDev = np.nanmean(sampling_iter), np.nanstd(sampling_iter)  
        
        # add to a dict of all grids
        #return ee.Dictionary({'stats': sampling_iter, 'size': sample_size})
        return mean, stdDev, sample_size.getInfo()
    
    d, dfs = {}, []
    # we map over all different grid sizes
    print(f" Running the sampling error simulation. Please be patient, this can take a while.")
    for idx, grid in enumerate(grid_sizes):
        print(f" Running {nr_of_runs_per_grid} times the sample error simulation at a scale of {grid} meter.")
        mean, stddev, sample_size = get_grid_sample_error(grid)
        d['idx'] = idx
        d['grid_size'] = grid
        d['sample_size'] = sample_size
        d['mean'] = mean
        d['stddev'] = stddev
        dfs.append(pd.DataFrame([d]))
    
    return pd.concat(dfs)


# we should invert that to do something similar as extrating from global data
def calculate_sample_size_cochran(total_area, subarea, z_score=1.645, target_precision=0.2):
    
    proportional_change = subarea/total_area
    error = target_precision * proportional_change
    return ((z_score*z_score * proportional_change * (1 - proportional_change))/(error*error))


# we should invert that to do something similar as extrating from global data
def calculate_error_cochran(total_area, subarea, z_score=1.645, sample_size=0.2):
    
    proportional_change = subarea/total_area
    error = target_precision * proportional_change
    return ((z_score*z_score * proportional_change * (1 - proportional_change))/(error*error))