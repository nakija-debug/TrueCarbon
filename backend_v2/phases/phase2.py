import ee
import geemap

# 1. Initialize (This stays at the top)
try:
    ee.Initialize(project='student-research-carbon')
except:
    ee.Authenticate()
    ee.Initialize(project='student-research-carbon')

# 2. DEFINE THE FUNCTION
# Everything else must go INSIDE this function so the UI can call it.
def run_analysis():
    print("Starting analysis...") # This prints to terminal for debugging
    
    # --- A. DEFINE REGION & DATA ---
    roi = ee.Geometry.Point([77.3178, 28.4089]).buffer(1000)
    
    # Get 2023 Data
    dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
        .filterBounds(roi) \
        .filterDate('2023-01-01', '2023-12-30') \
        .select('label') \
        .mode() \
        .clip(roi)

    # --- B. PERFORM CALCULATIONS ---
    # Count pixels that are Trees (Class 1)
    trees = dw.eq(1)
    
    # Calculate Area
    pixel_area = trees.multiply(ee.Image.pixelArea())
    stats = pixel_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=roi,
        scale=10,
        maxPixels=1e9
    )
    
    # Get the numbers
    area_sqm = stats.get('label').getInfo()
    area_hectares = area_sqm / 10000
    carbon_tonnes = area_hectares * 120  # Assumption: 120t/ha
    
    # --- C. PREPARE THE MAP ---
    # We create the map object here, but we don't ".to_html()" it.
    # The UI will handle displaying it.
    m = geemap.Map()
    m.centerObject(roi, 13)
    
    vis_params = {
        'min': 0, 'max': 8,
        'palette': ['419bdf', '397d49', '88b053', '7a87c6', 'e49635', 
                    'dfc35a', 'c4281b', 'a59b8f', 'b39fe1']
    }
    m.addLayer(dw, vis_params, 'LULC 2023')

    # --- D. RETURN RESULTS TO THE UI ---
    # Instead of printing, we package everything into a dictionary
    return {
        "map_object": m,
        "new_tree_area_ha": area_hectares, 
        "carbon_tonnes": carbon_tonnes,
        "chart_data": {
            "Trees": area_hectares, 
            "Crops": 45.0,  # Placeholder for now
            "Built Area": 20.0  # Placeholder for now
        }
    }
