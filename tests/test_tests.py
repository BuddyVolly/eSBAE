from shapely.geometry import Polygon
from e_sbae.sampling import random_point


seed = np.random.seed(42)
def test_tests() -> None:
    """test that the tests are running, to be replaced by actual tests"""

    assert True
    
    
def test_random_point(geometry):
    
    retrieved_random_point = random_point(geometry)
    assert retrieved_random_point == Point(12.5, 30)
                            