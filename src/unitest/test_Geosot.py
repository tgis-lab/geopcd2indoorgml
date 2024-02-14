'''
Created on 2023年6月27日

@author: Zhiyong Wang
'''

from src.geosot3d.LngLatSegments import LngLatSegments
import unittest
from src.geosot3d.Height import Height
from src.geosot3d.Morton3D import Morton3D

class TestLngLatSegments(unittest.TestCase):
    # mutiple test inputs, refer to https://stackoverflow.com/questions/32899/how-do-you-generate-dynamic-parameterized-unit-tests-in-python
    
    def test_dms(self):
        param_list = []
        param_list.append(("39° 54' 37.0098\" N", 0, 39, 54, 37, 20, 37.0098))
        param_list.append(("116° 18' 54.8198\" E", 0, 116, 18, 54, 1679, 54.8198))
        param_list.append(("39° 54' 37.0098\" S", 1, 39, 54, 37, 20, 37.0098))
        param_list.append(("116° 18' 54.8198\" W", 1, 116, 18, 54, 1679, 54.8198))
        
        for params in param_list:
            _segmetns = LngLatSegments(params[0])
            self.assertEqual(params[1], _segmetns.G);
            self.assertEqual(params[2], _segmetns.D);
            self.assertEqual(params[3], _segmetns.M);
            self.assertEqual(params[4], _segmetns.S);
            self.assertEqual(params[5], _segmetns.S11);
            #self.assertEqual(params[6], _segmetns.Seconds);
 
 
    def test_degree(self):
        param_list = []
        param_list.append((-12.345678, 1, 12, 20, 44, 903, 44.4409))
        param_list.append((12.345678, 0, 12, 20, 44, 903, 44.4409))
        
        for params in param_list:
            _segmetns = LngLatSegments(params[0])
            self.assertEqual(params[1], _segmetns.G);
            self.assertEqual(params[2], _segmetns.D);
            self.assertEqual(params[3], _segmetns.M);
            self.assertEqual(params[4], _segmetns.S);
            self.assertEqual(params[5], _segmetns.S11);
            #self.assertEqual(params[6], _segmetns.Seconds);
            
            
    def test_height(self):
        height = Height(25)
        self.assertEqual(height.calc_geosot_n(height.H2, height.theta8s), 40330.499999790045)
        self.assertAlmostEqual(height.calc_geosot_Hn(255), height.H255, 9)
        self.assertAlmostEqual(height.calc_geosot_Hn(-256), height.HN256, 9)
        self.assertEqual(height.calc_geosot_hn(255), 9178.33696700411)
        self.assertEqual(height.calc_geosot_hn(-256), 1.3269786717965377)
        self.assertEqual(height.calc_geosot_Ln(255), 9178.336967004097)
        self.assertEqual(height.calc_geosot_Ln(-256), 1.3269786717965357)
        # H2 = 23694.168548
        # H3 = -5025.376350
        self.assertAlmostEqual(height.calc_geosot_hn(height.calc_geosot_n(height.H2, height.theta8s), height.theta8s), 1.156318, 5)
        self.assertAlmostEqual(height.calc_geosot_hn(height.calc_geosot_n(height.H3, height.theta8s), height.theta8s), 0.052015, 6)
        
    def test_morton(self):
        param_list = []
        param_list.append((1, 11, 139))
        param_list.append((13, 42, 2265))
        m = Morton3D(dimensions=2, bits=32)
        for params in param_list:
            code = m.pack(params[0], params[1])
            values = m.unpack(code)  
            self.assertEqual(code, params[2])
            self.assertEqual(values[0], params[0])
            self.assertEqual(values[1], params[1])
            
        


if __name__ == '__main__':
    unittest.main()